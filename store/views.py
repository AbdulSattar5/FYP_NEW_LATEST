from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count, Avg, Sum
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.templatetags.static import static
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.contrib.auth.models import User
from store.models import (
    Category, Product, UserInteraction, Recommendation,
    Order, Feedback, UserProfile
)
from store.forms import (
    UserSignupForm, UserLoginForm, UserProfileUpdateForm,
    ProductSearchForm, OrderForm, FeedbackForm, ProductForm
)
from store.recommendation_engine import (
    RecommendationEngine,
    get_recommendations,
    recommend_with_scores,
)
import logging
import json
import uuid

logger = logging.getLogger(__name__)
ALLOWED_TRACK_INTERACTIONS = {'view', 'click', 'cart', 'purchase', 'search'}
ORDER_SUBMISSION_TOKEN_PREFIX = 'order_submission_token'


def _recommendable_products_q():
    """Products that can be shown in recommendation/trending slots."""
    return Q(is_available=True) & (Q(manages_local_stock=False) | Q(stock_level__gt=0))


def _parse_json_body(request):
    """Parse request JSON body and return dict or None if invalid."""
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _ensure_session_key(request):
    """Ensure session has a key and return it."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _product_image_url(product):
    """Return product image URL with safe fallback."""
    try:
        if product.image:
            return product.image.url
        if isinstance(product.attributes, dict):
            external_image = (product.attributes.get('external_image_url') or product.attributes.get('image_url') or '').strip()
            if external_image:
                return external_image
    except ValueError:
        pass
    return static('images/default-product.svg')


def _parse_decimal_query_value(raw_value):
    """Safely parse decimal query params used in filters."""
    if raw_value in (None, ''):
        return None
    try:
        return Decimal(str(raw_value).strip())
    except (InvalidOperation, ValueError, TypeError):
        return None


def _serialize_product_for_api(product):
    """Common product serializer for JSON APIs."""
    is_affiliate = bool(getattr(product, 'is_affiliate_product', False))
    buy_url = getattr(product, 'buy_on_source_url', '') if is_affiliate else ''
    return {
        'id': product.product_id,
        'title': product.name,
        'slug': product.slug,
        'price': float(product.discount_price),
        'image': _product_image_url(product),
        'category': product.category.name if product.category else '',
        'rating': float(product.rating),
        'stock': product.stock_level,
        'is_affiliate': is_affiliate,
        'can_add_to_cart': bool(getattr(product, 'can_add_to_cart', False)),
        'external_url': buy_url,
        'action_label': 'Buy on Source' if is_affiliate else 'View Details',
        'description': product.description or '',
    }


def _order_submission_session_key(product_id):
    """Build per-product order submission token key."""
    return f'{ORDER_SUBMISSION_TOKEN_PREFIX}_{product_id}'


def _issue_order_submission_token(request, product_id):
    """Create and persist a fresh submission token for checkout idempotency."""
    token = uuid.uuid4().hex
    request.session[_order_submission_session_key(product_id)] = token
    request.session.modified = True
    return token


def _dedupe_products(products, limit=None, exclude_ids=None):
    """Return unique in-stock active products while preserving order."""
    seen = set(exclude_ids or set())
    unique_products = []
    for product in products or []:
        if not product:
            continue
        if not product.is_available:
            continue
        if product.manages_local_stock and product.stock_level <= 0:
            continue
        if product.product_id in seen:
            continue
        seen.add(product.product_id)
        unique_products.append(product)
        if limit and len(unique_products) >= limit:
            break
    return unique_products


def _get_actor_recommendation_kwargs(request):
    """Return kwargs for recommendation calls based on user/session identity."""
    if request.user.is_authenticated:
        return {'user': request.user}
    return {'session_key': _ensure_session_key(request)}


def _get_trending_products(limit=8, exclude_ids=None):
    """Simple trending fallback from active in-stock catalog."""
    products = Product.objects.filter(
        _recommendable_products_q(),
    ).select_related('category').order_by('-rating', '-stock_level', '-created_at')
    return _dedupe_products(products, limit=limit, exclude_ids=exclude_ids)


def _get_recently_viewed_products(request, limit=8, exclude_ids=None):
    """Return recently viewed products for logged-in users or anonymous sessions."""
    filters = {
        'interaction_type': 'view',
        'product__isnull': False,
    }
    if request.user.is_authenticated:
        filters['user'] = request.user
    else:
        filters['session_key'] = _ensure_session_key(request)

    viewed_ids = list(
        UserInteraction.objects.filter(**filters)
        .order_by('-timestamp')
        .values_list('product_id', flat=True)
    )
    if not viewed_ids:
        return []

    products = Product.objects.filter(
        product_id__in=viewed_ids,
    ).filter(
        _recommendable_products_q(),
    ).select_related('category')
    product_map = {product.product_id: product for product in products}
    ordered = [product_map[pid] for pid in viewed_ids if pid in product_map]
    return _dedupe_products(ordered, limit=limit, exclude_ids=exclude_ids)


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTION - INTERACTION TRACKING
# ═══════════════════════════════════════════════════════════

def log_interaction(user, product_id, interaction_type, count_increment=1, session_key=None, query='', metadata=None):
    """
    Automatically track user behavior for ML engine
    Called from views to log: 'view', 'cart', 'purchase', 'like', 'search'
    """
    actor_user = user if user and user.is_authenticated else None
    actor_session = session_key.strip() if isinstance(session_key, str) and session_key.strip() else None

    if actor_user is None and actor_session is None:
        return

    try:
        product = Product.objects.get(product_id=product_id, is_available=True) if product_id else None
        UserInteraction.objects.create(
            user=actor_user,
            session_key=actor_session,
            product=product,
            interaction_type=interaction_type,
            interaction_count=max(1, int(count_increment or 1)),
            query=(query or '').strip(),
            metadata=metadata or {},
        )
        actor_label = actor_user.username if actor_user else f'session:{actor_session}'
        product_label = product.name if product else 'n/a'
        logger.info(f"Logged {interaction_type} for {actor_label} on product {product_label}")
    except Product.DoesNotExist:
        logger.warning(f"Product {product_id} not found for interaction logging")
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")


# ═══════════════════════════════════════════════════════════
# 1. HOME VIEW
# ═══════════════════════════════════════════════════════════

def home_view(request):
    """Home page with featured products, trending, discounts, and AI recommendations"""
    
    recommendable = Product.objects.filter(_recommendable_products_q()).select_related('category')

    # Get trending products (by rating)
    trending_products = recommendable.order_by('-rating')[:8]

    # Featured slot: use flagged products, or fall back to top-rated so home is never empty
    featured_products = list(
        recommendable.filter(is_featured=True).order_by('-rating')[:8]
    )
    if not featured_products:
        featured_products = list(trending_products[:8])
    
    # Get discounted products
    discounted_products = Product.objects.filter(
        is_on_discount=True,
    ).filter(
        _recommendable_products_q()
    ).order_by('-discount_percentage')[:6].select_related('category')
    
    # Get all categories with product count
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_available=True))
    )[:8]
    catalog_count = Product.objects.filter(is_available=True).count()
    category_count = Category.objects.count()
    
    actor_kwargs = _get_actor_recommendation_kwargs(request)
    has_personal_history = False
    if request.user.is_authenticated:
        has_personal_history = UserInteraction.objects.filter(user=request.user).exists()
    else:
        has_personal_history = UserInteraction.objects.filter(
            session_key=actor_kwargs.get('session_key')
        ).exists()

    recommended_products = _dedupe_products(
        get_recommendations(limit=6, **actor_kwargs),
        limit=6,
    )
    if not recommended_products:
        recommended_products = _get_trending_products(limit=6)

    recommended_ids = [product.product_id for product in recommended_products]
    recently_viewed_products = _get_recently_viewed_products(
        request,
        limit=6,
        exclude_ids=set(recommended_ids),
    )
    
    context = {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'discounted_products': discounted_products,
        'categories': categories,
        'recommended_products': recommended_products,
        'recommended_ids': recommended_ids,
        'recently_viewed_products': recently_viewed_products,
        'has_personal_history': has_personal_history,
        'catalog_count': catalog_count,
        'category_count': category_count,
    }
    
    return render(request, 'home.html', context)


# ═══════════════════════════════════════════════════════════
# 2. SIGNUP VIEW
# ═══════════════════════════════════════════════════════════

def signup_view(request):
    """User registration view"""
    
    # If already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user
            user = form.save()
            
            # Create UserProfile with additional fields
            profile = user.profile  # Auto-created by signal
            profile.phone_number = form.cleaned_data.get('phone_number', '')
            profile.subscription_type = form.cleaned_data.get('subscription_type', 'free')
            
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()
            
            # Auto-login after signup
            login(request, user)
            messages.success(request, f'Welcome to AI Shop, {user.first_name}! 🎉')
            return redirect('store:home')
    else:
        form = UserSignupForm()
    
    return render(request, 'auth/signup.html', {'form': form})


# ═══════════════════════════════════════════════════════════
# 3. LOGIN VIEW
# ═══════════════════════════════════════════════════════════

def login_view(request):
    """User login view"""
    
    # If already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Handle remember me
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Redirect to 'next' parameter or home
                next_url = request.GET.get('next', 'store:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


# ═══════════════════════════════════════════════════════════
# 4. LOGOUT VIEW
# ═══════════════════════════════════════════════════════════

@require_POST
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('store:home')


# ═══════════════════════════════════════════════════════════
# 5. PROFILE VIEW
# ═══════════════════════════════════════════════════════════

@login_required
def profile_view(request):
    """User profile view with order history and stats"""
    
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            # Update User model fields
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            
            # Update UserProfile
            form.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('store:profile')
    else:
        # Pre-fill form with user data
        form = UserProfileUpdateForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    
    # Get recent orders
    recent_orders = Order.objects.filter(user=request.user).order_by('-ordered_at')[:5]
    
    # Calculate stats
    total_orders = Order.objects.filter(user=request.user).count()
    total_spent = Order.objects.filter(user=request.user).aggregate(
        total=Sum('total_price')
    )['total'] or 0
    feedbacks_count = Feedback.objects.filter(user=request.user).count()
    
    context = {
        'form': form,
        'profile': profile,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'feedbacks_count': feedbacks_count,
    }
    
    return render(request, 'auth/profile.html', context)


# ═══════════════════════════════════════════════════════════
# 6. PRODUCT LIST VIEW
# ═══════════════════════════════════════════════════════════

def product_list_view(request):
    """Product listing with search, filter, and sort"""
    
    # Get all available products
    products = Product.objects.filter(is_available=True).select_related('category')
    
    # Search
    search_query = request.GET.get('q', '')
    actor_kwargs = _get_actor_recommendation_kwargs(request)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        log_interaction(
            request.user,
            None,
            'search',
            session_key=None if request.user.is_authenticated else actor_kwargs.get('session_key'),
            query=search_query,
            metadata={'source': 'product_list'},
        )
    
    # Category filter
    category_slug = request.GET.get('category', '')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
    
    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_price_value = _parse_decimal_query_value(min_price)
    max_price_value = _parse_decimal_query_value(max_price)
    price_filter_error = False

    if min_price and min_price_value is None:
        price_filter_error = True
    if max_price and max_price_value is None:
        price_filter_error = True

    if min_price_value is not None:
        products = products.filter(price__gte=min_price_value)
    if max_price_value is not None:
        products = products.filter(price__lte=max_price_value)
    
    # Sort
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by in ('price_asc', 'price_low'):
        sort_by = 'price_asc'
        products = products.order_by('price')
    elif sort_by in ('price_desc', 'price_high'):
        sort_by = 'price_desc'
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'discount':
        products = products.filter(is_on_discount=True).order_by('-discount_percentage')
    
    # Get total count before pagination
    total_count = products.count()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Get all categories for sidebar
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_available=True))
    )
    
    # Get recommended product IDs for badge display
    recommended_products = _dedupe_products(
        get_recommendations(limit=12, **actor_kwargs),
        limit=12,
    )
    recommended_ids = [p.product_id for p in recommended_products]
    
    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'all_categories': categories,
        'total_count': total_count,
        'current_category': current_category,
        'search_query': search_query,
        'sort_by': sort_by,
        'recommended_ids': recommended_ids,
        'min_price': min_price,
        'max_price': max_price,
        'price_filter_error': price_filter_error,
    }
    
    return render(request, 'products/product_list.html', context)


# ═══════════════════════════════════════════════════════════
# 7. PRODUCT DETAIL VIEW
# ═══════════════════════════════════════════════════════════

def product_detail_view(request, pk):
    """Product detail page with interaction tracking and recommendations"""
    
    product = get_object_or_404(
        Product.objects.select_related('category'),
        product_id=pk,
        is_available=True
    )
    
    actor_kwargs = _get_actor_recommendation_kwargs(request)
    log_interaction(
        request.user,
        pk,
        'view',
        session_key=None if request.user.is_authenticated else actor_kwargs.get('session_key'),
    )
    
    # Similar products from same category
    similar_base_qs = Product.objects.filter(
        _recommendable_products_q()
    ).exclude(product_id=pk).select_related('category')
    if product.category_id:
        similar_products = _dedupe_products(
            similar_base_qs.filter(category=product.category).order_by('-rating'),
            limit=6,
            exclude_ids={product.product_id},
        )
    else:
        similar_products = _dedupe_products(
            similar_base_qs.order_by('-rating'),
            limit=6,
            exclude_ids={product.product_id},
        )

    recommended_products = _dedupe_products(
        get_recommendations(limit=4, **actor_kwargs),
        limit=4,
        exclude_ids={product.product_id},
    )
    if not recommended_products:
        recommended_products = _get_trending_products(limit=4, exclude_ids={product.product_id})
    recommended_ids = [p.product_id for p in recommended_products]

    trending_products = _get_trending_products(limit=6, exclude_ids={product.product_id})
    recently_viewed_products = _get_recently_viewed_products(
        request,
        limit=6,
        exclude_ids={product.product_id},
    )
    
    # Get product feedbacks
    feedbacks = Feedback.objects.filter(
        product=product
    ).select_related('user')[:10]
    
    # Check if user already purchased or rated this product
    has_feedback = False
    has_purchased = False
    has_rated = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(
            user=request.user,
            product=product
        ).exclude(status='cancelled').exists()
        has_rated = Feedback.objects.filter(
            user=request.user,
            product=product
        ).exists()
        has_feedback = Feedback.objects.filter(
            user=request.user,
            product=product
        ).exists()
    
    # Calculate average rating
    avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'recommended_products': recommended_products,
        'recommended_ids': recommended_ids,
        'trending_products': trending_products,
        'recently_viewed_products': recently_viewed_products,
        'feedbacks': feedbacks,
        'has_feedback': has_feedback,
        'has_purchased': has_purchased,
        'has_rated': has_rated,
        'avg_rating': round(avg_rating, 1),
    }
    
    return render(request, 'products/product_detail.html', context)


# ═══════════════════════════════════════════════════════════
# 8. CATEGORY PRODUCTS VIEW
# ═══════════════════════════════════════════════════════════

def category_products_view(request, slug):
    """Category-specific product listing"""
    
    category = get_object_or_404(Category, slug=slug)
    
    # Filter products by category
    products = Product.objects.filter(
        category=category,
        is_available=True
    ).select_related('category')
    
    # Apply price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_price_value = _parse_decimal_query_value(min_price)
    max_price_value = _parse_decimal_query_value(max_price)
    price_filter_error = False

    if min_price and min_price_value is None:
        price_filter_error = True
    if max_price and max_price_value is None:
        price_filter_error = True

    if min_price_value is not None:
        products = products.filter(price__gte=min_price_value)
    if max_price_value is not None:
        products = products.filter(price__lte=max_price_value)
    
    # Sort
    sort_by = request.GET.get('sort_by', 'newest')
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by in ('price_asc', 'price_low'):
        sort_by = 'price_asc'
        products = products.order_by('price')
    elif sort_by in ('price_desc', 'price_high'):
        sort_by = 'price_desc'
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    elif sort_by == 'discount':
        products = products.filter(is_on_discount=True).order_by('-discount_percentage')
    
    # Get total count
    total_count = products.count()
    
    # Pagination
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Get all categories for sidebar
    all_categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_available=True))
    )
    
    # Get user recommendations for badge
    actor_kwargs = _get_actor_recommendation_kwargs(request)
    user_recommendations = _dedupe_products(
        get_recommendations(limit=12, **actor_kwargs),
        limit=12,
    )
    recommended_ids = [p.product_id for p in user_recommendations]
    
    context = {
        'category': category,
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'all_categories': all_categories,
        'recommended_products': user_recommendations,
        'recommended_ids': recommended_ids,
        'total_count': total_count,
        'current_sort': sort_by,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'price_filter_error': price_filter_error,
    }
    
    return render(request, 'products/category_products.html', context)


# ═══════════════════════════════════════════════════════════
# 9. API: SEARCH SUGGESTIONS
# ═══════════════════════════════════════════════════════════

@require_GET
def search_suggestions_api_view(request):
    """Search suggestions API for navbar autocomplete."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'success': True, 'suggestions': []})

    suggestions_qs = Product.objects.filter(
        is_available=True
    ).filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).select_related('category')[:10]

    suggestions = [
        {
            'id': product.product_id,
            'title': product.name,
            'slug': product.slug,
            'price': float(product.discount_price),
            'image': _product_image_url(product),
            'category': product.category.name if product.category else '',
        }
        for product in suggestions_qs
    ]

    return JsonResponse({'success': True, 'suggestions': suggestions})


# ═══════════════════════════════════════════════════════════
# 10. API: TRACK INTERACTION
# ═══════════════════════════════════════════════════════════

@require_POST
def track_interaction_api_view(request):
    """Track user/anonymous interaction with product."""
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON body',
        }, status=400)

    product_id = payload.get('product_id')
    interaction_type = str(payload.get('interaction_type', '')).strip().lower()
    query = str(payload.get('query', '')).strip()
    raw_metadata = payload.get('metadata', {})
    metadata = raw_metadata if isinstance(raw_metadata, dict) else {}

    if interaction_type not in ALLOWED_TRACK_INTERACTIONS:
        return JsonResponse({
            'success': False,
            'error': f'Invalid interaction_type. Allowed: {sorted(ALLOWED_TRACK_INTERACTIONS)}',
        }, status=400)

    product = None
    if product_id:
        product = Product.objects.filter(
            product_id=product_id,
            is_available=True,
        ).first()
        if not product:
            return JsonResponse({
                'success': False,
                'error': 'Product not found',
            }, status=404)
    elif interaction_type != 'search':
        return JsonResponse({
            'success': False,
            'error': 'product_id is required',
        }, status=400)

    if interaction_type == 'search' and not query and not product:
        return JsonResponse({
            'success': False,
            'error': 'query is required for search events without product_id',
        }, status=400)

    # Purchase interactions are logged in order flow; avoid duplicate records.
    if interaction_type == 'purchase':
        return JsonResponse({
            'success': True,
            'message': 'Purchase logging is handled by order placement',
        })

    session_key = _ensure_session_key(request)
    actor_user = request.user if request.user.is_authenticated else None

    log_interaction(
        user=actor_user,
        product_id=product.product_id if product else None,
        interaction_type=interaction_type,
        count_increment=1,
        session_key=None if actor_user else session_key,
        query=query,
        metadata=metadata,
    )

    if not actor_user:
        anonymous_log = request.session.get('anonymous_interactions', {})
        product_key = product.product_id if product else 'search'
        event_key = f'{product_key}:{interaction_type}:{query}'
        event = anonymous_log.get(event_key, {
            'session_key': session_key,
            'product_id': product.product_id if product else None,
            'interaction_type': interaction_type,
            'query': query,
            'count': 0,
        })
        event['count'] += 1
        anonymous_log[event_key] = event
        request.session['anonymous_interactions'] = anonymous_log
        request.session.modified = True

    return JsonResponse({
        'success': True,
        'message': 'Interaction tracked',
    })


# ═══════════════════════════════════════════════════════════
# 11. API: CART UPDATE
# ═══════════════════════════════════════════════════════════

@require_POST
def update_cart_api_view(request, product_id):
    """Update cart item quantity (or remove on quantity=0)."""
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON body',
        }, status=400)

    quantity = payload.get('quantity')
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return JsonResponse({
            'success': False,
            'error': 'Quantity must be an integer',
        }, status=400)

    if quantity < 0:
        return JsonResponse({
            'success': False,
            'error': 'Quantity cannot be negative',
        }, status=400)

    product = Product.objects.filter(
        product_id=product_id,
        is_available=True,
    ).first()
    if not product:
        return JsonResponse({
            'success': False,
            'error': 'Product not found',
        }, status=404)
    if not product.can_add_to_cart:
        return JsonResponse({
            'success': False,
            'error': 'This product is available on source only and cannot be added to cart.',
        }, status=400)

    cart = request.session.get('cart', {})
    product_key = str(product_id)

    if quantity == 0:
        cart.pop(product_key, None)
    else:
        if product.stock_level <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Product out of stock',
            }, status=400)

        if quantity > product.stock_level:
            return JsonResponse({
                'success': False,
                'error': f'Only {product.stock_level} items available',
            }, status=400)

        cart[product_key] = {
            'name': product.name,
            'price': float(product.discount_price),
            'image': _product_image_url(product),
            'quantity': quantity,
            'product_id': product.product_id,
        }

    request.session['cart'] = cart
    request.session.modified = True

    subtotal = 0.0
    cart_count = 0
    for item_product_id, item in cart.items():
        item_quantity = int(item.get('quantity', 0))
        if item_quantity <= 0:
            continue
        try:
            item_product_id_int = int(item_product_id)
        except (TypeError, ValueError):
            continue
        live_product = Product.objects.filter(
            product_id=item_product_id_int,
            is_available=True,
        ).first()
        if not live_product:
            continue
        cart_count += item_quantity
        subtotal += float(live_product.discount_price) * item_quantity

    total = subtotal

    return JsonResponse({
        'success': True,
        'status': 'success',
        'message': 'Cart updated',
        'cart_count': cart_count,
        'subtotal': round(subtotal, 2),
        'total': round(total, 2),
    })


# ═══════════════════════════════════════════════════════════
# 12. API: RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════

@require_GET
def recommendations_api_view(request):
    """Get personalized recommendations with fallback to popular products."""
    actor_kwargs = _get_actor_recommendation_kwargs(request)
    recommended_products = _dedupe_products(
        get_recommendations(limit=12, **actor_kwargs),
        limit=12,
    )
    response_source = 'personalized'

    if not recommended_products:
        recommended_products = _get_trending_products(limit=12)
        response_source = 'fallback'

    recommendations = [_serialize_product_for_api(product) for product in recommended_products]
    return JsonResponse({
        'success': True,
        'source': response_source,
        'recommendations': recommendations,
    })


# ═══════════════════════════════════════════════════════════
# 13. API: PRODUCT QUICK VIEW
# ═══════════════════════════════════════════════════════════

@require_GET
def product_quick_view_api_view(request, product_id):
    """Quick product details API for modals/cards."""
    product = Product.objects.filter(
        product_id=product_id,
        is_available=True,
    ).select_related('category').first()

    if not product:
        return JsonResponse({
            'success': False,
            'error': 'Product not found',
        }, status=404)

    return JsonResponse({
        'success': True,
        'product': _serialize_product_for_api(product),
    })


# ═══════════════════════════════════════════════════════════
# 14. RECOMMENDATIONS VIEW
# ═══════════════════════════════════════════════════════════

@login_required
def recommendations_view(request):
    """Full page showing all AI recommendations for the user"""

    recommended_products = _dedupe_products(
        get_recommendations(user=request.user, limit=96),
        limit=96,
    )

    # Score metadata for UI badges/reasons.
    scored = recommend_with_scores(user=request.user, limit=96)
    score_map = {item['product_id']: item for item in scored}

    recommendation_rows = []
    for product in recommended_products:
        score_item = score_map.get(product.product_id, {})
        score_value = float(score_item.get('score', 0.0))
        recommendation_rows.append({
            'product': product,
            'score': score_value,
            'score_percentage': int(round(score_value * 100)),
            'reason': score_item.get('reason', 'Popular with shoppers'),
        })
    
    # User stats for display
    interaction_count = UserInteraction.objects.filter(user=request.user).count()
    products_viewed = UserInteraction.objects.filter(
        user=request.user, 
        interaction_type='view'
    ).count()
    products_purchased = UserInteraction.objects.filter(
        user=request.user, 
        interaction_type='purchase'
    ).count()
    items_carted = UserInteraction.objects.filter(
        user=request.user, 
        interaction_type='cart'
    ).count()
    
    # Pagination
    paginator = Paginator(recommendation_rows, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    trending_products = _get_trending_products(limit=6)
    recently_viewed_products = _get_recently_viewed_products(request, limit=6)
    
    context = {
        'recommendations': page_obj.object_list,
        'recommended_products': page_obj.object_list,
        'recommended_ids': [row['product'].product_id for row in recommendation_rows],
        'page_obj': page_obj,
        'interaction_count': interaction_count,
        'products_viewed': products_viewed,
        'products_purchased': products_purchased,
        'items_carted': items_carted,
        'trending_products': trending_products,
        'recently_viewed_products': recently_viewed_products,
        'total_recs': len(recommendation_rows),
    }
    
    return render(request, 'products/recommendations.html', context)


# ═══════════════════════════════════════════════════════════
# 10. REFRESH RECOMMENDATIONS VIEW (AJAX)
# ═══════════════════════════════════════════════════════════

@login_required
@require_POST
def refresh_recommendations_view(request):
    """AJAX endpoint to refresh recommendations"""
    try:
        engine = RecommendationEngine()
        recs = engine.generate_recommendations_for_user(request.user.id)
        
        return JsonResponse({
            'status': 'success',
            'success': True,
            'count': len(recs),
            'message': f'Generated {len(recs)} fresh recommendations!'
        })
    except Exception as e:
        logger.error(f"Error refreshing recommendations: {e}")
        return JsonResponse({
            'status': 'error',
            'success': False,
            'message': 'Failed to refresh recommendations'
        }, status=500)


# ═══════════════════════════════════════════════════════════
# 11. ADD TO CART VIEW (AJAX)
# ═══════════════════════════════════════════════════════════

@login_required
@require_POST
def add_to_cart_view(request, product_id):
    """Add product to cart (AJAX) and log interaction"""
    try:
        product = get_object_or_404(Product, product_id=product_id, is_available=True)

        payload = _parse_json_body(request)
        if payload is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request payload',
            }, status=400)

        requested_quantity = payload.get('quantity', 1)
        try:
            requested_quantity = int(requested_quantity)
        except (TypeError, ValueError):
            requested_quantity = 1
        if requested_quantity < 1:
            return JsonResponse({
                'status': 'error',
                'message': 'Quantity must be at least 1',
            }, status=400)

        if not product.can_add_to_cart:
            return JsonResponse({
                'status': 'error',
                'message': 'This product is available on source only and cannot be added to cart.',
            }, status=400)

        # Check stock
        if product.stock_level <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Product out of stock'
            }, status=400)
        
        # Get or create cart in session
        cart = request.session.get('cart', {})
        
        # Add to cart
        product_key = str(product_id)
        if product_key in cart:
            new_quantity = int(cart[product_key].get('quantity', 1)) + requested_quantity
            if new_quantity > product.stock_level:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Only {product.stock_level} items available',
                }, status=400)
            cart[product_key]['quantity'] = new_quantity
        else:
            if requested_quantity > product.stock_level:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Only {product.stock_level} items available',
                }, status=400)
            cart[product_key] = {
                'name': product.name,
                'price': float(product.discount_price),
                'image': product.image.url if product.image else '',
                'quantity': requested_quantity,
                'product_id': product_id
            }
        
        request.session['cart'] = cart
        request.session.modified = True
        
        # Log cart interaction
        log_interaction(request.user, product_id, 'cart', count_increment=requested_quantity)
        
        # Calculate cart count
        cart_count = sum(item['quantity'] for item in cart.values())
        
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} added to cart!',
            'cart_count': cart_count
        })
        
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to add to cart'
        }, status=500)


# ═══════════════════════════════════════════════════════════
# 12. VIEW CART
# ═══════════════════════════════════════════════════════════

def view_cart_view(request):
    """Display shopping cart"""
    
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0.0
    discount = 0.0
    total_items = 0
    invalid_product_keys = []
    
    # Build cart items with full product details
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(product_id=int(product_id))
            if not product.can_add_to_cart:
                invalid_product_keys.append(product_id)
                continue
            quantity = int(item.get('quantity', 1))
            unit_price = float(product.discount_price or 0)
            item_subtotal = unit_price * quantity
            cart_item = {
                'product': product,
                'product_id': product.product_id,
                'name': product.name,
                'category': product.category.name if product.category else '',
                'stock_level': product.stock_level,
                'image': _product_image_url(product),
                'price': unit_price,
                'quantity': quantity,
                'subtotal': item_subtotal,
            }
            cart_items.append(cart_item)
            subtotal += cart_item['subtotal']
            total_items += quantity
        except Product.DoesNotExist:
            invalid_product_keys.append(product_id)
            continue

    if invalid_product_keys:
        for invalid_key in invalid_product_keys:
            cart.pop(str(invalid_key), None)
        request.session['cart'] = cart
        request.session.modified = True

    remaining_for_free = max(0, round(2000 - subtotal, 2))
    delivery_fee = 0 if subtotal >= 2000 else 150
    total = subtotal - discount + delivery_fee
    cart_product_ids = {item['product_id'] for item in cart_items}
    checkout_product_id = next(
        (item['product_id'] for item in cart_items if item.get('stock_level', 0) > 0),
        None
    )

    actor_kwargs = _get_actor_recommendation_kwargs(request)
    recommended_products = _dedupe_products(
        get_recommendations(limit=6, **actor_kwargs),
        limit=6,
        exclude_ids=cart_product_ids,
    )
    if not recommended_products:
        recommended_products = _get_trending_products(limit=6, exclude_ids=cart_product_ids)

    recently_viewed_products = _get_recently_viewed_products(
        request,
        limit=6,
        exclude_ids=cart_product_ids,
    )
    trending_products = _get_trending_products(limit=6, exclude_ids=cart_product_ids)
    recommended_ids = [product.product_id for product in recommended_products]

    context = {
        'cart_items': cart_items,
        'total_price': subtotal,
        'subtotal': round(subtotal, 2),
        'discount': round(discount, 2),
        'delivery_fee': delivery_fee,
        'total': round(total, 2),
        'remaining_for_free': remaining_for_free,
        'total_items': total_items,
        'checkout_product_id': checkout_product_id,
        'recommended_products': recommended_products,
        'recommended_ids': recommended_ids,
        'trending_products': trending_products,
        'recently_viewed_products': recently_viewed_products,
    }
    
    return render(request, 'orders/cart.html', context)


# ═══════════════════════════════════════════════════════════
# 13. REMOVE FROM CART
# ═══════════════════════════════════════════════════════════

@login_required
def remove_from_cart_view(request, product_id):
    """Remove product from cart"""
    
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    
    if product_key in cart:
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Product removed from cart.')
    
    # Calculate new cart count
    cart_count = sum(item['quantity'] for item in cart.values())
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': cart_count
        })
    
    return redirect('store:cart')


# ═══════════════════════════════════════════════════════════
# 14. PLACE ORDER VIEW
# ═══════════════════════════════════════════════════════════

@login_required
def place_order_view(request, product_id):
    """Place order for a product."""
    product = Product.objects.select_related('category').filter(
        product_id=product_id,
        is_available=True,
    ).first()
    if not product:
        messages.error(request, 'Product is unavailable.')
        return redirect('store:product_list')
    if not product.can_add_to_cart:
        messages.error(request, 'This product is available on source only and cannot be checked out locally.')
        return redirect('store:product_detail', pk=product_id)

    token_key = _order_submission_session_key(product_id)

    if request.method == 'POST':
        submitted_token = request.POST.get('submission_token', '')
        expected_token = request.session.get(token_key)
        if not expected_token or submitted_token != expected_token:
            messages.warning(request, 'This order request was already processed. Please start a new checkout.')
            return redirect('store:order_history')

        # Consume token to prevent accidental double-submit on refresh/resend.
        request.session.pop(token_key, None)
        request.session.modified = True

        form = OrderForm(request.POST, product=product)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']

            try:
                with transaction.atomic():
                    locked_product = Product.objects.select_for_update().filter(
                        product_id=product_id,
                        is_available=True,
                    ).first()
                    if not locked_product:
                        messages.error(request, 'Product is unavailable.')
                        return redirect('store:place_order', product_id=product_id)

                    if locked_product.stock_level < quantity:
                        messages.error(request, f'Only {locked_product.stock_level} items available in stock.')
                        return redirect('store:place_order', product_id=product_id)

                    order = form.save(commit=False)
                    order.user = request.user
                    order.product = locked_product
                    order.unit_price = locked_product.discount_price
                    order.save()

                    locked_product.stock_level -= quantity
                    locked_product.save(update_fields=['stock_level'])

                    # Single source of truth: purchase interaction is logged only here.
                    log_interaction(request.user, product_id, 'purchase')

                # Clear cart only after successful order transaction.
                cart = request.session.get('cart', {})
                if str(product_id) in cart:
                    del cart[str(product_id)]
                    request.session['cart'] = cart
                    request.session.modified = True

                # Trigger recommendation refresh after successful commit path only.
                try:
                    engine = RecommendationEngine()
                    engine.generate_recommendations_for_user(request.user.id)
                except Exception as e:
                    logger.error(f"Error generating recommendations after purchase: {e}")

                messages.success(request, f'Order #{order.order_id} placed successfully! 🎉')
                return redirect('store:order_history')
            except Exception as e:
                logger.error(f"Error placing order: {e}")
                messages.error(request, 'Failed to place order. Please try again.')
                return redirect('store:place_order', product_id=product_id)
        _issue_order_submission_token(request, product_id)
    else:
        # Pre-fill form with profile data
        initial_data = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data = {
                'delivery_address': profile.address,
                'phone_number': profile.phone_number,
            }
        
        form = OrderForm(initial=initial_data, product=product)
    
    order_submission_token = _issue_order_submission_token(request, product_id)
    context = {
        'form': form,
        'product': product,
        'order_submission_token': order_submission_token,
    }
    
    return render(request, 'orders/place_order.html', context)


# ═══════════════════════════════════════════════════════════
# 15. ORDER HISTORY VIEW
# ═══════════════════════════════════════════════════════════

@login_required
def order_history_view(request):
    """Display user's order history"""
    
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # Calculate stats
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_price'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'total_orders': total_orders,
        'total_spent': total_spent,
    }
    
    return render(request, 'orders/order_history.html', context)


# ═══════════════════════════════════════════════════════════
# 16. SUBMIT FEEDBACK VIEW
# ═══════════════════════════════════════════════════════════

@login_required
def submit_feedback_view(request, product_id):
    """Submit product feedback/review"""
    
    product = get_object_or_404(Product, product_id=product_id)
    
    # Check if user has purchased this product
    has_purchased = Order.objects.filter(
        user=request.user,
        product=product
    ).exclude(status='cancelled').exists()
    
    if not has_purchased:
        messages.error(request, 'You can only review products you have purchased.')
        return redirect('store:product_detail', pk=product_id)
    
    # Check if user already gave feedback
    existing_feedback = Feedback.objects.filter(
        user=request.user,
        product=product
    ).first()
    
    if existing_feedback:
        messages.info(request, 'You have already reviewed this product.')
        return redirect('store:product_detail', pk=product_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.product = product
            feedback.save()
            
            # Update product rating (average of all feedbacks)
            avg_rating = Feedback.objects.filter(product=product).aggregate(
                avg=Avg('rating')
            )['avg']
            product.rating = round(avg_rating, 1)
            product.save(update_fields=['rating'])
            
            # Log like interaction
            log_interaction(request.user, product_id, 'like')
            
            messages.success(request, 'Thank you for your review! 🌟')
            return redirect('store:product_detail', pk=product_id)
    else:
        form = FeedbackForm()
    
    context = {
        'form': form,
        'product': product,
    }
    
    return render(request, 'feedback/submit_feedback.html', context)


# ═══════════════════════════════════════════════════════════
# 17. SEARCH VIEW
# ═══════════════════════════════════════════════════════════

def search_view(request):
    """Search products"""
    return product_list_view(request)


# ═══════════════════════════════════════════════════════════
# ADMIN PANEL VIEWS
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# 18. ADMIN DASHBOARD VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_dashboard_view(request):
    """Admin dashboard with stats and charts"""
    
    # Calculate stats
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    # Recent orders
    recent_orders = Order.objects.select_related(
        'user', 'product'
    ).order_by('-ordered_at')[:10]
    
    # Top 5 products by order count + revenue
    top_products = Product.objects.annotate(
        order_count=Count('order'),
        total_revenue=Sum('order__total_price'),
    ).order_by('-order_count')[:5]
    
    # Top 5 users by purchase amount
    top_users = User.objects.annotate(
        total_spent=Sum('orders__total_price')
    ).order_by('-total_spent')[:5]
    
    # Category breakdown
    category_data = Category.objects.annotate(
        product_count=Count('products')
    ).values('name', 'product_count')

    pending_orders = Order.objects.filter(status='pending').count()

    # Last six rolling 30-day windows for revenue trend (oldest to newest)
    revenue_data = []
    for window_index in range(5, -1, -1):
        window_start = timezone.now() - timedelta(days=(window_index + 1) * 30)
        window_end = timezone.now() - timedelta(days=window_index * 30)
        window_total = Order.objects.filter(
            ordered_at__gte=window_start,
            ordered_at__lt=window_end,
        ).aggregate(total=Sum('total_price'))['total'] or 0
        revenue_data.append(float(window_total))

    status_order = ['pending', 'confirmed', 'shipped', 'delivered']
    orders_by_status = [
        Order.objects.filter(status=status).count()
        for status in status_order
    ]
    
    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'top_users': top_users,
        'category_data': list(category_data),
        'pending_orders': pending_orders,
        'revenue_data': revenue_data,
        'orders_by_status': orders_by_status,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


# ═══════════════════════════════════════════════════════════
# 19. ADMIN PRODUCT LIST VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_product_list_view(request):
    """Admin product management list"""
    
    products = Product.objects.select_related('category').order_by('-created_at')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/product_list.html', context)


# ═══════════════════════════════════════════════════════════
# 20. ADMIN ADD PRODUCT VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_add_product_view(request):
    """Admin add new product"""
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('store:admin_products')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'action': 'Add',
    }
    
    return render(request, 'admin_panel/product_form.html', context)


# ═══════════════════════════════════════════════════════════
# 21. ADMIN EDIT PRODUCT VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_edit_product_view(request, product_id):
    """Admin edit product"""
    
    product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('store:admin_products')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'action': 'Edit',
    }
    
    return render(request, 'admin_panel/product_form.html', context)


# ═══════════════════════════════════════════════════════════
# 22. ADMIN DELETE PRODUCT VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_delete_product_view(request, product_id):
    """Admin delete product"""
    
    product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('store:admin_products')
    
    context = {
        'product': product,
    }
    
    return render(request, 'admin_panel/product_confirm_delete.html', context)


# ═══════════════════════════════════════════════════════════
# 23. ADMIN USER LIST VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_user_list_view(request):
    """Admin user management"""
    
    users = User.objects.select_related('profile').order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/user_management.html', context)


# ═══════════════════════════════════════════════════════════
# 24. ADMIN ORDER MANAGEMENT VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_order_management_view(request):
    """Admin order management"""
    
    orders = Order.objects.select_related('user', 'product').order_by('-ordered_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |
            Q(product__name__icontains=search_query) |
            Q(order_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin_panel/order_management.html', context)


# ═══════════════════════════════════════════════════════════
# 25. ADMIN ANALYTICS VIEW
# ═══════════════════════════════════════════════════════════

@staff_member_required
def admin_analytics_view(request):
    """Admin analytics and reports"""
    
    # Date range filter
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Revenue data
    orders = Order.objects.filter(ordered_at__gte=start_date)
    total_revenue = orders.aggregate(total=Sum('total_price'))['total'] or 0
    total_orders = orders.count()
    
    # Top products by revenue
    top_products_data = Product.objects.filter(
        order__ordered_at__gte=start_date
    ).annotate(
        revenue=Sum('order__total_price'),
        order_count=Count('order')
    ).order_by('-revenue')[:10]
    
    # Category performance
    category_performance = Category.objects.annotate(
        product_count=Count('products'),
        total_revenue=Sum('products__order__total_price', filter=Q(products__order__ordered_at__gte=start_date))
    ).order_by('-total_revenue')
    
    # User engagement stats
    total_views = UserInteraction.objects.filter(
        interaction_type='view',
        timestamp__gte=start_date
    ).count()
    
    total_cart_adds = UserInteraction.objects.filter(
        interaction_type='cart',
        timestamp__gte=start_date
    ).count()
    
    total_purchases = UserInteraction.objects.filter(
        interaction_type='purchase',
        timestamp__gte=start_date
    ).count()
    
    context = {
        'days': days,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'top_products_data': top_products_data,
        'category_performance': category_performance,
        'total_views': total_views,
        'total_cart_adds': total_cart_adds,
        'total_purchases': total_purchases,
    }
    
    return render(request, 'admin_panel/analytics.html', context)
