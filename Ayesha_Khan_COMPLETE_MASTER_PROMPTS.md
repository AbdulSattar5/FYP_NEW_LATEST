# 🚀 COMPLETE MASTER BUILD PROMPTS
## AI-Powered Personalized Product Platform

### Tech Stack: Python | Django | SQLite | Machine Learning | HTML5 | CSS3 | JavaScript

---

## 📋 COMPLETE BUILD ORDER TABLE

| Step | Prompt # | What It Creates |
|------|----------|-----------------|
| 1 | PROMPT 1 | Project setup, virtual env, Django settings, folder structure |
| 2 | PROMPT 2 | All database models + signals + admin registration |
| 3 | PROMPT 3 | AI Recommendation Engine (ML core) |
| 3.5 | PROMPT 3.5 | Complete ML Integration (interaction tracking + hybrid engine) |
| 4 | PROMPT 4 | All Django Forms |
| 5 | PROMPT 5 | All Views — complete backend logic |
| 5.5 | PROMPT 5.5 | Product data system + Category display views |
| 6 | PROMPT 6 | URL configuration (all routes) |
| 7 | PROMPT 7 | Base HTML template + Navbar + Footer |
| 8 | PROMPT 8 | Home Page (hero, categories, trending, AI recommendations) |
| 9 | PROMPT 9 | Auth templates (signup, login, profile) |
| 10 | PROMPT 10 | Product templates (list, detail, category, recommendations page) |
| 11 | PROMPT 11 | Order & Feedback templates |
| 12 | PROMPT 12 | Admin dashboard templates + analytics |
| 13 | PROMPT 13 | Complete CSS + JavaScript (all interactions) |
| 14 | PROMPT 14 | Sample data seeding + test products with images |
| 15 | PROMPT 15 | Final integration, testing & deployment checklist |

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 1 — PROJECT SETUP, SETTINGS & FOLDER STRUCTURE
# ═══════════════════════════════════════════════════════════

```
You are a senior Django developer. I am building an AI-Powered Personalized Product Platform — 
a full-stack e-commerce website with machine learning recommendations.

PROJECT NAME: ai_product_platform
APP NAME: store

=== STEP 1: COMPLETE SETUP INSTRUCTIONS ===

Give me the exact terminal commands to:
1. Create virtual environment: python -m venv venv
2. Activate it (Windows + Linux/Mac commands both)
3. Install ALL required packages:
   pip install django==4.2.x
   pip install pillow          # for ImageField (product images)
   pip install scikit-learn    # for ML recommendations
   pip install pandas          # for data manipulation
   pip install numpy           # for numerical operations
   pip install django-crispy-forms crispy-bootstrap5
   pip install whitenoise      # for static files in production

4. Create Django project: django-admin startproject ai_product_platform .
5. Create app: python manage.py startapp store
6. Create requirements.txt

=== STEP 2: SETTINGS.PY — COMPLETE FILE ===

Write the COMPLETE settings.py with:

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'crispy_forms',
    'crispy_bootstrap5',
]

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Database — SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media Files — CRITICAL for product images
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Security (for development — change in production)
SECRET_KEY = 'your-secret-key-here-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

=== STEP 3: FOLDER STRUCTURE ===

Create this EXACT folder structure:

ai_product_platform/
│
├── ai_product_platform/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py          ← main urls
│   ├── wsgi.py
│   └── asgi.py
│
├── store/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py          ← app urls
│   ├── recommendation_engine.py   ← ML engine
│   ├── signals.py
│   │
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── import_products.py   ← bulk CSV import
│   │       ├── seed_data.py         ← sample data
│   │       └── generate_recommendations.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── partials/
│   │   │   ├── navbar.html
│   │   │   ├── footer.html
│   │   │   ├── product_card.html    ← reusable product card
│   │   │   ├── pagination.html
│   │   │   └── messages.html
│   │   ├── auth/
│   │   │   ├── signup.html
│   │   │   ├── login.html
│   │   │   └── profile.html
│   │   ├── products/
│   │   │   ├── product_list.html
│   │   │   ├── product_detail.html
│   │   │   ├── category_products.html
│   │   │   └── recommendations.html
│   │   ├── orders/
│   │   │   ├── place_order.html
│   │   │   └── order_history.html
│   │   ├── feedback/
│   │   │   └── submit_feedback.html
│   │   └── admin_panel/
│   │       ├── dashboard.html
│   │       ├── product_form.html
│   │       ├── user_management.html
│   │       └── analytics.html
│   │
│   └── templatetags/
│       ├── __init__.py
│       └── store_tags.py   ← custom template tags
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│       └── logo.png       ← placeholder logo
│
├── media/               ← product images go here (auto-created)
│   └── products/
│
├── manage.py
└── requirements.txt

=== STEP 4: MAIN urls.py (ai_product_platform/urls.py) ===

Write the COMPLETE main urls.py:

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

CRITICAL: The + static(...) part is MANDATORY — without it, product images will NOT display.
This serves files from MEDIA_ROOT at MEDIA_URL. In development Django serves images directly.

=== STEP 5: apps.py ===

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    
    def ready(self):
        import store.signals

=== IMAGE DISPLAY EXPLANATION ===
When admin uploads a product image:
1. Django saves file to: media/products/filename.jpg
2. MEDIA_ROOT = BASE_DIR / 'media'  
3. In template: {{ product.image.url }} → /media/products/filename.jpg
4. Browser fetches: http://127.0.0.1:8000/media/products/filename.jpg
5. Django serves it because of static(settings.MEDIA_URL, ...) in urls.py

NO external API needed. NO Next.js needed. Django handles everything.

Write ALL files completely. Include every line of code.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 2 — ALL DATABASE MODELS + SIGNALS + ADMIN
# ═══════════════════════════════════════════════════════════

```
You are a senior Django developer. I am building an AI-Powered Personalized Product Platform.
Project setup is done. Now create ALL database models, signals, and admin configuration.

=== PART A: store/models.py — COMPLETE FILE ===

Write the COMPLETE models.py with ALL these models:

### 1. Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-tag', 
        help_text='FontAwesome icon class e.g. fa-laptop, fa-shirt, fa-mobile')
    color = models.CharField(max_length=7, default='#6C63FF',
        help_text='Hex color for category card background')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self): return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:category_products', kwargs={'slug': self.slug})

### 2. Product Model
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
        related_name='products')
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, 
        blank=True, null=True, help_text='Price before discount')
    is_on_discount = models.BooleanField(default=False)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, 
        default=0, help_text='e.g. 20 for 20% off')
    
    # Image — stores in media/products/
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Inventory
    stock_level = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Stats (auto-calculated)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    
    # Product attributes (flexible JSON for brand, color, size, etc.)
    attributes = models.JSONField(default=dict, blank=True,
        help_text='{"brand": "Samsung", "color": "Black", "warranty": "1 Year"}')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self): return self.name
    
    @property
    def discount_price(self):
        if self.is_on_discount and self.discount_percentage:
            discount = self.price * (self.discount_percentage / 100)
            return round(self.price - discount, 2)
        return self.price
    
    @property
    def is_in_stock(self):
        return self.stock_level > 0 and self.is_available
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = slugify(self.name) + '-' + str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('store:product_detail', kwargs={'pk': self.product_id})

### 3. UserInteraction Model (feeds the ML engine)
INTERACTION_TYPES = [
    ('view', 'Viewed'),
    ('cart', 'Added to Cart'),
    ('purchase', 'Purchased'),
    ('like', 'Liked/Feedback'),
    ('search', 'Searched'),
]

class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
        related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
        related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    interaction_count = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'product', 'interaction_type']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.interaction_type})"

### 4. Recommendation Model (stores ML-generated results)
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
        related_name='recommendations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0, 
        help_text='Relevance score 0.0 to 1.0 from ML engine')
    reason = models.CharField(max_length=200, default='Based on your activity',
        help_text='Human-readable reason for recommendation')
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-score']
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"Rec for {self.user.username}: {self.product.name} ({self.score:.2f})"
    
    @property
    def score_percentage(self):
        return int(self.score * 100)

### 5. Order Model
ORDER_STATUS = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
        related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    # Delivery details
    delivery_address = models.TextField()
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    
    # Pricing snapshot (keep original price at order time)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    notes = models.TextField(blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ordered_at']
    
    def __str__(self):
        return f"Order #{self.order_id} — {self.user.username} — {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

### 6. Feedback Model
class Feedback(models.Model):
    RATING_CHOICES = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
        related_name='feedbacks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
        related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} rated {self.product.name}: {self.rating}/5"

### 7. UserProfile Model (extends Django User)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
        related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    SUBSCRIPTION_TYPES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]
    subscription_type = models.CharField(max_length=10, 
        choices=SUBSCRIPTION_TYPES, default='free')
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    
    bio = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

=== PART B: store/signals.py — COMPLETE FILE ===

Write signals.py with:
1. Auto-create UserProfile when new User is created (post_save signal)
2. Auto-update product rating when new Feedback is submitted
3. Auto-update product stock when Order is confirmed
4. Log purchase interaction after order creation

Include ALL imports and full signal code.

=== PART C: store/admin.py — COMPLETE FILE ===

Register ALL models with professional admin configuration:

1. ProductAdmin:
   - list_display: name, category, price, discount_price property, stock_level, 
     is_featured, is_on_discount, rating, is_available
   - list_editable: price, stock_level, is_featured, is_on_discount, is_available
   - list_filter: category, is_featured, is_on_discount, is_available
   - search_fields: name, description
   - readonly_fields: rating, created_at, updated_at
   - fieldsets with sections: Basic Info, Pricing, Inventory, Attributes, Stats
   - Image preview in admin using custom method show_image()

2. CategoryAdmin:
   - list_display: name, slug, icon, color, product_count (custom method)
   - prepopulated_fields: {'slug': ('name',)}

3. OrderAdmin:
   - list_display: order_id, user, product, quantity, total_price, status, ordered_at
   - list_filter: status, ordered_at
   - list_editable: status
   - search_fields: user__username, product__name

4. FeedbackAdmin:
   - list_display: user, product, rating, comment, created_at
   - list_filter: rating

5. UserInteractionAdmin:
   - list_display: user, product, interaction_type, interaction_count, timestamp
   - list_filter: interaction_type

6. RecommendationAdmin:
   - list_display: user, product, score, reason, timestamp

7. UserProfileAdmin with inline in UserAdmin:
   - Show profile picture preview

=== PART D: MIGRATIONS ===

After writing all models, run:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

Write COMPLETE code for every file. Include all imports from django.db, django.contrib.auth.models, etc.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 3 — AI RECOMMENDATION ENGINE (ML CORE)
# ═══════════════════════════════════════════════════════════

```
You are an expert Django developer AND Machine Learning engineer.
I am building an AI-Powered Personalized Product Platform using Django + SQLite.
Models are already created. Now build the COMPLETE Machine Learning recommendation engine.

=== FILE: store/recommendation_engine.py ===

Write the COMPLETE recommendation_engine.py file with this architecture:

## IMPORTS (ALL required)
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

## INTERACTION WEIGHTS (how much each action matters)
INTERACTION_WEIGHTS = {
    'view': 1,
    'search': 1,
    'like': 2,
    'cart': 3,
    'purchase': 5,
}

## CLASS: RecommendationEngine
Build with these methods — ALL fully implemented:

### METHOD 1: _get_models(self)
Avoids circular imports. Returns: UserInteraction, Product, Recommendation, Category

### METHOD 2: build_interaction_matrix(self)
Builds user-item matrix:
- Query ALL UserInteraction records
- Create DataFrame with columns: user_id, product_id, interaction_type, interaction_count
- Apply INTERACTION_WEIGHTS to get weighted_score
- Pivot to matrix: rows=users, columns=products, values=weighted_score (sum, fill_value=0)
- Return matrix or empty DataFrame if no data

### METHOD 3: get_collaborative_filtering_recommendations(self, user_id, n=10)
Collaborative Filtering:
- Build interaction matrix
- If user_id not in matrix: return get_popular_products(n)
- Calculate cosine_similarity on matrix
- Find top 5 similar users (excluding self)
- Get products those similar users interacted with (not seen by target user)
- Score = similarity_score * interaction_score
- Return top n product_ids by score
- Full try/except with logger.error on failure

### METHOD 4: get_content_based_recommendations(self, user_id, n=10)
Content-Based Filtering using TF-IDF:
- Get all interactions for this user
- If no interactions: return get_popular_products(n)
- Build user preference text (product name + category + description, repeated by weight)
- Build TF-IDF on ALL available products
- Transform user profile text with same vectorizer
- Calculate cosine similarity between user vector and all products
- Exclude already-interacted products
- Return top n product_ids
- Full try/except with logger.error on failure

### METHOD 5: get_popular_products(self, n=10)
Cold-start fallback:
- Return products ordered by -rating, -stock_level where is_available=True, stock_level>0
- Used for new users with no history

### METHOD 6: get_hybrid_recommendations(self, user_id, n=10)
Hybrid (60% collaborative + 40% content-based):
- Check if user has ANY interactions
- If not: return get_popular_products(n)
- Get both collaborative and content-based recommendations
- Merge strategy:
  * BOTH lists = highest priority (score=1.0, reason="Highly recommended for you")
  * Collaborative only = 0.6 weight (reason="Based on similar shoppers")
  * Content only = 0.4 weight (reason="Based on your browsing history")
  * Popular fallback = 0.1 (reason="Trending product")
- Return list of tuples: [(product_id, score, reason), ...][:n]

### METHOD 7: generate_recommendations_for_user(self, user_id)
Save to database:
- Call get_hybrid_recommendations(user_id, n=12)
- DELETE old recommendations for this user
- Create Recommendation objects in bulk_create
- Log success/failure
- Return new_recs list

### METHOD 8: generate_all_recommendations(self)
Batch processing:
- Get ALL active users
- Call generate_recommendations_for_user for each
- Log progress
- Return total count

## STANDALONE FUNCTION: get_quick_recommendations(user_id, n=6)
Fast function for views:
1. Check Recommendation table for saved recs for this user
2. If found: return Product queryset with select_related('category')
3. If NOT found: run engine.generate_recommendations_for_user(user_id) then retry
4. Final fallback: return popular products by rating
Returns: Product queryset (not just IDs) — READY to pass to template

=== FILE: store/management/commands/generate_recommendations.py ===

Management command to regenerate all recommendations:
- Usage: python manage.py generate_recommendations
- Optional: --user-id flag to regenerate for specific user only
- Print progress to console
- Log start time, end time, total users processed

Write COMPLETE code for every method. No shortcuts. No "# implement this" comments.
Every line of code must be functional and production-quality.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 3.5 — COMPLETE ML INTEGRATION
# (Interaction Tracking + Views Connection + Auto-refresh)
# ═══════════════════════════════════════════════════════════

```
You are an expert Django developer. I have my ML engine built. 
Now I need the COMPLETE integration — how interactions are automatically logged,
and how recommendations connect to every view and template.

=== PART A: INTERACTION TRACKING HELPER ===

Add this helper function at the TOP of store/views.py (before any views):

def log_interaction(user, product_id, interaction_type, count_increment=1):
    """
    Automatically called from views to track user behavior for ML engine.
    interaction_type: 'view', 'cart', 'purchase', 'like', 'search'
    """
    if not user.is_authenticated:
        return
    
    try:
        product = Product.objects.get(product_id=product_id, is_available=True)
        interaction, created = UserInteraction.objects.get_or_create(
            user=user,
            product=product,
            interaction_type=interaction_type,
            defaults={'interaction_count': count_increment}
        )
        if not created:
            interaction.interaction_count += count_increment
            interaction.save(update_fields=['interaction_count'])
    except Product.DoesNotExist:
        pass

WHERE IS IT CALLED? (add to each relevant view automatically):
1. product_detail_view → log_interaction(request.user, pk, 'view')
2. add_to_cart_view → log_interaction(request.user, product_id, 'cart')  
3. place_order_view (after order.save()) → log_interaction(request.user, product.product_id, 'purchase')
4. submit_feedback_view (after feedback.save()) → log_interaction(request.user, product.product_id, 'like')

=== PART B: RECOMMENDATION VIEWS ===

Write these COMPLETE views in store/views.py:

### recommendations_view (full page)
@login_required
def recommendations_view(request):
    # Always regenerate fresh recommendations
    engine = RecommendationEngine()
    engine.generate_recommendations_for_user(request.user.id)
    
    # Get all recommendations with product details
    recommendations = Recommendation.objects.filter(
        user=request.user
    ).select_related('product', 'product__category').order_by('-score')
    
    # User stats for display
    interaction_count = UserInteraction.objects.filter(user=request.user).count()
    products_viewed = UserInteraction.objects.filter(user=request.user, interaction_type='view').count()
    products_purchased = UserInteraction.objects.filter(user=request.user, interaction_type='purchase').count()
    items_carted = UserInteraction.objects.filter(user=request.user, interaction_type='cart').count()
    
    paginator = Paginator(recommendations, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'interaction_count': interaction_count,
        'products_viewed': products_viewed,
        'products_purchased': products_purchased,
        'items_carted': items_carted,
        'total_recs': recommendations.count(),
    }
    return render(request, 'products/recommendations.html', context)

### refresh_recommendations_view (AJAX endpoint)
@login_required
def refresh_recommendations_view(request):
    if request.method == 'POST':
        engine = RecommendationEngine()
        recs = engine.generate_recommendations_for_user(request.user.id)
        return JsonResponse({
            'status': 'success',
            'count': len(recs),
            'message': f'Generated {len(recs)} fresh recommendations!'
        })
    return JsonResponse({'status': 'error'}, status=405)

=== PART C: HOW RECOMMENDATIONS APPEAR IN EVERY VIEW ===

### In home_view — add to context:
recommended_products = []
recommended_ids = []
if request.user.is_authenticated:
    recommended_products = get_quick_recommendations(request.user.id, n=6)
    recommended_ids = list(recommended_products.values_list('product_id', flat=True))
else:
    recommended_products = Product.objects.filter(
        is_available=True, stock_level__gt=0
    ).order_by('-rating')[:6].select_related('category')

context['recommended_products'] = recommended_products
context['recommended_ids'] = recommended_ids

### In product_detail_view — add:
# Log view + trigger recommendation refresh
log_interaction(request.user, pk, 'view')

# Check if recommendations are fresh (less than 1 hour old)
if request.user.is_authenticated:
    from django.utils import timezone
    from datetime import timedelta
    recent_rec_exists = Recommendation.objects.filter(
        user=request.user,
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).exists()
    if not recent_rec_exists:
        engine = RecommendationEngine()
        engine.generate_recommendations_for_user(request.user.id)

# Similar products from same category
similar_products = Product.objects.filter(
    category=product.category, is_available=True
).exclude(product_id=pk).order_by('-rating')[:6].select_related('category')

# Personalized recs for sidebar
personalized_products = []
if request.user.is_authenticated:
    personalized_products = get_quick_recommendations(request.user.id, n=4)

context['similar_products'] = similar_products
context['personalized_products'] = personalized_products

=== PART D: COMPLETE DATA FLOW DIAGRAM IN CODE COMMENTS ===

Add this comment block to recommendation_engine.py explaining the complete flow:

# DATA FLOW:
# USER ACTION → log_interaction() → UserInteraction table
#     ↓
# RecommendationEngine.get_hybrid_recommendations()
#     → Collaborative Filtering (cosine similarity between users)
#     → Content-Based Filtering (TF-IDF on product descriptions)
#     → Hybrid merge (60% collab + 40% content)
#     ↓
# Recommendation objects saved to database
#     ↓
# get_quick_recommendations() fetches from DB → Product queryset
#     ↓
# Template displays: {{ product.image.url }} → /media/products/image.jpg
#     (served by Django via MEDIA_URL config in main urls.py)

Write COMPLETE code for every part. Every function fully implemented.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 4 — ALL DJANGO FORMS
# ═══════════════════════════════════════════════════════════

```
You are a senior Django developer. Models and ML engine are ready.
Now write ALL Django Forms for the AI-Powered Personalized Product Platform.

=== FILE: store/forms.py — COMPLETE FILE ===

Write EVERY form with Bootstrap 5 styling, validation, and error messages.

### 1. UserSignupForm (extends UserCreationForm)
Fields:
- username (TextInput, placeholder='Choose username')
- first_name (TextInput, required)
- last_name (TextInput, required)  
- email (EmailInput, required, unique validation)
- password1 (PasswordInput)
- password2 (PasswordInput, confirm)
- phone_number (TextInput, optional)
- profile_picture (FileInput, optional)
- subscription_type (Select: Free/Premium)
- agree_terms (CheckboxInput, required=True)

Custom validation:
- clean_email(): check email is unique in User table, raise ValidationError if exists
- clean_username(): check no special chars
- All Bootstrap 5 classes applied via widgets

### 2. UserLoginForm (extends AuthenticationForm)
Fields:
- username (TextInput with icon, placeholder='Username or Email')
- password (PasswordInput with show/hide toggle)
- remember_me (CheckboxInput)

### 3. UserProfileUpdateForm (ModelForm for UserProfile)
Fields:
- first_name, last_name (from User model, not UserProfile)
- profile_picture (ImageField with preview)
- phone_number
- address (Textarea)
- bio (Textarea, max 500 chars with character counter)

### 4. ProductSearchForm
Fields:
- query (TextInput, placeholder='Search products...', autofocus)
- category (ModelChoiceField, queryset=Category.objects.all(), required=False)
- min_price (NumberInput, min=0, required=False)
- max_price (NumberInput, min=0, required=False)
- sort_by (Select: newest, price_asc, price_desc, rating, discount)

### 5. OrderForm (ModelForm for Order)
Fields:
- quantity (NumberInput, min=1)
- delivery_address (Textarea, placeholder='Full delivery address')
- city (TextInput)
- phone_number (TextInput, placeholder='+92 300 1234567')
- notes (Textarea, optional, placeholder='Special instructions...')

Custom validation:
- clean_quantity(): check against product stock_level
- clean_phone_number(): validate Pakistani format (+92 or 0300...)

### 6. FeedbackForm (ModelForm for Feedback)
Fields:
- rating (RadioSelect with star styling, choices 1-5)
- comment (Textarea, optional, placeholder='Tell us about this product...')

Custom widget: rating displayed as 5 clickable star icons (via CSS)

### 7. ProductForm (Admin — for custom admin panel)
Fields: ALL product fields
- name, category, description, attributes (JSON)
- price, original_price, discount_percentage
- stock_level, image
- is_available, is_featured, is_on_discount (all CheckboxInput)

Custom validation:
- clean_discount_percentage(): ensure 0-100
- clean_price(): ensure > 0
- clean(): if is_on_discount, original_price must be set and > price

### 8. ContactForm (for feedback/contact page)
Fields: name, email, subject, message

=== COMPLETE FORM STRUCTURE ===

For EACH form:
1. Full Meta class with model, fields, widgets
2. All Bootstrap 5 attrs: class='form-control', class='form-select', etc.
3. placeholders, help_text, labels
4. Custom clean_ methods for validation
5. Custom __init__ if needed

Write COMPLETE forms.py — every form fully coded. No shortcuts.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 5 — ALL VIEWS (COMPLETE BACKEND LOGIC)
# ═══════════════════════════════════════════════════════════

```
You are a senior Django developer. Models, forms, and ML engine are all ready.
Now write ALL views for the AI-Powered Personalized Product Platform.

=== FILE: store/views.py — COMPLETE FILE ===

Import everything needed at the top:
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import *
from .forms import *
from .recommendation_engine import RecommendationEngine, get_quick_recommendations

## HELPER FUNCTION (add at top)
def log_interaction(user, product_id, interaction_type, count_increment=1):
    [complete implementation as in Prompt 3.5]

## 1. home_view(request)
URL: /
- Get featured products (is_featured=True, is_available=True, top 8)
- Get trending products (ordered by -rating, is_available=True, top 8)
- Get discounted products (is_on_discount=True, ordered by -discount_percentage, top 6)
- Get all categories with product_count annotation
- Get AI recommendations (from get_quick_recommendations if authenticated, else popular)
- Context: featured_products, trending_products, discounted_products, 
           categories, recommended_products, recommended_ids
- Template: home.html

## 2. signup_view(request)
URL: /signup/
- If already logged in: redirect to home
- GET: render empty UserSignupForm
- POST: validate form, create User, create UserProfile with phone/pic/subscription,
        auto-login after signup, success message "Welcome to AI Shop!", redirect home
- Template: auth/signup.html

## 3. login_view(request)
URL: /login/
- If already logged in: redirect to home
- GET: render UserLoginForm
- POST: authenticate user, login if valid, handle remember_me (session expiry),
        redirect to 'next' parameter or home
- Error messages for invalid credentials
- Template: auth/login.html

## 4. logout_view(request)
URL: /logout/
- POST only, call logout(request), success message, redirect home

## 5. profile_view(request)
@login_required
URL: /profile/
- GET: get UserProfile, recent orders (last 5), total_orders count, 
       total_spent (sum of total_price), feedbacks given count
- POST: update User (first_name, last_name) + UserProfile
- Context: profile, recent_orders, total_orders, total_spent, feedbacks_count
- Template: auth/profile.html

## 6. product_list_view(request)
URL: /products/
- Get ALL products with is_available=True
- Apply search: Q(name__icontains=q) | Q(description__icontains=q)
- Apply category filter: ?category=slug
- Apply price filter: ?min_price=X&max_price=Y
- Apply sort: ?sort_by=newest|price_asc|price_desc|rating|discount
- Paginate: 12 per page
- Get all categories for sidebar filter
- Get recommended product IDs for badge display
- Context: page_obj, categories, total_count, current_category,
           search_query, sort_by, recommended_ids, min_price, max_price
- Template: products/product_list.html

## 7. product_detail_view(request, pk)
URL: /product/<int:pk>/
- Get product or 404 (is_available=True)
- Log view interaction: log_interaction(request.user, pk, 'view')
- Trigger recommendation refresh if >1 hour since last rec
- Similar products: same category, top 6 by rating, exclude current
- Personalized products: get_quick_recommendations(n=4)
- Product feedbacks: Feedback.objects.filter(product=product)
- Check if user already gave feedback: has_feedback bool
- Average rating: feedbacks.aggregate(Avg('rating'))
- Context: product, similar_products, personalized_products, 
           feedbacks, has_feedback, avg_rating
- Template: products/product_detail.html

## 8. category_products_view(request, slug)
URL: /category/<slug:slug>/
- Get category or 404
- Filter products by category + is_available=True
- Apply sort (same as product_list)
- Apply price filter
- Paginate: 12 per page
- Get all categories for sidebar with product_count annotation
- Get user recommendations for badge
- Context: category, page_obj, all_categories, user_recommendations,
           total_count, current_sort, min_price, max_price
- Template: products/category_products.html

## 9. recommendations_view(request)
@login_required
URL: /recommendations/
[Full implementation from Prompt 3.5]

## 10. refresh_recommendations_view(request)
@login_required
URL: /recommendations/refresh/
[Full implementation from Prompt 3.5]

## 11. add_to_cart_view(request, product_id)
@login_required, @require_POST
URL: /cart/add/<int:product_id>/
- Get product or 404
- Check stock_level > 0
- Add to session cart: request.session['cart']
  Cart structure: {'product_id': {'name': ..., 'price': ..., 'image': ..., 'quantity': ..., 'product_id': ...}}
- Log interaction: log_interaction(request.user, product_id, 'cart')
- Return JsonResponse({'status': 'success', 'cart_count': total_items, 'message': 'Added!'})

## 12. view_cart_view(request)
URL: /cart/
- Get cart from session: request.session.get('cart', {})
- Build cart_items list with full product details from DB
- Calculate total_price, total_items
- Context: cart_items, total_price, total_items
- Template: orders/cart.html

## 13. remove_from_cart_view(request, product_id)
@login_required
URL: /cart/remove/<int:product_id>/
- Remove from session cart
- Return JsonResponse with new cart_count

## 14. place_order_view(request, product_id)
@login_required
URL: /order/<int:product_id>/
- Get product or 404
- GET: render OrderForm pre-filled with profile address
- POST: validate OrderForm
  * Check stock_level >= quantity
  * Create Order with unit_price = product.discount_price
  * Decrease product.stock_level by quantity
  * Log interaction: log_interaction(request.user, product_id, 'purchase', quantity)
  * Trigger generate_recommendations_for_user (more accurate after purchase)
  * Success message with order_id
  * Redirect to order_history
- Template: orders/place_order.html

## 15. order_history_view(request)
@login_required
URL: /orders/
- Get all orders for this user, ordered by -ordered_at
- Paginate: 10 per page
- Context: page_obj, total_orders, total_spent
- Template: orders/order_history.html

## 16. submit_feedback_view(request, product_id)
@login_required
URL: /feedback/<int:product_id>/
- Get product or 404
- Check user has purchased this product (Order exists with status not cancelled)
- If not purchased: error message "You can only review purchased products"
- Check no existing feedback: if exists, redirect with message "Already reviewed"
- POST: validate FeedbackForm
  * Save feedback
  * Update product rating (average of all feedbacks)
  * Log interaction: log_interaction(request.user, product_id, 'like')
  * Success message
  * Redirect to product_detail
- Template: feedback/submit_feedback.html

## 17. search_view(request)
URL: /search/
- Get q from GET params
- Search: Product.objects.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q), is_available=True)
- Log search interaction for each result product? No — just for top result
- Paginate: 12 per page
- Template: products/product_list.html (reuse with search context)

## ADMIN PANEL VIEWS (staff_member_required)

## 18. admin_dashboard_view(request)
URL: /admin-panel/
- Stats: total_users, total_products, total_orders, total_revenue
- Recent 10 orders
- Top 5 products by order count
- Top 5 users by purchase amount
- Category breakdown (pie chart data)
- Template: admin_panel/dashboard.html

## 19. admin_product_list_view(request)
## 20. admin_add_product_view(request)
## 21. admin_edit_product_view(request, product_id)
## 22. admin_delete_product_view(request, product_id)
## 23. admin_user_list_view(request)
## 24. admin_order_management_view(request)
## 25. admin_analytics_view(request)
[Full implementation for each — CRUD operations on products/users/orders]

Write COMPLETE views.py — every view fully implemented with all logic.
No "# TODO" or placeholder comments. Production-ready code.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 5.5 — PRODUCT DATA SYSTEM + CATEGORY DISPLAY
# (How products enter DB + complete category page)
# ═══════════════════════════════════════════════════════════

```
You are an expert Django developer. I need the COMPLETE product data management system.

=== PART A: HOW PRODUCTS ENTER THE DATABASE ===

### METHOD 1: Django Admin (Built-in — already covered in Prompt 2)
Admin URL: http://127.0.0.1:8000/django-admin/store/product/add/
This is where admin manually adds products WITH IMAGE UPLOAD.

Image display in admin:
def show_image(self, obj):
    if obj.image:
        return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:5px;">', obj.image.url)
    return "No Image"
show_image.short_description = 'Preview'

### METHOD 2: Bulk CSV Import
Create: store/management/commands/import_products.py

COMPLETE CODE:
import csv
from django.core.management.base import BaseCommand
from store.models import Product, Category

class Command(BaseCommand):
    help = 'Import products from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
    
    def handle(self, *args, **options):
        csv_path = options['csv_file']
        imported = 0
        skipped = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    category, _ = Category.objects.get_or_create(
                        name=row['category'],
                        defaults={'slug': row['category'].lower().replace(' ', '-')}
                    )
                    Product.objects.create(
                        name=row['name'],
                        category=category,
                        description=row['description'],
                        price=float(row['price']),
                        original_price=float(row.get('original_price', 0)) or None,
                        stock_level=int(row.get('stock_level', 10)),
                        is_featured=row.get('is_featured', '').lower() == 'true',
                        is_on_discount=row.get('is_on_discount', '').lower() == 'true',
                        discount_percentage=float(row.get('discount_percentage', 0)),
                        attributes={
                            'brand': row.get('brand', ''),
                            'color': row.get('color', '')
                        }
                    )
                    imported += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Skipped row: {e}"))
                    skipped += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {imported} products. Skipped {skipped}.'))

CSV Format:
name,category,description,price,original_price,stock_level,is_featured,is_on_discount,discount_percentage,brand,color

### METHOD 3: Custom Admin Panel
[Write admin_add_product_view, admin_edit_product_view, admin_delete_product_view 
with ProductForm — COMPLETE code as defined in Prompt 5]

=== PART B: CATEGORY PRODUCTS VIEW (COMPLETE) ===

Write the COMPLETE category_products_view (also defined in Prompt 5):
[Full implementation with sorting, filtering, pagination, recommendations]

=== PART C: CUSTOM TEMPLATE TAGS ===

Create: store/templatetags/store_tags.py

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def currency(value):
    return f"Rs. {float(value):,.0f}"

@register.filter
def star_range(rating):
    return range(1, 6)  # for template star loop

@register.simple_tag
def get_cart_count(request):
    cart = request.session.get('cart', {})
    return sum(item.get('quantity', 1) for item in cart.values())

@register.simple_tag
def category_color(category_name):
    colors = {
        'Electronics': '#6C63FF',
        'Clothing': '#FF6584',
        'Books': '#43AA8B',
        'Food': '#F8961E',
        'Beauty': '#F72585',
        'Sports': '#4CC9F0',
    }
    return colors.get(category_name, '#6C63FF')

=== PART D: PRODUCT CARD PARTIAL TEMPLATE ===

Create: store/templates/partials/product_card.html
This REUSABLE card is included in home.html, product_list.html, category_products.html, etc.

Design the card to show:
1. Product image ({{ product.image.url }} or placeholder icon if no image)
2. Category badge
3. "🤖 For You" green badge if product.product_id in recommended_ids
4. Discount badge if is_on_discount
5. Product name (2 lines max, text-overflow ellipsis)
6. Star rating (5 stars, filled based on product.rating)
7. Price (crossed-out original + discount price in red if on discount)
8. "Add to Cart" button (calls addToCart(product_id) JS function)
9. "View Details" link
10. Stock warning: "Only X left!" if stock_level < 5

Usage: {% include 'partials/product_card.html' with product=product recommended_ids=recommended_ids %}

Write COMPLETE code for ALL parts above.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 6 — URL CONFIGURATION
# ═══════════════════════════════════════════════════════════

```
You are a senior Django developer. Write the COMPLETE URL configuration.

=== FILE: store/urls.py — COMPLETE FILE ===

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Home
    path('', views.home_view, name='home'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Products
    path('products/', views.product_list_view, name='product_list'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('category/<slug:slug>/', views.category_products_view, name='category_products'),
    path('search/', views.search_view, name='search'),
    
    # AI Recommendations
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('recommendations/refresh/', views.refresh_recommendations_view, name='refresh_recommendations'),
    
    # Cart (session-based)
    path('cart/', views.view_cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    
    # Orders
    path('order/<int:product_id>/', views.place_order_view, name='place_order'),
    path('orders/', views.order_history_view, name='order_history'),
    
    # Feedback
    path('feedback/<int:product_id>/', views.submit_feedback_view, name='submit_feedback'),
    
    # Admin Panel (custom — separate from django-admin)
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/products/', views.admin_product_list_view, name='admin_products'),
    path('admin-panel/products/add/', views.admin_add_product_view, name='admin_add_product'),
    path('admin-panel/products/edit/<int:product_id>/', views.admin_edit_product_view, name='admin_edit_product'),
    path('admin-panel/products/delete/<int:product_id>/', views.admin_delete_product_view, name='admin_delete_product'),
    path('admin-panel/users/', views.admin_user_list_view, name='admin_users'),
    path('admin-panel/orders/', views.admin_order_management_view, name='admin_orders'),
    path('admin-panel/analytics/', views.admin_analytics_view, name='admin_analytics'),
]

=== FILE: ai_product_platform/urls.py (main) — COMPLETE ===

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

CRITICAL NOTE:
The line: + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
IS ESSENTIAL for product images to display in browser.
Without this, all product images show as broken image icons.
This tells Django: serve files from MEDIA_ROOT at MEDIA_URL path in development.

=== NAMED URL REFERENCE TABLE ===

| URL Name | Pattern | Used In |
|----------|---------|---------|
| store:home | / | navbar, redirects |
| store:signup | /signup/ | navbar, login page link |
| store:login | /login/ | navbar, decorators |
| store:logout | /logout/ | navbar form |
| store:profile | /profile/ | navbar user menu |
| store:product_list | /products/ | navbar, categories |
| store:product_detail | /product/<pk>/ | product cards |
| store:category_products | /category/<slug>/ | category list |
| store:recommendations | /recommendations/ | navbar, home |
| store:cart | /cart/ | navbar cart icon |
| store:add_to_cart | /cart/add/<id>/ | product card buttons |
| store:place_order | /order/<id>/ | product detail |
| store:order_history | /orders/ | profile, navbar |
| store:submit_feedback | /feedback/<id>/ | product detail |
| store:admin_dashboard | /admin-panel/ | admin nav |

Write complete urls.py exactly as shown above.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 7 — BASE HTML TEMPLATE + NAVBAR + FOOTER
# ═══════════════════════════════════════════════════════════

```
You are a senior frontend developer. Create the COMPLETE base template for an 
AI-Powered E-commerce platform. Professional, modern, Bootstrap 5 design.

=== FILE: store/templates/base.html — COMPLETE FILE ===

Design Requirements:
- Modern, clean, professional e-commerce look
- Color scheme: Primary #6C63FF (purple), Secondary #3F8EFC (blue)
- Font: Google Fonts — Poppins (main text) + Inter (UI elements)
- Fully responsive (mobile-first)
- Bootstrap 5.3 CDN + FontAwesome 6 CDN

HTML Structure:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI Shop — Smart Shopping, Tailored For You{% endblock %}</title>
    
    <!-- Bootstrap 5.3 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- FontAwesome 6 -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- Google Fonts: Poppins -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Custom CSS -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>

    {% include 'partials/navbar.html' %}
    
    <!-- Flash Messages -->
    {% include 'partials/messages.html' %}
    
    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>
    
    {% include 'partials/footer.html' %}
    
    <!-- Bootstrap 5 JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>

=== FILE: store/templates/partials/navbar.html — COMPLETE ===

Design a professional e-commerce navbar:

TOP BAR (hidden on mobile):
- Left: 📞 +92-300-0000000 | ✉️ support@aishop.com
- Right: Free shipping on orders over Rs. 2000!

MAIN NAVBAR (sticky-top with shadow on scroll):
- Left: Logo (AI Shop text with gradient + ⚡ icon)
- Center: Search bar (full width) with category dropdown
- Right: 
  * 🤖 Recommendations (only if logged in, badge with count)
  * Cart icon with badge count
  * If logged in: Avatar dropdown (Profile, Orders, Logout)
  * If not logged in: Login + Signup buttons

CATEGORY NAV BAR (below main):
- Horizontal scrollable list of ALL categories with icons
- Each as a pill button linking to category page

JavaScript in navbar:
1. Make navbar sticky with shadow on scroll:
   window.addEventListener('scroll', () => {
     if(window.scrollY > 50) navbar.classList.add('shadow-lg', 'sticky-shadow');
   });
2. Search form: on Enter key, redirect to /search/?q=...
3. Cart badge updates via AJAX

=== FILE: store/templates/partials/footer.html — COMPLETE ===

Professional 4-column footer:

Column 1: About AI Shop
- Logo + tagline "Smart Shopping, Tailored For You"
- Short description about AI-powered recommendations
- Social media icons: Facebook, Instagram, Twitter, LinkedIn

Column 2: Quick Links
- Home, Shop, About, Contact
- Recommendations (logged in users)
- Track Order

Column 3: Categories
- Loop through top 6 categories from context
- Each as a link

Column 4: Contact & Newsletter
- Address: IUB, Bahawalpur, Pakistan
- Email input + Subscribe button
- Payment icons (Visa, Mastercard, JazzCash, EasyPaisa)

Bottom bar:
- © 2024 AI Shop. All rights reserved.
- Privacy Policy | Terms of Service
- Built with ❤️ + 🤖 AI by Ayesha Khan

=== FILE: store/templates/partials/messages.html ===

Display Django messages as dismissible Bootstrap 5 alerts:
{% if messages %}
<div class="container mt-2">
    {% for message in messages %}
    <div class="alert {{ message.tags }} alert-dismissible fade show" role="alert">
        {% if 'success' in message.tags %}<i class="fas fa-check-circle me-2"></i>{% endif %}
        {% if 'error' in message.tags %}<i class="fas fa-exclamation-circle me-2"></i>{% endif %}
        {% if 'warning' in message.tags %}<i class="fas fa-exclamation-triangle me-2"></i>{% endif %}
        {% if 'info' in message.tags %}<i class="fas fa-info-circle me-2"></i>{% endif %}
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
    {% endfor %}
</div>
{% endif %}

Auto-dismiss after 4 seconds with JavaScript.

Write COMPLETE HTML for all 4 files. Include every line of code.
Professional, beautiful design. Include all Django template tags.
{% load static %}, {% url 'store:...' %}, {% if user.is_authenticated %} etc.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 8 — HOME PAGE
# (Hero, Categories, Trending, Discounts, AI Recommendations)
# ═══════════════════════════════════════════════════════════

```
You are a senior frontend developer + Django template expert.
Create the COMPLETE, BEAUTIFUL home page for the AI-Powered E-commerce platform.

=== FILE: store/templates/home.html — COMPLETE FILE ===

{% extends 'base.html' %}
{% load static store_tags %}

=== SECTION 1: HERO BANNER ===
Full-width gradient hero (purple to blue):
- Left side (60%):
  * "Smart Shopping," in big bold text
  * "Tailored For You 🤖" with gradient text effect
  * Subtitle: "AI-powered recommendations based on YOUR preferences"
  * Two CTA buttons: "Shop Now" (primary) + "See My Recommendations" (outline, only if logged in)
  * Stats row: 1000+ Products | AI-Powered | 500+ Happy Customers

- Right side (40%):
  * Animated shopping illustration (CSS-drawn or hero image)
  * Floating cards showing "🤖 AI Match: 95%", "⭐ Top Rated", "🔥 Trending"

=== SECTION 2: CATEGORY PILLS ===
"Browse by Category"
- Horizontal scrollable row of category cards
- Each card: gradient background, white icon, category name, product count
- Hover effect: lift + shadow
- Click: goes to /category/<slug>/
- Mobile: horizontal scroll with custom scrollbar

=== SECTION 3: LIMITED TIME DISCOUNT BANNER ===
Only shown if discounted products exist:
- Red/orange gradient banner
- "🔥 Limited Time Offer — Up to 20% OFF!"
- Countdown timer (JavaScript): HH:MM:SS
- "Shop Sale" button
- Horizontal scroll of discounted product cards

=== SECTION 4: AI RECOMMENDATIONS ("Recommended For You") ===
CRITICAL SECTION — only for logged-in users:

{% if user.is_authenticated and recommended_products %}
<section class="py-5" style="background: linear-gradient(135deg, #f8f7ff, #f0eeff);">
  <div class="container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">🤖 <span class="text-gradient">Recommended For You</span></h2>
        <p class="text-muted mb-0">Powered by AI — Based on your browsing & purchase history</p>
      </div>
      <a href="{% url 'store:recommendations' %}" class="btn btn-outline-primary btn-sm rounded-pill">
        See All <i class="fas fa-arrow-right ms-1"></i>
      </a>
    </div>
    <div class="row g-3">
      {% for product in recommended_products %}
      <div class="col-lg-2 col-md-3 col-sm-4 col-6">
        {% include 'partials/product_card.html' with product=product recommended_ids=recommended_ids badge_label="🤖 For You" %}
      </div>
      {% endfor %}
    </div>
  </div>
</section>
{% else %}
<!-- For guests: show login prompt with benefits -->
<section class="py-5 text-center" style="background: linear-gradient(135deg, #f8f7ff, #f0eeff);">
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-6">
        <div style="font-size:4rem;">🤖</div>
        <h3 class="fw-bold mt-3">Get Personalized Recommendations</h3>
        <p class="text-muted">Our AI learns your preferences and shows you products you'll love!</p>
        <div class="d-flex gap-3 justify-content-center mt-3">
          <a href="{% url 'store:signup' %}" class="btn btn-primary rounded-pill px-4">Create Account</a>
          <a href="{% url 'store:login' %}" class="btn btn-outline-primary rounded-pill px-4">Login</a>
        </div>
      </div>
    </div>
  </div>
</section>
{% endif %}

=== SECTION 5: TRENDING PRODUCTS ===
"🔥 Trending Products"
- Grid: 4 per row desktop, 2 tablet, 1 mobile
- Use {% include 'partials/product_card.html' %} for each product
- "View All" button linking to /products/

=== SECTION 6: FEATURED PRODUCTS ===
"⭐ Featured Products"
- Similar grid layout
- Products with is_featured=True

=== SECTION 7: WHY CHOOSE AI SHOP ===
3-column feature cards:
1. 🤖 AI Recommendations — Personalized picks just for you
2. 🛡️ Secure Shopping — Encrypted transactions, safe data
3. ⚡ Fast Delivery — Quick delivery across Pakistan

=== COMPLETE PRODUCT CARD PARTIAL ===
store/templates/partials/product_card.html:

Show:
1. Product image — {{ product.image.url }} — CRITICAL for image display
   If no image: gradient placeholder with fa-box icon
2. Category badge (small, top-left)
3. AI badge if product_id in recommended_ids
4. Discount badge (% off) if is_on_discount
5. Product name (2-line clamp)
6. Star rating
7. Price with discount
8. Add to Cart (AJAX) + View buttons

IMAGE DISPLAY CODE:
{% if product.image %}
<img src="{{ product.image.url }}" alt="{{ product.name }}" 
     class="card-img-top" style="height:200px; object-fit:cover;">
{% else %}
<div class="card-placeholder d-flex align-items-center justify-content-center"
     style="height:200px; background:linear-gradient(135deg,#6C63FF22,#6C63FF44);">
  <i class="fas fa-box-open fa-3x" style="color:#6C63FF; opacity:0.5;"></i>
</div>
{% endif %}

WHY {{ product.image.url }} WORKS:
- Django ImageField auto-generates .url property
- .url = MEDIA_URL + field_value = '/media/products/filename.jpg'
- Django serves this from MEDIA_ROOT in development (via main urls.py static() config)
- In templates, ALWAYS use {{ product.image.url }} — NEVER hardcode paths

Write COMPLETE home.html with every section fully coded.
Beautiful, professional design. All Django template tags correct.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 9 — AUTH TEMPLATES (SIGNUP, LOGIN, PROFILE)
# ═══════════════════════════════════════════════════════════

```
You are a senior frontend developer. Create COMPLETE authentication templates.
Professional, modern design matching the AI Shop brand.

=== FILE: store/templates/auth/signup.html ===

{% extends 'base.html' %}
{% load static crispy_forms_tags %}

Design:
- Two-column layout:
  Left (40%): Gradient panel with AI Shop branding, benefits list
    * "Join AI Shop" heading
    * Benefits: ✅ AI Recommendations, ✅ Order Tracking, ✅ Exclusive Deals, ✅ Easy Returns
    * "Already have account? Login" link
  
  Right (60%): Signup form card
    * "Create Your Account" heading
    * Form using {{ form|crispy }} or manual Bootstrap fields
    * Name fields (first + last in one row)
    * Username, Email
    * Password fields
    * Phone Number (optional)
    * Profile Picture upload with preview
    * Subscription dropdown (Free/Premium)
    * Terms checkbox: "I agree to Terms and Privacy Policy"
    * Big "Create Account" button
    * OR divider + Google/Facebook social buttons (UI only, no backend needed)

JavaScript:
- Real-time password strength indicator (weak/medium/strong bar)
- Profile picture preview on file select
- Show/hide password toggle

=== FILE: store/templates/auth/login.html ===

Design:
- Centered card with max-width 480px
- AI Shop logo at top
- "Welcome Back!" heading
- Subtitle: "Your AI shopping assistant is waiting for you"
- Username field with person icon
- Password field with lock icon + show/hide toggle
- Remember Me checkbox
- Login button (full width, gradient)
- Forgot Password link
- "Don't have account? Sign Up" link
- Background: subtle gradient or pattern

=== FILE: store/templates/auth/profile.html ===

{% extends 'base.html' %}

Design:
- Two-column layout:
  
  Left sidebar (30%):
  - Profile picture (large circle) with upload hover effect
  - Username + full name
  - Member since date
  - Subscription badge (Free/Premium)
  - Quick stats: Orders ({{ total_orders }}), Reviews ({{ feedbacks_count }}), Spent (Rs. {{ total_spent }})
  - Navigation: Profile Info, Order History, My Recommendations, Security

  Right main area (70%):
  - "Profile Information" section
    * Editable form (first_name, last_name, email, phone, address, bio)
    * "Update Profile" button
  
  - "Recent Orders" section
    * Table: Order ID, Product, Amount, Status badge (colored by status), Date
    * "View All Orders" link
  
  - "My Preferences" section
    * Most viewed categories
    * Subscription upgrade CTA if on Free plan

Write COMPLETE HTML for all 3 files with Bootstrap 5 styling.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 10 — PRODUCT TEMPLATES
# (Product List, Product Detail, Category, Recommendations Page)
# ═══════════════════════════════════════════════════════════

```
You are a senior frontend developer + Django template expert.
Create COMPLETE product templates.

=== FILE: store/templates/products/product_list.html ===

{% extends 'base.html' %}

Design:
- Page header: "All Products ({{ total_count }} items)"
- 2-column layout:
  
  LEFT SIDEBAR (25%):
  - Search bar (form, GET method, q param)
  - "Filter by Category" — all categories as checkboxes/links with count
  - "Price Range" — min/max inputs with Apply button
  - "Sort By" — select dropdown
  - "Clear Filters" link if any filter is active
  
  RIGHT MAIN (75%):
  - Active filters display (pills with X to remove)
  - Product count text: "Showing X of Y products"
  - Grid: 3 per row desktop, 2 tablet, 1 mobile
  - Each: {% include 'partials/product_card.html' %}
  - Pagination at bottom

Empty state:
- If no products found: illustration + "No products found" + "Clear filters" button

=== FILE: store/templates/products/product_detail.html ===

{% extends 'base.html' %}

Design:
- Breadcrumb: Home > Category > Product Name
- Product detail section:
  
  LEFT (50%): Image gallery
  - Main large image
  - Image fallback: gradient placeholder
  - CORRECT image usage: <img src="{{ product.image.url }}" ...>
  - Discount badge overlay on image if on discount
  
  RIGHT (50%): Product info
  - Category badge
  - Product name (h1)
  - Star rating + "X reviews" link
  - Price section:
    * If on discount: crossed original + discounted price + "Save X%" badge
    * If not: just current price
  - Stock indicator: "In Stock (X remaining)" in green or "Out of Stock" in red
  - Add to Cart button (large, gradient, AJAX)
  - Place Order button
  - Share product icons
  - Product attributes (from JSON field):
    {% for key, value in product.attributes.items %}
    <span class="badge bg-light text-dark me-1">{{ key|title }}: {{ value }}</span>
    {% endfor %}
  - Category: link
  - Description (full text)

- "Rate This Product" section (only if purchased and not yet rated):
  - 5-star interactive rating
  - Comment textarea
  - Submit button

- User Reviews section:
  - Average rating display
  - List of feedbacks with user, stars, comment, date
  - Paginate if many reviews

- "More from [Category]" section:
  - 6 similar products grid
  - {% include 'partials/product_card.html' %}

- "Recommended For You" section (if logged in):
  - 4 personalized products

=== FILE: store/templates/products/category_products.html ===

{% extends 'base.html' %}

Design:
- Category hero banner (gradient background with category color):
  * Large category icon
  * Category name (h1)
  * Description
  * "{{ total_count }} products"

- 2-column layout (same as product_list but category is pre-selected)
  
  Left Sidebar:
  - "All Categories" list with active category highlighted in purple
  - Each shows: icon, name, product count badge
  - Price Range Filter
  - Sort By

  Right Main:
  - Product grid
  - Pagination

=== FILE: store/templates/products/recommendations.html ===

{% extends 'base.html' %}

Design:
- HERO SECTION (gradient purple-blue):
  * "🤖 Your AI Recommendations" h1
  * "Powered by Collaborative + Content-Based Machine Learning"
  * Stats row (4 cards):
    - {{ interaction_count }} Total Interactions
    - {{ products_viewed }} Products Viewed
    - {{ products_purchased }} Purchases Made
    - {{ total_recs }} AI Suggestions
  * "🔄 Refresh Recommendations" button (AJAX)

- HOW IT WORKS section:
  3 steps with icons:
  1. 👁️ You Browse — We track your interactions
  2. 🧠 AI Learns — ML analyzes your patterns
  3. 🎯 Personalized — You see perfect products

- RECOMMENDATIONS GRID:
  For each recommendation:
  - AI Match score progress bar (0-100%)
  - "Based on similar shoppers" / "Based on your history" reason text
  - Product image ({{ rec.product.image.url }})
  - Category, name, rating, price
  - "Add to Cart" + "View" buttons
  
  Empty state if no recs:
  - "🤖 Our AI needs more data!"
  - "Browse products to get personalized recommendations"
  - "Start Browsing" button

Write COMPLETE HTML for ALL 4 files. Include every Django template tag.
Professional, beautiful design matching AI Shop brand.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 11 — ORDER & FEEDBACK TEMPLATES
# ═══════════════════════════════════════════════════════════

```
You are a senior frontend developer. Create COMPLETE order and feedback templates.

=== FILE: store/templates/orders/cart.html ===

{% extends 'base.html' %}

Design:
- Page title: "Your Shopping Cart ({{ total_items }} items)"
- Two-column:
  
  Left (65%): Cart Items Table
  - For each item in cart_items:
    * Product image ({{ item.image_url }} from session data OR re-fetch from DB)
    * Product name + category
    * Unit price
    * Quantity controls (- button, number, + button) — AJAX update
    * Total for this item
    * Remove button (×)
  - If cart empty: "Your cart is empty" with shopping illustration + "Continue Shopping" button

  Right (35%): Order Summary Card
  - Subtotal
  - Discount if any
  - Delivery fee (Free if > 2000)
  - TOTAL (big, bold)
  - "Proceed to Checkout" button
  - "Continue Shopping" link
  - Security badges (SSL, Secure Payment)

=== FILE: store/templates/orders/place_order.html ===

{% extends 'base.html' %}

Design:
- Progress bar: Cart → Delivery Details → Order Placed ✅
- Two-column:
  
  Left (60%): Delivery Details Form
  - {{ form|crispy }} or manual Bootstrap form
  - Delivery Address (textarea)
  - City dropdown (major Pakistani cities)
  - Phone Number
  - Special Notes (optional)
  - Map icon suggesting "Detect My Location" (UI only)

  Right (40%): Order Summary Card
  - Product image ({{ product.image.url }})
  - Product name
  - Category
  - Unit price
  - Quantity selector
  - Calculated total
  - Expected delivery: 3-5 business days
  - "Place Order" button (big, green gradient)

=== FILE: store/templates/orders/order_history.html ===

{% extends 'base.html' %}

Design:
- Page title: "My Orders"
- Summary stats: Total Orders, Total Spent, Pending Orders
- Responsive table OR card list:
  
  For each order:
  - Order ID badge
  - Product image (thumbnail) + name + category
  - Quantity × Unit Price = Total
  - Delivery address (truncated)
  - Status badge: 
    * pending = yellow/warning
    * confirmed = blue
    * processing = orange
    * shipped = purple
    * delivered = green
    * cancelled = red
  - Date placed
  - Actions: "Leave Review" (if delivered, no review yet)

Empty state: "No orders yet" + "Start Shopping" button

=== FILE: store/templates/feedback/submit_feedback.html ===

{% extends 'base.html' %}

Design:
- Product summary card at top: image, name, what you ordered
- Review form:
  * STAR RATING: 5 large interactive stars
    - CSS/JS: stars fill yellow on hover + on click
    - Selected rating stored in hidden input
  * Review title (optional text input)
  * Comment (large textarea)
  * "Submit Review" button
- Note: "Your review helps other shoppers make better decisions"
- Existing review display if user already reviewed

=== FILE: store/templates/partials/pagination.html ===

Reusable pagination:
{% if page_obj.has_other_pages %}
<nav class="mt-4">
  <ul class="pagination justify-content-center">
    {% if page_obj.has_previous %}
    <li class="page-item">
      <a class="page-link" href="?page={{ page_obj.previous_page_number }}{% if request.GET.sort_by %}&sort_by={{ request.GET.sort_by }}{% endif %}">Previous</a>
    </li>
    {% endif %}
    {% for num in page_obj.paginator.page_range %}
    <li class="page-item {% if page_obj.number == num %}active{% endif %}">
      <a class="page-link" href="?page={{ num }}">{{ num }}</a>
    </li>
    {% endfor %}
    {% if page_obj.has_next %}
    <li class="page-item">
      <a class="page-link" href="?page={{ page_obj.next_page_number }}">Next</a>
    </li>
    {% endif %}
  </ul>
</nav>
{% endif %}

Write COMPLETE HTML for ALL files. Professional design.
```

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 12 — ADMIN DASHBOARD TEMPLATES
# ═══════════════════════════════════════════════════════════

```
You are a senior frontend developer. Create a COMPLETE custom admin dashboard.
This is SEPARATE from Django's built-in /django-admin/ panel.

=== FILE: store/templates/admin_panel/dashboard.html ===

{% extends 'base.html' %}

Design: Professional admin dashboard

SIDEBAR (fixed left, 250px):
- AI Shop Admin logo
- Navigation items with icons:
  📊 Dashboard (active)
  📦 Products
  👥 Users
  📋 Orders
  💬 Feedback
  📈 Analytics
  ⚙️ Settings
- Admin profile at bottom

MAIN CONTENT:

1. STATS ROW (4 cards):
   - 💰 Total Revenue: Rs. {{ total_revenue|floatformat:0 }}
   - 📦 Total Products: {{ total_products }}
   - 👥 Total Users: {{ total_users }}
   - 📋 Total Orders: {{ total_orders }}
   Each card with: icon, value (big), label, % change from last month (green/red)

2. CHARTS ROW (2 columns):
   - Monthly Revenue Chart (line chart using Chart.js CDN)
     Data: last 6 months revenue
   - Orders by Status (pie/donut chart using Chart.js)
     Data: pending, confirmed, shipped, delivered counts

3. RECENT ORDERS TABLE:
   Columns: Order ID, Customer, Product, Amount, Status, Date, Actions
   Status badges with colors
   Actions: View, Update Status

4. TOP PRODUCTS (by order count):
   Small table: rank, product name, category, orders count, revenue generated

5. QUICK ACTIONS BAR:
   - ➕ Add New Product
   - 📊 Generate Report
   - 🤖 Regenerate All Recommendations
   - 📧 Send Newsletter (UI only)

=== FILE: store/templates/admin_panel/product_form.html ===

{% extends 'admin_panel/base_admin.html' or extends 'base.html' %}

Design: Two-column product form

Left Column:
- Product Name
- Category (select)
- Description (textarea)
- Attributes JSON (textarea with syntax helper)
- Status checkboxes: Is Available, Is Featured, Is On Discount

Right Column:
- Price
- Original Price
- Discount Percentage (hidden unless Is On Discount checked)
- Stock Level
- Image Upload:
  * Preview area (shows current image or placeholder)
  * File input
  * JavaScript preview on select

Bottom: Submit + Cancel buttons

JavaScript:
- Image preview on file select
- Show/hide discount field based on checkbox
- JSON attributes validation (try JSON.parse)

=== FILE: store/templates/admin_panel/user_management.html ===

User list table:
- Search box
- Columns: ID, Username, Email, Subscription, Orders, Joined Date, Active, Actions
- Action buttons: View, Edit, Block/Unblock
- Pagination

=== FILE: store/templates/admin_panel/analytics.html ===

Analytics page:
1. Date range picker (last 7 days / 30 days / 90 days / custom)
2. Revenue trend (line chart)
3. Top 10 products by revenue (horizontal bar chart)
4. User engagement: views, cart adds, purchases (grouped bar chart)
5. Category performance (pie chart)
6. AI Recommendation click-through stats (if tracked)
7. Export as CSV button

All charts use Chart.js (CDN). Pass data from views as JSON:
<script>
const revenueData = {{ revenue_data|safe }};
const topProducts = {{ top_products_data|safe }};
</script>

Write COMPLETE HTML for ALL admin templates. Professional, clean admin UI.
```

---

# ═══════════════════════════════════════════════
# PROMPT 13 (UPDATED) — AMAZON-LIKE UI/CSS/JS
# ═══════════════════════════════════════════════

```
You are an expert Frontend Developer. Update and rewrite the complete CSS and JavaScript
for an AI-powered e-commerce platform that looks and feels like Amazon.com — 
professional, fast, clean, and data-rich.

## FILE 1: store/static/css/style.css — COMPLETE REWRITE

### Amazon-Inspired Design System:

:root {
  /* Amazon Colors */
  --amazon-orange: #FF9900;
  --amazon-orange-dark: #E68A00;
  --amazon-navy: #131921;
  --amazon-navy-light: #232F3E;
  --amazon-blue: #146EB4;
  --amazon-blue-light: #007BFF;
  --amazon-green: #007600;
  --amazon-red: #CC0C39;
  --amazon-yellow: #F0C040;
  --amazon-gray: #F3F3F3;
  --amazon-border: #DDDDDD;
  --amazon-text: #0F1111;
  --amazon-text-secondary: #565959;
  --amazon-link: #007185;
  --amazon-link-hover: #C7511F;
  
  /* AI/Purple Accent (your brand color, keep this for AI sections) */
  --ai-purple: #6C63FF;
  --ai-purple-light: #f0eeff;
  
  /* Spacing */
  --card-radius: 8px;
  --transition: all 0.2s ease;
}

/* ===== GLOBAL ===== */
* { box-sizing: border-box; }
body {
  font-family: 'Amazon Ember', 'Segoe UI', Arial, sans-serif;
  font-size: 14px;
  color: var(--amazon-text);
  background: var(--amazon-gray);
  line-height: 1.5;
}
a { color: var(--amazon-link); text-decoration: none; }
a:hover { color: var(--amazon-link-hover); text-decoration: underline; }

/* ===== TOP NAVBAR (Amazon-style 3-layer) ===== */
.navbar-top {
  background: var(--amazon-navy);
  padding: 8px 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}
.navbar-logo { color: white; font-size: 1.6rem; font-weight: 800; letter-spacing: -1px; }
.navbar-logo span { color: var(--amazon-orange); }
.navbar-search-bar {
  display: flex;
  flex: 1;
  max-width: 680px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  border: 2px solid var(--amazon-orange);
}
.navbar-search-bar select {
  background: #f3f3f3;
  border: none;
  padding: 0 8px;
  font-size: 12px;
  color: #555;
  cursor: pointer;
  border-right: 1px solid #cdcdcd;
  min-width: 60px;
}
.navbar-search-bar input {
  flex: 1;
  border: none;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}
.navbar-search-bar button {
  background: var(--amazon-orange);
  border: none;
  width: 45px;
  cursor: pointer;
  font-size: 16px;
  color: var(--amazon-navy);
}
.navbar-search-bar button:hover { background: var(--amazon-orange-dark); }
.navbar-top-links { display: flex; align-items: center; gap: 16px; }
.navbar-top-link {
  color: white;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 3px;
  border: 1px solid transparent;
}
.navbar-top-link:hover { border-color: white; color: white; text-decoration: none; }
.navbar-top-link .nav-line1 { font-size: 11px; color: #ccc; display: block; }
.navbar-top-link .nav-line2 { font-size: 13px; font-weight: 700; display: block; }
.cart-link { position: relative; }
.cart-count-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--amazon-orange);
  color: var(--amazon-navy);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Navbar Sub-bar (categories bar) */
.navbar-subbar {
  background: var(--amazon-navy-light);
  padding: 6px 0;
  overflow-x: auto;
  white-space: nowrap;
}
.navbar-subbar::-webkit-scrollbar { height: 0; }
.navbar-subbar a {
  color: white;
  padding: 4px 10px;
  font-size: 13px;
  display: inline-block;
  border-radius: 3px;
  border: 1px solid transparent;
}
.navbar-subbar a:hover {
  border-color: white;
  text-decoration: none;
}

/* ===== MESSAGES ===== */
.messages-container { position: fixed; top: 70px; right: 20px; z-index: 9999; max-width: 350px; }
.alert { border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); font-size: 13px; }

/* ===== HERO BANNER (Amazon Carousel Style) ===== */
.hero-carousel { position: relative; overflow: hidden; }
.hero-slide {
  min-height: 400px;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
}
.hero-gradient-1 { background: linear-gradient(135deg, #131921 0%, #1a3a5c 50%, #146EB4 100%); }
.hero-gradient-2 { background: linear-gradient(135deg, #1a0533 0%, #4a0080 50%, #6C63FF 100%); }
.hero-gradient-3 { background: linear-gradient(135deg, #0d2137 0%, #c7511f 100%); }
.hero-content { padding: 40px; }
.hero-badge { background: var(--amazon-orange); color: black; padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; display: inline-block; margin-bottom: 12px; }
.hero-title { font-size: 2.4rem; font-weight: 800; color: white; line-height: 1.2; }
.hero-subtitle { font-size: 1rem; color: rgba(255,255,255,0.85); margin: 10px 0 20px; }
.btn-hero { background: var(--amazon-orange); color: var(--amazon-navy); font-weight: 700; border: none; padding: 12px 28px; border-radius: 4px; font-size: 15px; cursor: pointer; }
.btn-hero:hover { background: var(--amazon-orange-dark); }

/* ===== PRODUCT CARDS (Amazon style) ===== */
.product-card {
  background: white;
  border: 1px solid var(--amazon-border);
  border-radius: var(--card-radius);
  overflow: hidden;
  transition: var(--transition);
  height: 100%;
}
.product-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}
.product-card-img {
  width: 100%;
  height: 200px;
  object-fit: contain;
  padding: 16px;
  background: white;
}
.product-card-img-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f8f8;
  font-size: 3rem;
  color: #ccc;
}
.product-card-body { padding: 12px; }
.product-card-title {
  font-size: 14px;
  font-weight: 400;
  color: var(--amazon-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  min-height: 40px;
}
.product-card-brand { font-size: 12px; color: var(--amazon-text-secondary); }
.star-rating { color: var(--amazon-orange); font-size: 13px; }
.star-rating .rating-count { color: var(--amazon-link); font-size: 12px; }
.product-card-price { margin: 6px 0; }
.price-symbol { font-size: 13px; vertical-align: top; line-height: 24px; }
.price-whole { font-size: 22px; font-weight: 700; color: #0F1111; }
.price-fraction { font-size: 13px; vertical-align: top; line-height: 24px; }
.price-original { font-size: 12px; color: var(--amazon-text-secondary); text-decoration: line-through; }
.price-savings { color: var(--amazon-red); font-size: 13px; }
.price-discount-badge { color: var(--amazon-red); font-weight: 700; font-size: 13px; }
.badge-bestseller { background: var(--amazon-orange); color: black; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 2px; }
.badge-new { background: var(--amazon-green); color: white; font-size: 10px; padding: 2px 8px; border-radius: 2px; }
.badge-ai { background: var(--ai-purple); color: white; font-size: 10px; padding: 2px 8px; border-radius: 2px; }
.btn-add-cart {
  background: var(--amazon-orange);
  border: none;
  width: 100%;
  padding: 8px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--amazon-navy);
  cursor: pointer;
  transition: var(--transition);
}
.btn-add-cart:hover { background: var(--amazon-orange-dark); }
.btn-buy-now {
  background: #FFD814;
  border: none;
  width: 100%;
  padding: 8px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--amazon-navy);
  cursor: pointer;
  margin-top: 6px;
}
.btn-buy-now:hover { background: #F7CA00; }
.prime-badge { color: var(--amazon-blue); font-size: 11px; font-weight: 700; }
.free-delivery { color: var(--amazon-link); font-size: 12px; }

/* ===== CATEGORY CARDS ===== */
.category-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid var(--amazon-border);
}
.category-card:hover { box-shadow: 0 4px 15px rgba(0,0,0,0.12); transform: translateY(-3px); }
.category-icon { font-size: 2.5rem; margin-bottom: 8px; }
.category-name { font-size: 13px; font-weight: 700; color: var(--amazon-text); }
.category-count { font-size: 11px; color: var(--amazon-text-secondary); }

/* ===== SECTION HEADERS ===== */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0 8px;
  border-bottom: 2px solid var(--amazon-orange);
  margin-bottom: 16px;
}
.section-title { font-size: 20px; font-weight: 700; color: var(--amazon-text); margin: 0; }
.section-see-all { color: var(--amazon-link); font-size: 13px; }
.section-see-all:hover { color: var(--amazon-link-hover); }

/* ===== PRODUCT DETAIL PAGE ===== */
.product-detail-img-main {
  max-height: 450px;
  width: 100%;
  object-fit: contain;
  padding: 20px;
  border: 1px solid var(--amazon-border);
  border-radius: 8px;
  background: white;
}
.product-detail-price { font-size: 28px; font-weight: 400; color: #0F1111; }
.product-detail-price .rs { font-size: 18px; }
.in-stock-badge { color: var(--amazon-green); font-weight: 700; font-size: 18px; }
.out-of-stock-badge { color: var(--amazon-red); font-weight: 700; }
.buy-box {
  border: 1px solid var(--amazon-border);
  border-radius: 8px;
  padding: 20px;
  background: white;
}

/* ===== DISCOUNT TIMER ===== */
.discount-timer-bar {
  background: var(--amazon-red);
  color: white;
  text-align: center;
  padding: 10px;
  font-weight: 700;
  font-size: 14px;
}
.timer-digits {
  background: var(--amazon-navy);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 16px;
  margin: 0 4px;
}

/* ===== AI RECOMMENDATION SECTION ===== */
.ai-section {
  background: var(--ai-purple-light);
  border-left: 4px solid var(--ai-purple);
  border-radius: 0 8px 8px 0;
  padding: 20px;
  margin: 20px 0;
}
.ai-section-title { color: var(--ai-purple); font-weight: 700; font-size: 18px; }
.ai-score-bar { height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden; }
.ai-score-fill { height: 100%; background: linear-gradient(90deg, var(--ai-purple), #43B89C); border-radius: 3px; }
.ai-reason-tag { background: var(--ai-purple); color: white; font-size: 10px; padding: 2px 8px; border-radius: 10px; }

/* ===== CART ===== */
.cart-item { border-bottom: 1px solid var(--amazon-border); padding: 16px 0; }
.cart-item img { width: 120px; height: 120px; object-fit: contain; border: 1px solid var(--amazon-border); padding: 8px; border-radius: 4px; }
.cart-summary-box { border: 1px solid var(--amazon-border); border-radius: 8px; padding: 20px; background: white; }
.cart-total { font-size: 18px; font-weight: 400; }
.cart-total span { font-size: 20px; font-weight: 700; }

/* ===== ADMIN PANEL ===== */
.admin-sidebar {
  background: var(--amazon-navy);
  min-height: 100vh;
  width: 240px;
  position: fixed;
  left: 0;
  top: 0;
  padding-top: 20px;
  overflow-y: auto;
}
.admin-sidebar .brand { color: white; font-size: 18px; font-weight: 800; padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.1); display: block; }
.admin-sidebar .brand span { color: var(--amazon-orange); }
.admin-sidebar a { display: flex; align-items: center; gap: 10px; color: rgba(255,255,255,0.8); padding: 12px 20px; font-size: 13px; transition: var(--transition); }
.admin-sidebar a:hover, .admin-sidebar a.active { background: rgba(255,255,255,0.1); color: white; text-decoration: none; border-left: 3px solid var(--amazon-orange); }
.admin-sidebar a i { width: 20px; text-align: center; }
.admin-content { margin-left: 240px; padding: 24px; min-height: 100vh; background: #f5f5f5; }
.kpi-card { background: white; border-radius: 8px; padding: 20px; border-left: 4px solid var(--amazon-orange); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.kpi-number { font-size: 2rem; font-weight: 800; color: var(--amazon-text); }
.kpi-label { color: var(--amazon-text-secondary); font-size: 13px; }
.kpi-trend { font-size: 12px; color: var(--amazon-green); }

/* ===== FORMS ===== */
.auth-card { max-width: 450px; margin: 40px auto; background: white; border-radius: 8px; border: 1px solid var(--amazon-border); padding: 30px; }
.auth-title { font-size: 26px; font-weight: 400; margin-bottom: 20px; }
.form-input {
  width: 100%;
  border: 1px solid #a6a6a6;
  border-radius: 3px;
  padding: 8px 10px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
}
.form-input:focus { border-color: var(--amazon-orange); box-shadow: 0 0 0 3px rgba(255,153,0,0.3); }
.form-label { font-size: 13px; font-weight: 700; color: #111; display: block; margin-bottom: 4px; }
.btn-amazon-primary {
  background: linear-gradient(to bottom, #f7dfa5, #f0c14b);
  border: 1px solid #a88734;
  border-radius: 3px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 400;
  color: #111;
  cursor: pointer;
  width: 100%;
}
.btn-amazon-primary:hover { background: linear-gradient(to bottom, #f5d78e, #eeb933); }

/* ===== STAR RATING (Interactive) ===== */
.star-interactive { display: flex; flex-direction: row-reverse; gap: 4px; }
.star-interactive input { display: none; }
.star-interactive label { font-size: 28px; color: #ddd; cursor: pointer; transition: color 0.1s; }
.star-interactive input:checked ~ label,
.star-interactive label:hover,
.star-interactive label:hover ~ label { color: var(--amazon-orange); }

/* ===== LOADING SKELETON ===== */
.skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: skeleton-loading 1.5s infinite; border-radius: 4px; }
@keyframes skeleton-loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.skeleton-img { height: 200px; margin-bottom: 10px; }
.skeleton-text { height: 14px; margin: 6px 0; }
.skeleton-text.short { width: 60%; }
.skeleton-price { height: 22px; width: 80px; }

/* ===== ANIMATIONS ===== */
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-in-up { animation: fadeInUp 0.4s ease; }
@keyframes pulse-orange { 0%, 100% { box-shadow: 0 0 0 0 rgba(255,153,0,0.4); } 50% { box-shadow: 0 0 0 10px rgba(255,153,0,0); } }
.pulse-orange { animation: pulse-orange 2s infinite; }
@keyframes success-checkmark { 0% { transform: scale(0); } 50% { transform: scale(1.2); } 100% { transform: scale(1); } }
.success-checkmark { animation: success-checkmark 0.5s ease; }

/* ===== BREADCRUMB ===== */
.breadcrumb { background: none; padding: 8px 0; font-size: 13px; }
.breadcrumb-item a { color: var(--amazon-link); }
.breadcrumb-item.active { color: var(--amazon-text-secondary); }
.breadcrumb-item + .breadcrumb-item::before { content: "›"; color: var(--amazon-text-secondary); }

/* ===== FILTER SIDEBAR ===== */
.filter-sidebar { background: white; border: 1px solid var(--amazon-border); border-radius: 8px; padding: 16px; }
.filter-title { font-size: 14px; font-weight: 700; border-bottom: 1px solid var(--amazon-border); padding-bottom: 8px; margin-bottom: 12px; }
.filter-item { font-size: 13px; display: flex; align-items: center; gap: 8px; padding: 4px 0; cursor: pointer; }
.filter-item input { accent-color: var(--amazon-orange); }
.price-range-slider { accent-color: var(--amazon-orange); width: 100%; }

/* ===== FOOTER ===== */
.footer-links-bar { background: #37475A; padding: 16px 0; }
.footer-links-bar a { color: white; font-size: 13px; padding: 0 12px; border-right: 1px solid rgba(255,255,255,0.3); }
.footer-main { background: #232F3E; padding: 32px 0; }
.footer-col-title { color: white; font-weight: 700; font-size: 14px; margin-bottom: 12px; }
.footer-col a { display: block; color: #DDD; font-size: 13px; margin-bottom: 6px; }
.footer-col a:hover { color: white; text-decoration: underline; }
.footer-bottom { background: #131921; padding: 16px 0; text-align: center; }
.footer-bottom p { color: #999; font-size: 12px; margin: 0; }

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .navbar-search-bar { max-width: 100%; order: 3; width: 100%; margin-top: 8px; }
  .hero-title { font-size: 1.6rem; }
  .admin-sidebar { display: none; }
  .admin-content { margin-left: 0; }
  .product-card-img { height: 150px; }
}

/* ===== UTILITY ===== */
.text-orange { color: var(--amazon-orange); }
.text-ai { color: var(--ai-purple); }
.bg-ai { background: var(--ai-purple-light); }
.divider { border-top: 1px solid var(--amazon-border); margin: 16px 0; }
.rounded-pill-sm { border-radius: 20px; }
.shadow-sm-custom { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.cursor-pointer { cursor: pointer; }
.truncate-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.section-bg-white { background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; border: 1px solid var(--amazon-border); }

Write COMPLETE CSS file — every rule above fully implemented. No shortcuts.

---

## FILE 2: store/static/js/main.js — COMPLETE REWRITE (Amazon-like behavior)

Write complete JavaScript file with:

### 1. Cart System (localStorage based like Amazon):
```javascript
const Cart = {
  data: JSON.parse(localStorage.getItem('aiShopCart') || '{}'),
  
  add(productId, quantity = 1) {
    if (this.data[productId]) {
      this.data[productId].qty += quantity;
    } else {
      this.data[productId] = { qty: quantity };
    }
    this.save();
    this.updateBadge();
    // Sync with server
    fetch(`/cart/add/${productId}/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity })
    }).then(r => r.json()).then(data => {
      this.showAddedAnimation(productId);
      Toast.show(`Added to Cart! (${this.count()} items)`, 'success');
    });
  },
  
  remove(productId) {
    delete this.data[productId];
    this.save();
    this.updateBadge();
  },
  
  count() {
    return Object.values(this.data).reduce((sum, item) => sum + item.qty, 0);
  },
  
  save() {
    localStorage.setItem('aiShopCart', JSON.stringify(this.data));
  },
  
  updateBadge() {
    const badge = document.getElementById('cart-count-badge');
    if (badge) {
      badge.textContent = this.count();
      badge.style.display = this.count() > 0 ? 'flex' : 'none';
    }
  },
  
  showAddedAnimation(productId) {
    const btn = document.querySelector(`[data-product-id="${productId}"] .btn-add-cart`);
    if (btn) {
      const orig = btn.textContent;
      btn.textContent = '✓ Added!';
      btn.style.background = '#007600';
      btn.style.color = 'white';
      setTimeout(() => {
        btn.textContent = orig;
        btn.style.background = '';
        btn.style.color = '';
      }, 1500);
    }
  }
};

// Initialize on page load
Cart.updateBadge();
```

### 2. Toast Notification (Amazon-style):
```javascript
const Toast = {
  show(message, type = 'success', duration = 3000) {
    const container = document.getElementById('toast-container') || (() => {
      const c = document.createElement('div');
      c.id = 'toast-container';
      c.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;max-width:350px;';
      document.body.appendChild(c);
      return c;
    })();
    
    const colors = { success: '#007600', error: '#CC0C39', warning: '#FF9900', info: '#146EB4' };
    const icons = { success: '✓', error: '✗', warning: '⚠', info: 'ℹ' };
    
    const toast = document.createElement('div');
    toast.style.cssText = `
      background: white;
      border-left: 4px solid ${colors[type]};
      border-radius: 4px;
      padding: 12px 16px;
      margin-bottom: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.2);
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 10px;
      animation: fadeInRight 0.3s ease;
    `;
    toast.innerHTML = `
      <span style="color:${colors[type]};font-size:16px;font-weight:700;">${icons[type]}</span>
      <span>${message}</span>
      <button onclick="this.parentElement.remove()" style="margin-left:auto;border:none;background:none;cursor:pointer;color:#999;font-size:16px;">×</button>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.style.animation = 'fadeOut 0.3s ease forwards', duration - 300);
    setTimeout(() => toast.remove(), duration);
  }
};
```

### 3. Search Autocomplete (Amazon-style):
```javascript
const SearchAutocomplete = {
  init() {
    const input = document.getElementById('main-search-input');
    if (!input) return;
    
    let timeout;
    input.addEventListener('input', (e) => {
      clearTimeout(timeout);
      const q = e.target.value.trim();
      if (q.length < 2) { this.hide(); return; }
      timeout = setTimeout(() => this.search(q), 300);
    });
    
    document.addEventListener('click', (e) => {
      if (!input.contains(e.target)) this.hide();
    });
  },
  
  search(query) {
    fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
      .then(r => r.json())
      .then(data => this.show(data.suggestions))
      .catch(() => {});
  },
  
  show(suggestions) {
    this.hide();
    if (!suggestions.length) return;
    
    const dropdown = document.createElement('div');
    dropdown.id = 'search-dropdown';
    dropdown.style.cssText = `
      position: absolute;
      background: white;
      border: 1px solid #a6a6a6;
      border-top: none;
      width: 100%;
      z-index: 9999;
      box-shadow: 0 4px 8px rgba(0,0,0,0.2);
      border-radius: 0 0 4px 4px;
    `;
    
    suggestions.forEach(s => {
      const item = document.createElement('div');
      item.style.cssText = 'padding: 8px 12px; cursor: pointer; font-size: 13px; display:flex; align-items:center; gap:10px;';
      item.innerHTML = `<i class="fas fa-search" style="color:#999;font-size:11px;"></i> ${s.name}`;
      item.addEventListener('mouseenter', () => item.style.background = '#f5f5f5');
      item.addEventListener('mouseleave', () => item.style.background = 'white');
      item.addEventListener('click', () => {
        window.location.href = `/products/?query=${encodeURIComponent(s.name)}`;
      });
      dropdown.appendChild(item);
    });
    
    const searchBar = document.querySelector('.navbar-search-bar');
    if (searchBar) {
      searchBar.style.position = 'relative';
      searchBar.appendChild(dropdown);
    }
  },
  
  hide() {
    const d = document.getElementById('search-dropdown');
    if (d) d.remove();
  }
};
SearchAutocomplete.init();
```

### 4. Product Image Zoom (Amazon-style):
```javascript
function initImageZoom() {
  const img = document.getElementById('product-main-img');
  if (!img) return;
  
  const lens = document.createElement('div');
  lens.style.cssText = 'position:absolute;border:2px solid #FF9900;width:100px;height:100px;display:none;pointer-events:none;';
  img.parentElement.style.position = 'relative';
  img.parentElement.appendChild(lens);
  
  img.addEventListener('mousemove', (e) => {
    const rect = img.getBoundingClientRect();
    const x = e.clientX - rect.left - 50;
    const y = e.clientY - rect.top - 50;
    lens.style.left = Math.max(0, Math.min(x, img.width - 100)) + 'px';
    lens.style.top = Math.max(0, Math.min(y, img.height - 100)) + 'px';
    lens.style.display = 'block';
  });
  
  img.addEventListener('mouseleave', () => lens.style.display = 'none');
}
initImageZoom();
```

### 5. Interaction Tracking (background, silent):
```javascript
function trackInteraction(productId, type) {
  if (!window.userIsAuthenticated) return;
  fetch('/track/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
    body: JSON.stringify({ product_id: productId, interaction_type: type })
  }).catch(() => {}); // Silent fail — tracking should never break UX
}

// Auto-track visible products using Intersection Observer
const productObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const productId = entry.target.dataset.productId;
      if (productId) {
        trackInteraction(productId, 'view');
        productObserver.unobserve(entry.target);
      }
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-product-id]').forEach(el => productObserver.observe(el));
```

### 6. Countdown Timer (for discount banners):
```javascript
function startCountdown(endTimeISO, elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  
  function update() {
    const now = new Date();
    const end = new Date(endTimeISO);
    const diff = end - now;
    
    if (diff <= 0) {
      el.innerHTML = '<span style="color:#fff;">Offer Ended</span>';
      return;
    }
    
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    
    el.innerHTML = `
      <span class="timer-digits">${String(h).padStart(2,'0')}</span>h
      <span class="timer-digits">${String(m).padStart(2,'0')}</span>m
      <span class="timer-digits">${String(s).padStart(2,'0')}</span>s
    `;
  }
  
  update();
  setInterval(update, 1000);
}
```

### 7. Star Rating Input:
```javascript
function initStarRating() {
  document.querySelectorAll('.star-rating-input').forEach(container => {
    const stars = container.querySelectorAll('label');
    const input = container.querySelector('input[type="hidden"]');
    
    stars.forEach((star, i) => {
      star.addEventListener('click', () => {
        if (input) input.value = 5 - i;
      });
    });
  });
}
initStarRating();
```

### 8. CSRF Helper:
```javascript
function getCsrfToken() {
  const el = document.querySelector('[name=csrfmiddlewaretoken]');
  return el ? el.value : '';
}
```

### 9. Loading Skeleton:
```javascript
function showProductSkeletons(containerId, count = 4) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  container.innerHTML = Array(count).fill(`
    <div class="col-lg-3 col-md-4 col-6">
      <div class="product-card p-3">
        <div class="skeleton skeleton-img"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text short"></div>
        <div class="skeleton skeleton-price"></div>
      </div>
    </div>
  `).join('');
}
```

Write COMPLETE, production-ready JavaScript. Include all above functions.
Use vanilla JS only (no jQuery). ES6+ modern syntax. Well commented.
```

---

---

# ═══════════════════════════════════════════════
# PROMPT 14 (NEW) — AMAZON-SCALE REAL-WORLD DATA
# (500,000 Products, Amazon-like categories, real data)
# ═══════════════════════════════════════════════

```
You are an expert Django developer and data engineer.
I need a COMPLETE database seeding system that creates Amazon-scale real-world product data
for an e-commerce platform — up to 500,000 products with realistic names, prices, descriptions, 
categories, interactions, and orders.

## REQUIREMENTS:
- pip install Faker (for realistic data generation)
- Products should look like REAL Amazon products
- Categories should match Amazon's main categories
- Prices in Pakistani Rupees (PKR) — realistic market prices
- Fast bulk insertion (use bulk_create for speed)
- Progress bar showing generation progress

---

## FILE 1: requirements.txt — ADD these packages:
Faker==21.0.0
tqdm==4.66.1
(add to existing requirements.txt)

---

## FILE 2: store/management/commands/seed_database.py

### COMPLETE CODE:

```python
"""
Amazon-Scale Database Seeder
Usage:
    python manage.py seed_database --products 500000
    python manage.py seed_database --products 1000 (quick test)
    python manage.py seed_database (default: 50000 products)

Inserts REAL-WORLD style data:
  - Amazon-like categories
  - Realistic Pakistani product names + prices
  - Authentic product descriptions
  - Proper user interaction data for ML training
"""

import random
import json
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from faker import Faker

fake = Faker(['en_US'])

# ═══════════════════════════════════════════════════════════════
# REAL-WORLD AMAZON-LIKE PRODUCT CATALOG
# 20 Main Categories with real sub-categories and brands
# ═══════════════════════════════════════════════════════════════

PRODUCT_CATALOG = {
    "Electronics": {
        "icon": "fa-laptop",
        "slug": "electronics",
        "color": "#0066CC",
        "subcategories": ["Mobiles", "Laptops", "Tablets", "Cameras", "Smart Watches", "Headphones", "Speakers", "TVs", "Gaming"],
        "products": [
            # Mobiles
            {"name": "Samsung Galaxy S24 Ultra", "brand": "Samsung", "price_pkr": (289000, 349000), "desc": "6.8-inch Dynamic AMOLED 2X display, 200MP camera, S Pen included, 5000mAh battery, titanium frame"},
            {"name": "Samsung Galaxy A54 5G", "brand": "Samsung", "price_pkr": (89000, 115000), "desc": "6.4-inch Super AMOLED, 50MP triple camera, 5000mAh battery, IP67 water resistant"},
            {"name": "Samsung Galaxy S23 FE", "brand": "Samsung", "price_pkr": (105000, 130000), "desc": "6.4-inch Dynamic AMOLED, Snapdragon 8 Gen 1, 50MP camera, 4500mAh battery"},
            {"name": "iPhone 15 Pro Max", "brand": "Apple", "price_pkr": (399000, 459000), "desc": "6.7-inch Super Retina XDR OLED, A17 Pro chip, 48MP main camera with 5x optical zoom, titanium design"},
            {"name": "iPhone 15", "brand": "Apple", "price_pkr": (219000, 260000), "desc": "6.1-inch Super Retina XDR, A16 Bionic chip, 48MP main camera, Dynamic Island, USB-C connector"},
            {"name": "iPhone 14", "brand": "Apple", "price_pkr": (179000, 205000), "desc": "6.1-inch Super Retina XDR display, A15 Bionic chip, 12MP dual camera, Crash Detection"},
            {"name": "Xiaomi 14 Ultra", "brand": "Xiaomi", "price_pkr": (195000, 235000), "desc": "6.73-inch LTPO AMOLED, Snapdragon 8 Gen 3, Leica 1-inch optical sensor, 5000mAh 90W charging"},
            {"name": "Xiaomi Redmi Note 13 Pro+", "brand": "Xiaomi", "price_pkr": (65000, 82000), "desc": "6.67-inch AMOLED 120Hz, 200MP HyperOS camera, 5000mAh 120W HyperCharge"},
            {"name": "Xiaomi Redmi 13C", "brand": "Xiaomi", "price_pkr": (28000, 36000), "desc": "6.74-inch IPS LCD, Helio G85, 50MP AI triple camera, 5000mAh battery"},
            {"name": "OnePlus 12", "brand": "OnePlus", "price_pkr": (175000, 215000), "desc": "6.82-inch LTPO3 AMOLED, Snapdragon 8 Gen 3, Hasselblad 50MP triple camera, 5400mAh 100W SUPERVOOC"},
            {"name": "OnePlus Nord CE 3 Lite", "brand": "OnePlus", "price_pkr": (52000, 65000), "desc": "6.72-inch IPS LCD 120Hz, Snapdragon 695, 108MP triple camera, 5000mAh 67W fast charge"},
            {"name": "Oppo Reno 11 Pro", "brand": "Oppo", "price_pkr": (89000, 108000), "desc": "6.74-inch AMOLED 120Hz, MediaTek Dimensity 8200, 50MP triple camera, 4600mAh 80W"},
            {"name": "Vivo Y100", "brand": "Vivo", "price_pkr": (55000, 70000), "desc": "6.67-inch AMOLED 120Hz, Snapdragon 695, 64MP triple camera, 4600mAh 44W FlashCharge"},
            {"name": "Google Pixel 8 Pro", "brand": "Google", "price_pkr": (245000, 290000), "desc": "6.7-inch LTPO OLED, Google Tensor G3, 50MP triple camera, 7 years Android updates, 5050mAh"},
            {"name": "Infinix Hot 40 Pro", "brand": "Infinix", "price_pkr": (38000, 48000), "desc": "6.78-inch AMOLED 120Hz, Helio G99, 108MP main camera, 5000mAh 45W fast charge"},
            # Laptops
            {"name": "HP Victus 15 Gaming Laptop", "brand": "HP", "price_pkr": (165000, 195000), "desc": "AMD Ryzen 5 7535HS, RTX 4060 8GB, 15.6-inch FHD 144Hz, 16GB DDR5 RAM, 512GB NVMe SSD"},
            {"name": "Dell XPS 15 9560", "brand": "Dell", "price_pkr": (285000, 340000), "desc": "Intel Core i7-13700H, 15.6-inch OLED 3.5K, NVIDIA RTX 4070, 16GB LPDDR5, 1TB SSD"},
            {"name": "Apple MacBook Air M2", "brand": "Apple", "price_pkr": (249000, 299000), "desc": "Apple M2 chip, 13.6-inch Liquid Retina, 8GB unified memory, 256GB SSD, 18-hour battery, MagSafe"},
            {"name": "Apple MacBook Pro 14-inch M3 Pro", "brand": "Apple", "price_pkr": (415000, 479000), "desc": "Apple M3 Pro chip, 14.2-inch Liquid Retina XDR, 18GB unified memory, 512GB SSD"},
            {"name": "Lenovo IdeaPad Slim 5i", "brand": "Lenovo", "price_pkr": (115000, 148000), "desc": "Intel Core i5-1335U, 15.6-inch FHD IPS, 16GB DDR5, 512GB SSD, Intel Iris Xe graphics"},
            {"name": "Asus VivoBook 15", "brand": "Asus", "price_pkr": (95000, 125000), "desc": "AMD Ryzen 5 7520U, 15.6-inch FHD, 16GB DDR5, 512GB PCIe SSD, 42Wh battery"},
            {"name": "Acer Aspire 5", "brand": "Acer", "price_pkr": (88000, 112000), "desc": "AMD Ryzen 5 7530U, 15.6-inch FHD IPS, 8GB RAM, 512GB SSD, AMD Radeon graphics, backlit keyboard"},
            {"name": "MSI Thin GF63", "brand": "MSI", "price_pkr": (155000, 188000), "desc": "Intel Core i7-12650H, RTX 4050 6GB, 15.6-inch FHD 144Hz, 16GB DDR4, 512GB NVMe"},
            {"name": "HP 15s Core i3", "brand": "HP", "price_pkr": (68000, 85000), "desc": "Intel Core i3-1215U, 15.6-inch FHD, 8GB DDR4, 512GB SSD, Intel UHD graphics, Windows 11"},
            {"name": "Lenovo LOQ Gaming Laptop", "brand": "Lenovo", "price_pkr": (175000, 215000), "desc": "AMD Ryzen 7 7745HX, RTX 4060 8GB, 15.6-inch FHD 165Hz, 16GB DDR5, 512GB SSD"},
            # Smart Watches
            {"name": "Apple Watch Series 9", "brand": "Apple", "price_pkr": (89000, 108000), "desc": "S9 SiP chip, 41mm/45mm, Always-On Retina, Double Tap gesture, blood oxygen, ECG, 18-hour battery"},
            {"name": "Samsung Galaxy Watch 6", "brand": "Samsung", "price_pkr": (62000, 78000), "desc": "40mm/44mm Sapphire Crystal, BioActive Sensor, sleep coaching, body composition, Wear OS 4"},
            {"name": "Xiaomi Mi Band 8 Pro", "brand": "Xiaomi", "price_pkr": (9500, 14000), "desc": "1.74-inch AMOLED 60Hz, 14-day battery, 150+ fitness modes, heart rate, SpO2, sleep tracking"},
            {"name": "Garmin Fenix 7", "brand": "Garmin", "price_pkr": (135000, 165000), "desc": "Multi-GNSS, Solar charging, 18-day battery, topographic maps, advanced training metrics"},
            {"name": "Fitbit Charge 6", "brand": "Fitbit", "price_pkr": (45000, 58000), "desc": "Built-in GPS, ECG app, heart rate zones, sleep tracking, 7-day battery, Google integration"},
            # Headphones
            {"name": "Sony WH-1000XM5 Wireless", "brand": "Sony", "price_pkr": (62000, 78000), "desc": "Industry-leading ANC, 30-hour battery, multipoint connection, LDAC Hi-Res Audio, 3-mic array"},
            {"name": "Bose QuietComfort 45", "brand": "Bose", "price_pkr": (55000, 70000), "desc": "World-class noise cancellation, 24-hour battery, Aware Mode, premium comfort, USB-C charging"},
            {"name": "AirPods Pro (2nd gen)", "brand": "Apple", "price_pkr": (59000, 72000), "desc": "H2 chip, Adaptive Audio, Personalized Spatial Audio, 30-hour total battery, IP54, USB-C"},
            {"name": "JBL Quantum 910 Gaming", "brand": "JBL", "price_pkr": (25000, 34000), "desc": "Head-tracking spatial audio, ANC, 2.4GHz wireless, 34-hour battery, JBL QuantumSurround"},
            {"name": "Sennheiser Momentum 4 Wireless", "brand": "Sennheiser", "price_pkr": (68000, 85000), "desc": "60-hour battery, adaptive ANC, crystal-clear Bluetooth 5.2, aptX HD, foldable design"},
        ],
        "base_discount_chance": 0.35,
    },
    
    "Fashion & Clothing": {
        "icon": "fa-tshirt",
        "slug": "fashion",
        "color": "#E91E63",
        "subcategories": ["Men's Clothing", "Women's Clothing", "Kids", "Footwear", "Bags", "Accessories", "Watches", "Jewelry"],
        "products": [
            {"name": "Gul Ahmed Lawn Suit 3-Piece Unstitched", "brand": "Gul Ahmed", "price_pkr": (3500, 8500), "desc": "Premium Egyptian cotton lawn fabric, intricate digital print, includes shirt, dupatta, trouser"},
            {"name": "Gul Ahmed Summer Collection Stitched", "brand": "Gul Ahmed", "price_pkr": (5500, 11000), "desc": "Ready-to-wear lawn outfit, embroidered neckline, breathable cotton, sizes S to XXL"},
            {"name": "Khaadi Khaddar 2-Piece", "brand": "Khaadi", "price_pkr": (6500, 14000), "desc": "Handwoven khaddar fabric, geometric patterns, autumn/winter collection, warm and comfortable"},
            {"name": "Khaadi Cotton Kurta for Men", "brand": "Khaadi", "price_pkr": (2800, 5500), "desc": "100% cotton, traditional embroidered collar, multiple colors, machine washable, comfort fit"},
            {"name": "Sapphire Western Trousers for Women", "brand": "Sapphire", "price_pkr": (3200, 6800), "desc": "Slim fit, high-rise waist, cotton blend, multiple colors and prints, office and casual wear"},
            {"name": "Bonanza Satrangi Kurta Shalwar Men", "brand": "Bonanza", "price_pkr": (3800, 7500), "desc": "Premium cotton, traditional cut, embroidered details, suitable for Eid, weddings, and occasions"},
            {"name": "J. Junaid Jamshed Girls Lawn Frock", "brand": "J.", "price_pkr": (2200, 4500), "desc": "Digital print lawn frock, smocking on yoke, flutter sleeves, comfortable for summer"},
            {"name": "Alkaram Embroidered Chiffon Dupatta", "brand": "Alkaram", "price_pkr": (1800, 3800), "desc": "Premium chiffon with intricate embroidery, multiple colors, completes any traditional outfit"},
            {"name": "Levi's 511 Slim Jeans Men", "brand": "Levi's", "price_pkr": (8500, 13500), "desc": "Slim fit from hip to ankle, 99% cotton 1% elastane, versatile for casual and smart casual"},
            {"name": "Nike Air Max 270 Shoes", "brand": "Nike", "price_pkr": (22000, 29000), "desc": "Max Air 270 unit, foam midsole, breathable mesh upper, casual lifestyle sneaker, multiple colorways"},
            {"name": "Adidas Ultraboost 23 Running Shoes", "brand": "Adidas", "price_pkr": (26000, 34000), "desc": "BOOST midsole, PRIMEKNIT+ upper, Continental rubber outsole, Linear Energy Push system"},
            {"name": "Servis Shoes Liza Ladies Heels", "brand": "Servis", "price_pkr": (2800, 5500), "desc": "Block heel, premium PU upper, comfortable insole, multiple colors, Pakistan's #1 footwear brand"},
            {"name": "Skechers GO Walk 6 Men", "brand": "Skechers", "price_pkr": (9500, 13500), "desc": "Air-Cooled Goga Mat insole, machine washable, high-rebound ULTRA GO cushioning, slip-on design"},
            {"name": "Bata Wedge Sandals Women", "brand": "Bata", "price_pkr": (1800, 4500), "desc": "Comfortable wedge heels, open toe design, ankle strap, suitable for casual and semi-formal"},
            {"name": "Puma RS-X Sneakers Unisex", "brand": "Puma", "price_pkr": (14500, 19000), "desc": "Retro-running design, RS (Running System) cushioning, bold color-blocking, leather/mesh upper"},
            {"name": "Fossil Leather Shoulder Bag Women", "brand": "Fossil", "price_pkr": (18500, 27000), "desc": "Genuine leather, multiple compartments, adjustable strap, magnetic closure, classic style"},
            {"name": "Polo Ralph Lauren Classic Fit Polo", "brand": "Ralph Lauren", "price_pkr": (12000, 18000), "desc": "100% cotton, signature pony embroidery, ribbed collar, two-button placket, 40+ colors"},
            {"name": "Zara Printed Blouse Women", "brand": "Zara", "price_pkr": (6500, 11000), "desc": "V-neck, floral print, flowing fabric, button-front, trendy for office and casual occasions"},
            {"name": "H&M Basic T-Shirt Pack of 3", "brand": "H&M", "price_pkr": (3200, 5500), "desc": "Regular fit, 100% cotton jersey, crew neck, pack of 3 in white/black/gray, soft and durable"},
            {"name": "Titan Raga Watch for Women", "brand": "Titan", "price_pkr": (12500, 18000), "desc": "Stainless steel case, mother of pearl dial, sapphire crystal glass, leather strap, 50m water resistant"},
        ],
        "base_discount_chance": 0.40,
    },
    
    "Home & Kitchen": {
        "icon": "fa-home",
        "slug": "home-kitchen",
        "color": "#795548",
        "subcategories": ["Kitchen Appliances", "Cookware", "Bedding", "Furniture", "Lighting", "Cleaning", "Storage", "Decor"],
        "products": [
            {"name": "Dawlance Inverter Refrigerator 15 CFT", "brand": "Dawlance", "price_pkr": (65000, 85000), "desc": "15 CFT capacity, energy-saving inverter compressor, LVP technology, twin cooling, 10-year warranty"},
            {"name": "PEL Aspire Refrigerator 14 CFT", "brand": "PEL", "price_pkr": (58000, 75000), "desc": "14 CFT, Haier compressor, Vita Fresh Zone, anti-bacterial gasket, glass shelves, flower line"},
            {"name": "Samsung 1.5 Ton Split AC Inverter", "brand": "Samsung", "price_pkr": (88000, 110000), "desc": "Digital Inverter, WindFree cooling, 5-star energy rating, Triple Protector Plus, Auto Clean"},
            {"name": "Gree 1 Ton Inverter Split AC", "brand": "Gree", "price_pkr": (65000, 82000), "desc": "1 Ton inverter, I-Feel technology, self-cleaning, copper condenser, 18000 BTU cooling capacity"},
            {"name": "Dawlance 9kg Washing Machine Automatic", "brand": "Dawlance", "price_pkr": (68000, 85000), "desc": "9kg top load, fully automatic, inverter motor, 16 wash programs, Digital display, child lock"},
            {"name": "Haier Washing Machine Twin Tub 12kg", "brand": "Haier", "price_pkr": (35000, 48000), "desc": "12kg wash, 7kg spin, semi-automatic, dual function wash, transparent lid, energy efficient"},
            {"name": "Anex Microwave Oven 30L Digital", "brand": "Anex", "price_pkr": (18000, 26000), "desc": "30L capacity, digital control, 10 power levels, 5 auto menus, pizza/grill function, 1000W power"},
            {"name": "Westpoint Stand Mixer 7L", "brand": "Westpoint", "price_pkr": (22000, 32000), "desc": "7L stainless steel bowl, 800W motor, 10 speed settings, includes dough hook, whisk, beater"},
            {"name": "National Electric Pressure Cooker 6L", "brand": "National", "price_pkr": (12500, 18000), "desc": "6L capacity, 14 cooking programs, keep warm, delay timer, safety lid lock, 1000W"},
            {"name": "Philips Air Fryer 4.1L HD9252", "brand": "Philips", "price_pkr": (28000, 38000), "desc": "4.1L, Rapid Air technology, 1400W, digital display, 7 pre-set programs, dishwasher-safe basket"},
            {"name": "Kenwood Hand Blender HB680", "brand": "Kenwood", "price_pkr": (8500, 13500), "desc": "700W motor, stainless steel blending shaft, variable speed, includes beaker and chopper attachment"},
            {"name": "Nonstick Cookware Set 7-Piece", "brand": "Sonex", "price_pkr": (8500, 16000), "desc": "7-piece: frypan, saucepans, stock pot with lids, granite non-stick coating, induction compatible"},
            {"name": "Sapphire Bed Sheet King Size", "brand": "Sapphire", "price_pkr": (4500, 9500), "desc": "100% Egyptian cotton, 400 thread count, King size, includes 2 pillowcases, multiple patterns"},
            {"name": "Interwood Wooden Dining Table 6-Seater", "brand": "Interwood", "price_pkr": (55000, 90000), "desc": "Solid wood, 6-seater, premium finish, included chairs, durable and elegant design"},
            {"name": "Kenmore Front Load Washing Machine", "brand": "Kenmore", "price_pkr": (72000, 95000), "desc": "8kg capacity, 1400 RPM spin, 15 wash programs, steam function, A+++ energy rating"},
            {"name": "Osaka Deep Freezer 15 CFT", "brand": "Osaka", "price_pkr": (52000, 68000), "desc": "15 CFT, fast freeze function, lockable lid, drain plug, inner light, energy-saving compressor"},
            {"name": "Dyson V12 Detect Slim Vacuum", "brand": "Dyson", "price_pkr": (89000, 112000), "desc": "Laser detects microscopic dust, HEPA filtration captures 99.99%, 60-min run time, 5 accessories"},
            {"name": "IKEA KALLAX Shelf Unit 4x4", "brand": "IKEA", "price_pkr": (18500, 26000), "desc": "77x147cm, 16 cube storage, white/black/wood options, compatible with KALLAX inserts"},
            {"name": "Villeroy & Boch Dinner Set 18-Piece", "brand": "Villeroy & Boch", "price_pkr": (28000, 45000), "desc": "Premium porcelain, 6 dinner plates + 6 soup plates + 6 bowls, dishwasher safe, elegant design"},
            {"name": "Panasonic Rice Cooker 1.8L SR-W18GH", "brand": "Panasonic", "price_pkr": (9500, 14500), "desc": "1.8L/10-cup capacity, automatic keep warm, non-stick inner bowl, steam tray included, 660W"},
        ],
        "base_discount_chance": 0.30,
    },
    
    "Books & Stationery": {
        "icon": "fa-book",
        "slug": "books",
        "color": "#3F51B5",
        "subcategories": ["Fiction", "Non-Fiction", "Textbooks", "Islamic Books", "Children's Books", "Stationery", "Arts & Crafts"],
        "products": [
            {"name": "Atomic Habits by James Clear", "brand": "Penguin", "price_pkr": (850, 1500), "desc": "The #1 New York Times bestseller. Tiny changes, remarkable results. Proven framework for building good habits and breaking bad ones."},
            {"name": "Rich Dad Poor Dad by Robert Kiyosaki", "brand": "Warner Books", "price_pkr": (750, 1350), "desc": "What the rich teach their kids about money that the poor and middle class do not. Classic personal finance guide."},
            {"name": "The Psychology of Money by Morgan Housel", "brand": "Harriman House", "price_pkr": (900, 1600), "desc": "Timeless lessons on wealth, greed, and happiness. 19 short stories exploring the strange ways people think about money."},
            {"name": "Sapiens by Yuval Noah Harari", "brand": "Harper", "price_pkr": (1200, 1950), "desc": "A brief history of humankind. From Stone Age to the 21st century, the most important aspects of human history."},
            {"name": "Think and Grow Rich by Napoleon Hill", "brand": "Fingerprint", "price_pkr": (650, 1100), "desc": "The original success classic. 13 principles to wealth and success drawn from interviews with 500+ wealthy individuals."},
            {"name": "The Alchemist by Paulo Coelho", "brand": "HarperCollins", "price_pkr": (750, 1250), "desc": "A fable about following your dream. Over 65 million copies sold worldwide in 80+ languages."},
            {"name": "Quran Majeed with Urdu Translation", "brand": "Taj Company", "price_pkr": (1200, 3500), "desc": "Complete Quran with word-by-word Urdu translation, Tafseer references, high-quality paper, durable binding"},
            {"name": "Seerat-un-Nabi by Allama Shibli Nomani", "brand": "Maktaba Al-Asriya", "price_pkr": (2500, 4500), "desc": "Complete 8-volume set, comprehensive biography of Prophet Muhammad (PBUH), Urdu language"},
            {"name": "A Level Physics Complete Revision", "brand": "Oxford", "price_pkr": (3500, 5500), "desc": "Complete revision guide for A-Level Physics, practice questions, exam tips, full-color diagrams"},
            {"name": "O Level Mathematics by Sue Pemberton", "brand": "Cambridge", "price_pkr": (2800, 4500), "desc": "Cambridge O Level Mathematics endorsed textbook, worked examples, practice exercises, exam format"},
            {"name": "MDCAT Biology Guide Pakistan", "brand": "Ilmi Kitab Khana", "price_pkr": (1800, 3200), "desc": "Comprehensive MDCAT biology guide, past papers, MCQs, NUMS/UHS syllabus aligned"},
            {"name": "CSS Compulsory Subjects Guide", "brand": "AH Publishers", "price_pkr": (2500, 4200), "desc": "Complete CSS preparation guide, past papers, model answers, current affairs, Pakistan affairs"},
            {"name": "Parker Jotter Ballpoint Pen Set", "brand": "Parker", "price_pkr": (2800, 4500), "desc": "Set of 5 classic Jotter pens, stainless steel with checkered pattern, includes blue and black refills"},
            {"name": "Staedtler Mars 780 Technical Pencil Set", "brand": "Staedtler", "price_pkr": (3500, 5500), "desc": "Set of 3: 0.3mm, 0.5mm, 0.7mm, includes spare leads and eraser, drafting and technical drawing"},
            {"name": "Moleskine Classic Hardcover Notebook A5", "brand": "Moleskine", "price_pkr": (2200, 3500), "desc": "240 pages, plain/ruled/squared, ivory paper, expandable inner pocket, elastic closure, ribbon bookmark"},
            {"name": "HP DeskJet 2723 All-in-One Printer", "brand": "HP", "price_pkr": (16500, 22000), "desc": "Print, scan, copy, wireless, HP Instant Ink compatible, 5.5ppm color, 1000-page monthly duty cycle"},
            {"name": "Faber-Castell 48 Color Pencils Metal Box", "brand": "Faber-Castell", "price_pkr": (3800, 6500), "desc": "48 vivid colors, superior lightfastness, break-resistant leads, SV bonding, premium metal tin"},
            {"name": "Post-it Super Sticky Notes Assorted 12 Pack", "brand": "3M", "price_pkr": (1200, 2200), "desc": "2x the sticking power, 3x12 pads of 45 sheets, 4 colors, 76x76mm, perfect for notes and reminders"},
            {"name": "Zero-G Premium Ballpoint Pen 10-Pack", "brand": "Pilot", "price_pkr": (950, 1800), "desc": "Ultra-smooth writing, 1.0mm tip, black ink, comfortable grip, retractable, 10-pack value set"},
            {"name": "Casio FX-991EX Scientific Calculator", "brand": "Casio", "price_pkr": (4500, 6500), "desc": "552 functions, high-resolution display, spreadsheet mode, QR code function, allowed in IGCSE/A-Level"},
        ],
        "base_discount_chance": 0.25,
    },
    
    "Sports & Outdoor": {
        "icon": "fa-dumbbell",
        "slug": "sports",
        "color": "#FF5722",
        "subcategories": ["Cricket", "Fitness", "Gym Equipment", "Cycling", "Badminton", "Football", "Yoga", "Swimming"],
        "products": [
            {"name": "Gray-Nicolls Predator3 Cricket Bat English Willow", "brand": "Gray-Nicolls", "price_pkr": (28000, 45000), "desc": "Grade 1 English Willow, full profile blade, rounded toe, short handle, signed by county professionals"},
            {"name": "SS Ton Reserve Edition Cricket Bat", "brand": "SS", "price_pkr": (35000, 55000), "desc": "English Willow Grade A, high spine, oval handle, full shoulder, used by national team players"},
            {"name": "Kookaburra Pace Cricket Ball Red 5.5oz", "brand": "Kookaburra", "price_pkr": (3500, 5500), "desc": "Premium hand-stitched, 4-piece construction, Grade 1 alum-tanned leather, WICF approved"},
            {"name": "Adidas Predator League Football", "brand": "Adidas", "price_pkr": (8500, 14000), "desc": "FIFA quality mark, 4-color printed, thermally bonded, 3D printed grip zones, size 5"},
            {"name": "Yonex Astrox 99 Pro Badminton Racket", "brand": "Yonex", "price_pkr": (22000, 32000), "desc": "4U/G5, Namd graphite, rotational generator system, included full cover, string: BG66 Ultimax"},
            {"name": "CrossFit Adjustable Dumbbell Set 5-50kg", "brand": "PowerBlock", "price_pkr": (45000, 65000), "desc": "Adjustable from 2.5kg to 25kg per dumbbell, replaces 28 sets, steel construction, safe selector pin"},
            {"name": "Impex Marcy Smith Machine Home Gym", "brand": "Marcy", "price_pkr": (185000, 250000), "desc": "200kg weight capacity, built-in weight stack, pull-up bar, cable crossover, adjustable bench included"},
            {"name": "Nike Dri-FIT Running Shoes Zoom Pegasus 40", "brand": "Nike", "price_pkr": (24000, 32000), "desc": "Zoom Air unit, React foam midsole, breathable engineered mesh, reflective details, 8mm heel drop"},
            {"name": "Lifeline Treadmill DT-7 DC Motor", "brand": "Lifeline", "price_pkr": (75000, 98000), "desc": "3HP DC motor, 16kmph max speed, 15% auto-incline, heart rate sensors, 100kg capacity"},
            {"name": "Kettler Air 7 Exercise Bike", "brand": "Kettler", "price_pkr": (65000, 88000), "desc": "8-stage magnetic resistance, heart rate monitoring, 120kg capacity, 18kg flywheel, computer display"},
            {"name": "Lululemon Align High-Rise Yoga Pants", "brand": "Lululemon", "price_pkr": (18500, 26000), "desc": "Nulu fabric, 4-way stretch, sweat-wicking, lightweight, 7/8 length, squat-proof, 25 colors"},
            {"name": "Speedo Endurance+ Goggles", "brand": "Speedo", "price_pkr": (3500, 5500), "desc": "Anti-fog coating, UV protection, hydrodynamic design, adjustable nose bridge, competition grade"},
            {"name": "Columbia Watertight II Rain Jacket", "brand": "Columbia", "price_pkr": (22000, 32000), "desc": "100% nylon, Omni-Tech waterproof, packable design, adjustable hood, multiple colors"},
            {"name": "Garmin Edge 540 GPS Cycling Computer", "brand": "Garmin", "price_pkr": (62000, 82000), "desc": "GPS/GLONASS/Galileo, 26-hour battery, Forksight, ClimbPro, compatible with all cycling sensors"},
            {"name": "Reebok CrossFit Nano X3 Training Shoes", "brand": "Reebok", "price_pkr": (15500, 22000), "desc": "Floatride Energy Foam, raised heel, lateral bands, rubber compound outsole, wide toe box"},
            {"name": "Wilson Ultra 108 Tennis Racket", "brand": "Wilson", "price_pkr": (28000, 42000), "desc": "Carbon fiber frame, 108sq-in head, power holes, power web, 16x19 string pattern, 4-3/8 grip"},
            {"name": "Regatta Stretch Walking Trousers Men", "brand": "Regatta", "price_pkr": 8500, "price_pkr": (8500, 14000), "desc": "4-way stretch, moisture-wicking, UPF 40+, zip-off legs, multiple pockets, quick-dry"},
            {"name": "Trigon Cricket Gloves Batting Premium", "brand": "Trigon", "price_pkr": (5500, 9500), "desc": "Premium leather palm, high-density foam protection, Velcro wrist, comfortable fit, both hands"},
            {"name": "Nivia Storm Football Boots", "brand": "Nivia", "price_pkr": (4500, 8500), "desc": "Synthetic upper, TPU outsole, ankle support, direct-shot technology, FG for natural grass"},
            {"name": "Decathlon Domyos Skipping Rope Speed", "brand": "Decathlon", "price_pkr": (1800, 3500), "desc": "Speed rope for CrossFit, adjustable length, ball bearings handle, 300cm rope, 180RPM capability"},
        ],
        "base_discount_chance": 0.28,
    },
    
    "Beauty & Personal Care": {
        "icon": "fa-spa",
        "slug": "beauty",
        "color": "#E91E63",
        "subcategories": ["Skincare", "Hair Care", "Makeup", "Fragrances", "Men's Grooming", "Oral Care", "Bath & Body"],
        "products": [
            {"name": "Neutrogena Hydro Boost Water Gel 50g", "brand": "Neutrogena", "price_pkr": (2800, 4500), "desc": "Hyaluronic acid, oil-free, non-comedogenic, fragrance-free, instantly quenches skin's thirst"},
            {"name": "Cetaphil Gentle Skin Cleanser 500ml", "brand": "Cetaphil", "price_pkr": (1800, 2800), "desc": "Gentle non-foaming formula, suitable for sensitive skin, dermatologist recommended, no fragrance"},
            {"name": "L'Oreal Paris Revitalift Serum 30ml", "brand": "L'Oreal", "price_pkr": (3500, 5500), "desc": "1.5% pure hyaluronic acid, 3 molecular weights, reduces wrinkles in 1 week, plumps and firms"},
            {"name": "The Ordinary Niacinamide 10% + Zinc 1%", "brand": "The Ordinary", "price_pkr": (1800, 2800), "desc": "High-strength vitamin B3 and zinc formula, reduces blemishes, minimizes pores, balances sebum"},
            {"name": "Pond's Bright Beauty BB Cream SPF30", "brand": "Pond's", "price_pkr": (850, 1500), "desc": "5-in-1 BB cream: moisturize, protect SPF30, vitamin B3, whitening, oil control, natural finish"},
            {"name": "Dove Deep Moisture Body Wash 500ml", "brand": "Dove", "price_pkr": (950, 1600), "desc": "NutriumMoisture technology, 1/4 moisturizing cream, dermatologist tested, gentle and caring"},
            {"name": "Pantene Pro-V Silky Smooth Shampoo 400ml", "brand": "Pantene", "price_pkr": (850, 1450), "desc": "Pro-V formula, repairs damage, smooths frizz, strengthens hair, long-lasting softness and shine"},
            {"name": "TRESemme Keratin Smooth Shampoo 580ml", "brand": "TRESemme", "price_pkr": (1200, 1950), "desc": "Marula oil and keratin, smooths frizz 80%, humidity-resistant up to 48 hours, salon-quality"},
            {"name": "Maybelline Fit Me Foundation 30ml", "brand": "Maybelline", "price_pkr": (2200, 3500), "desc": "Natural matte finish, pore minimizing, 40 shades, non-comedogenic, dermatologist tested"},
            {"name": "MAC Studio Fix Powder Plus Foundation", "brand": "MAC", "price_pkr": (7500, 11000), "desc": "Medium to full coverage, matte finish, broad SPF 15, oil control for 8 hours, 50 shades"},
            {"name": "Lakmé 9-to-5 Primer + Matte Perfect Cover", "brand": "Lakmé", "price_pkr": (1800, 2800), "desc": "30ml, matte coverage with primer base, long wear up to 16 hours, oil control, 8 shades"},
            {"name": "Pakistan's Own Jasmine Attar 12ml", "brand": "Al-Haramain", "price_pkr": (1800, 3500), "desc": "Pure jasmine essential oil attar, non-alcoholic, long lasting 8+ hours, handpicked flowers"},
            {"name": "J. Junaid Jamshed Mushk Perfume 100ml", "brand": "J.", "price_pkr": (2800, 4500), "desc": "Oud and musk blend, long-lasting spray, halal certified, classic Pakistani fragrance"},
            {"name": "Braun Series 5 Electric Shaver 5018s", "brand": "Braun", "price_pkr": (28000, 38000), "desc": "AutoSense technology, 100% waterproof, 3-day stubble trimmer, Flex MotionTech, EasyClick attachments"},
            {"name": "Gillette Mach3 Razor with 4 Blades", "brand": "Gillette", "price_pkr": (1800, 2800), "desc": "3 DuraComfort blades, pivoting head, lubricating strip with aloe, fits all Mach3 cartridges"},
            {"name": "Oral-B Pro 2000 Electric Toothbrush", "brand": "Oral-B", "price_pkr": (8500, 13500), "desc": "2D cleaning, pressure sensor, 2-minute timer, 2 cleaning modes, includes 1 sensitive brush head"},
            {"name": "Colgate Optic White Charcoal Toothpaste 100g", "brand": "Colgate", "price_pkr": (650, 1100), "desc": "Activated charcoal, removes surface stains, whitens in 3 days, strengthens enamel, fresh mint"},
            {"name": "Victoria's Secret Love Spell Body Mist 250ml", "brand": "Victoria's Secret", "price_pkr": (5500, 8500), "desc": "Cherry blossom, peach, and white musk blend, lightweight refreshing mist, long-lasting fragrance"},
            {"name": "Himalaya Anti-Dandruff Shampoo 400ml", "brand": "Himalaya", "price_pkr": (650, 1100), "desc": "Tea tree oil and rosemary, reduces dandruff 100% in 2 weeks, gentle daily use, clinically tested"},
            {"name": "Sunsilk Stunning Black Shine Conditioner 180ml", "brand": "Sunsilk", "price_pkr": (450, 850), "desc": "Amla and vitamin complex, adds deep shine, reduces breakage, detangles, everyday use conditioner"},
        ],
        "base_discount_chance": 0.38,
    },
    
    "Toys & Baby": {
        "icon": "fa-baby",
        "slug": "toys-baby",
        "color": "#8BC34A",
        "subcategories": ["Baby Essentials", "Educational Toys", "Action Figures", "Board Games", "RC Toys", "Dolls", "Building Sets"],
        "products": [
            {"name": "LEGO Technic Lamborghini Huracán 42161", "brand": "LEGO", "price_pkr": (28000, 42000), "desc": "806 pieces, 1:12 scale, V10 engine, rear-wheel steering, opening hood/doors, 18+ age recommendation"},
            {"name": "LEGO City Police Station 60316", "brand": "LEGO", "price_pkr": (16500, 24000), "desc": "668 pieces, includes police vehicles, 6 minifigures, jail cell, command center, garage, ages 6+"},
            {"name": "Barbie Fashionista Doll 2024 Collection", "brand": "Barbie", "price_pkr": (3500, 6500), "desc": "18cm, articulated, comes with 2 outfits, accessories, and display stand, ages 3+ years"},
            {"name": "Hot Wheels 20-Car Gift Pack", "brand": "Hot Wheels", "price_pkr": (3800, 6500), "desc": "20 die-cast 1:64 scale vehicles, various models including race cars, trucks, fantasy vehicles"},
            {"name": "Monopoly Classic Board Game", "brand": "Hasbro", "price_pkr": (5500, 8500), "desc": "Classic property trading game, 2-6 players, ages 8+, includes board, dice, cards, playing pieces"},
            {"name": "Nerf Elite 2.0 Commander RD-6 Blaster", "brand": "Nerf", "price_pkr": (5500, 8500), "desc": "6-dart rotating drum, 18 darts included, slam-fire, 27m range, compatible with all Elite darts"},
            {"name": "Pampers Premium Care Diapers Size 3 (128 pcs)", "brand": "Pampers", "price_pkr": (5500, 7500), "desc": "Size 3 (6-10kg), 128 diapers, extra softness, wetness indicator, up to 12 hours dryness"},
            {"name": "Huggies Gold Diapers Size 4 (72 pcs)", "brand": "Huggies", "price_pkr": (4800, 6500), "desc": "Size 4 (8-14kg), 72 diapers, stretchy sides, SkinCare lotion, breathable cover, 12-hour protection"},
            {"name": "Philips Avent Natural Baby Bottle 260ml", "brand": "Philips Avent", "price_pkr": (2800, 4500), "desc": "Natural latch, anti-colic valve, wide breast-shaped nipple, BPA-free, dishwasher safe"},
            {"name": "Fisher-Price Baby Gym Play Mat", "brand": "Fisher-Price", "price_pkr": (6500, 9500), "desc": "5 position play gym, 12 activities, detachable toys, machine-washable mat, newborn to 12 months"},
            {"name": "Huffy 20-inch Kids Mountain Bike", "brand": "Huffy", "price_pkr": (25000, 38000), "desc": "Steel frame, 7-speed Shimano, front and rear hand brakes, adjustable seat, front suspension"},
            {"name": "Melissa & Doug Wooden Puzzles Set 8", "brand": "Melissa & Doug", "price_pkr": (3500, 5500), "desc": "8 chunky puzzle boards, animals/vehicles/shapes, smooth wooden pieces, 2-3 year olds"},
            {"name": "RC Buggy Off-Road 1:12 Scale 4WD", "brand": "TAMIYA", "price_pkr": (12500, 18000), "desc": "1:12 scale, 4WD, 2.4GHz remote, 25kmph, rechargeable battery, off-road tyres, USB charging"},
            {"name": "UNO Card Game Family Pack", "brand": "Mattel", "price_pkr": (1800, 3200), "desc": "112 cards, classic rules, special action cards, 2-10 players, ages 7+, fast-paced fun"},
            {"name": "Baby Shark Musical Bath Toys Set", "brand": "ZURU", "price_pkr": (3200, 5500), "desc": "6-piece bath toy set, Baby Shark, water squirters, floating toys, ages 2+, BPA-free"},
            {"name": "Chicco Bib Easy Meal 2-Pack", "brand": "Chicco", "price_pkr": (1200, 2200), "desc": "Flexible crumb catcher, adjustable neck velcro, easy wipe clean, ages 6m+, dishwasher safe"},
            {"name": "VTech Baby Walker Music & Lights", "brand": "VTech", "price_pkr": (8500, 13500), "desc": "Baby push-along walker, lights and sounds, English/Spanish learning mode, 3 activity areas, 9m+"},
            {"name": "Play-Doh Ultimate Color Collection 65 Cans", "brand": "Hasbro", "price_pkr": (8500, 13500), "desc": "65 non-toxic colors, 2oz cans, resealable containers, ages 2+, classic fun for creativity"},
            {"name": "Rubik's Cube 3x3 Original Speed", "brand": "Rubik's", "price_pkr": (3500, 5500), "desc": "Original 3x3, smooth turning, PVC stickers, anti-pop mechanism, ages 8+, the iconic puzzle"},
            {"name": "Kumon Math Workbook Grade 1-3 Set", "brand": "Kumon", "price_pkr": (4500, 7500), "desc": "3-book set: addition/subtraction/multiplication, 192 pages per book, gradual skill building"},
        ],
        "base_discount_chance": 0.32,
    },
    
    "Food & Grocery": {
        "icon": "fa-utensils",
        "slug": "food-grocery",
        "color": "#4CAF50",
        "subcategories": ["Dry Fruits", "Tea & Coffee", "Spices", "Organic Foods", "Snacks", "Cooking Oils", "Dairy", "Imported Foods"],
        "products": [
            {"name": "Shan Biryani Masala 60g", "brand": "Shan", "price_pkr": (120, 220), "desc": "Authentic recipe masala, spice blend for biryani, serves 5-6 persons, no artificial colors or preservatives"},
            {"name": "National Recipe Mix Nihari 100g", "brand": "National Foods", "price_pkr": (95, 180), "desc": "Authentic Nihari recipe mix, premium spices, serves 8-10 persons, rich dark color and aroma"},
            {"name": "Tapal Danedar Tea 900g", "brand": "Tapal", "price_pkr": (1450, 1950), "desc": "Pakistan's best-selling tea, bold and full-bodied, made from finest Kenyan and Lankan tea leaves"},
            {"name": "Lipton Yellow Label Tea 200 Tea Bags", "brand": "Lipton", "price_pkr": (1800, 2500), "desc": "200 individual tea bags, rich and refreshing, Rainforest Alliance certified, ideal for office use"},
            {"name": "Nescafe Classic Instant Coffee 200g", "brand": "Nescafe", "price_pkr": (1650, 2200), "desc": "100% pure coffee, rich aroma, full-bodied taste, jar for freshness, dissolved in seconds"},
            {"name": "Rooh Afza Sharbat 1 Litre", "brand": "Hamdard", "price_pkr": (650, 950), "desc": "Traditional summer drink, rose flavor, herbs and flowers blend, Pakistan's iconic Ramadan drink"},
            {"name": "Premium Dates Medjool 1kg", "brand": "Al-Madina", "price_pkr": (2800, 4500), "desc": "Large Medjool dates, fresh and moist, naturally sweet, imported from Saudi Arabia, no preservatives"},
            {"name": "Kashmiri Almonds Premium 500g", "brand": "Nutri Valley", "price_pkr": (2800, 4500), "desc": "Raw Kashmiri almonds, thin shell, sweet and crunchy, vacuum packed for freshness"},
            {"name": "Organic Desi Ghee 1kg Pure", "brand": "Tehzeeb", "price_pkr": (3800, 5500), "desc": "100% pure desi cow ghee, traditional wooden churning, certified organic, rich flavor, golden color"},
            {"name": "Sunridge Farm Oats Quick Cook 1kg", "brand": "Sunridge", "price_pkr": (850, 1400), "desc": "100% wholegrain rolled oats, high fiber, no added sugar or salt, cooks in 5 minutes"},
            {"name": "Borges Extra Virgin Olive Oil 500ml", "brand": "Borges", "price_pkr": (2800, 4200), "desc": "Cold pressed, Spanish origin, 0.2% acidity, rich polyphenols, ideal for salads and dipping"},
            {"name": "Kellogg's Cornflakes Original 750g", "brand": "Kellogg's", "price_pkr": (1200, 1800), "desc": "Golden toasted cornflakes, fortified with 11 vitamins and minerals, crispy texture, classic taste"},
            {"name": "Pran Mango Juice Tetra Pack 250ml x6", "brand": "Pran", "price_pkr": (850, 1450), "desc": "Pack of 6, 100% real mango juice, no artificial colors, no preservatives, 250ml each"},
            {"name": "Nutella Hazelnut Spread 750g", "brand": "Ferrero", "price_pkr": (2200, 3200), "desc": "Classic hazelnut spread with cocoa, palm oil-free, made with quality ingredients, glass jar"},
            {"name": "Himalayan Pink Salt Fine Grain 1kg", "brand": "Himalayan Chef", "price_pkr": (650, 1100), "desc": "Authentic Pakistani pink salt, rich in 84 minerals, hand-mined from Khewra, chemical free"},
            {"name": "Walls Cornetto Classic 6-Pack", "brand": "Walls", "price_pkr": (950, 1600), "desc": "6 cones, real chocolate, vanilla ice cream, waffle cone with chocolate-coated tip, 110ml each"},
            {"name": "Lays Classic Salted Chips Value Pack 6x34g", "brand": "Lays", "price_pkr": (850, 1350), "desc": "Classic salted potato chips, crispy and light, value pack of 6 regular bags, enjoy anywhere"},
            {"name": "Nestle MILO Activ-Go 400g Tin", "brand": "Nestle", "price_pkr": (1200, 1800), "desc": "Malt-based chocolate drink, rich in iron, calcium, vitamins B2/B3/B6/B12, kids nutrition"},
            {"name": "Rafhan Corn Oil 5 Litre", "brand": "Rafhan", "price_pkr": (3500, 4800), "desc": "100% pure corn oil, high smoke point, cholesterol-free, rich in Vitamin E, ideal for frying"},
            {"name": "Olper's Full Cream Milk UHT 1L x6", "brand": "Engro", "price_pkr": (1650, 2200), "desc": "Pack of 6, full cream UHT milk, 3.5% fat, fortified with vitamins A&D, 6-month shelf life"},
        ],
        "base_discount_chance": 0.22,
    },
    
    "Health & Medicine": {
        "icon": "fa-heartbeat",
        "slug": "health",
        "color": "#00BCD4",
        "subcategories": ["Vitamins", "Medical Devices", "First Aid", "Protein & Supplements", "Personal Care", "Eye Care"],
        "products": [
            {"name": "Ensure Nutritional Supplement Vanilla 400g", "brand": "Abbott", "price_pkr": (3200, 4800), "desc": "Complete balanced nutrition, 28 essential vitamins and minerals, 26g protein, suitable for adults"},
            {"name": "Vitamin C 1000mg Effervescent 20 Tablets", "brand": "Redoxon", "price_pkr": (1200, 1950), "desc": "1000mg Vitamin C, zinc, effervescent tablets, orange flavor, boosts immunity, antioxidant"},
            {"name": "Fish Oil Omega-3 1000mg 100 Softgels", "brand": "Now Foods", "price_pkr": (2800, 4200), "desc": "EPA 180mg + DHA 120mg, heart health, brain function, molecularly distilled, no fishy aftertaste"},
            {"name": "Multivitamin for Women 60 Tablets", "brand": "GNC", "price_pkr": (3800, 5800), "desc": "23 vitamins and minerals, iron, folic acid, calcium, supports energy, immunity, bone health"},
            {"name": "Oximeter Fingertip SpO2 Monitor Digital", "brand": "Contec", "price_pkr": (3500, 5500), "desc": "Blood oxygen saturation + pulse rate, 2-second results, OLED display, auto power-off, batteries included"},
            {"name": "Omron Blood Pressure Monitor HEM-7120", "brand": "Omron", "price_pkr": (9500, 14500), "desc": "Automatic upper arm, Intellisense technology, 60 memory per user, irregular heartbeat indicator"},
            {"name": "Whey Protein Optimum Nutrition Gold Standard 2lb", "brand": "ON", "price_pkr": (12500, 17500), "desc": "24g protein per serving, 5.5g BCAAs, low sugar, 58 servings, chocolate/vanilla/strawberry flavors"},
            {"name": "Band-Aid Premium Flexible Fabric 80 Count", "brand": "Johnson & Johnson", "price_pkr": (850, 1450), "desc": "Flexible fabric, stays on in water, 80 assorted bandages, sterile, skin-tone shades"},
            {"name": "Dettol Antiseptic Liquid 250ml", "brand": "Dettol", "price_pkr": (450, 750), "desc": "Kills 99.9% germs, dilute for wound care, antiseptic for cuts/grazes, also disinfects surfaces"},
            {"name": "Horlicks Original Health Drink 500g", "brand": "GSK", "price_pkr": (1650, 2400), "desc": "23 vital nutrients, calcium, vitamin D, protein, malted wheat, supports height and immunity in kids"},
        ],
        "base_discount_chance": 0.18,
    },
    
    "Automotive": {
        "icon": "fa-car",
        "slug": "automotive",
        "color": "#607D8B",
        "subcategories": ["Car Accessories", "Car Care", "Tyres", "Batteries", "Navigation", "Tools"],
        "products": [
            {"name": "Michelin Pilot Sport 5 Tyre 225/45 R17", "brand": "Michelin", "price_pkr": (22000, 32000), "desc": "Ultra-high performance, 300+ km/h rated, wet braking champion, 20% longer tread life, electric vehicle compatible"},
            {"name": "70Mai Dash Cam Pro Plus A500S 2.7K", "brand": "70Mai", "price_pkr": (18500, 26000), "desc": "2.7K resolution, GPS+ADAS, built-in 5GHz WiFi, night vision, parking mode, 140° wide angle"},
            {"name": "Xiaomi Car Air Purifier 2H", "brand": "Xiaomi", "price_pkr": (8500, 14000), "desc": "HEPA filter, removes 99% PM2.5, 12V car socket, compact design, filter replacement reminder"},
            {"name": "Atlas Battery 55Ah MF-55 Maintenance Free", "brand": "Atlas", "price_pkr": (18500, 24000), "desc": "55Ah maintenance-free battery, DIN standard, 2-year warranty, suitable for 1000-1600cc cars"},
            {"name": "Garmin DriveSmart 65 GPS Navigator", "brand": "Garmin", "price_pkr": (45000, 62000), "desc": "6.95-inch display, Pakistan/India maps, live traffic, driver alerts, hands-free Bluetooth calling"},
            {"name": "Turtle Wax Hybrid Solutions Ceramic Polish 500ml", "brand": "Turtle Wax", "price_pkr": (3500, 5500), "desc": "Ceramic coating, 12-month protection, scratch resistance, UV protection, deep glossy finish"},
            {"name": "3M Car Wrap Matte Black Vinyl 1.52x5m", "brand": "3M", "price_pkr": (8500, 13500), "desc": "Genuine 3M, matte black finish, air-release adhesive, conformable for complex curves, removable"},
            {"name": "K&N High-Flow Air Filter for 1000cc Honda", "brand": "K&N", "price_pkr": (5500, 8500), "desc": "Washable and reusable, increases horsepower, million-mile warranty, direct fit replacement"},
            {"name": "Baseus Car Vacuum Cleaner Wireless 15000Pa", "brand": "Baseus", "price_pkr": (5500, 8500), "desc": "15000Pa suction, cordless, 2-in-1 handheld, 25-minute battery, HEPA filter, LED light"},
            {"name": "Toyota Genuine Engine Oil 5W-30 4L SN", "brand": "Toyota", "price_pkr": (4800, 6800), "desc": "Genuine Toyota 5W-30 fully synthetic, SN standard, suitable for all Toyota vehicles, 4-liter pack"},
        ],
        "base_discount_chance": 0.20,
    },
    
    "Office Supplies": {
        "icon": "fa-briefcase",
        "slug": "office",
        "color": "#9C27B0",
        "subcategories": ["Printing", "Office Furniture", "Filing", "Desk Accessories", "Whiteboards"],
        "products": [
            {"name": "HP LaserJet Pro M404dw Mono Printer", "brand": "HP", "price_pkr": (65000, 85000), "desc": "38ppm, automatic duplex, WiFi, Ethernet, USB, 1200dpi resolution, 4.3-inch touchscreen"},
            {"name": "Epson EcoTank L3250 All-in-One Printer", "brand": "Epson", "price_pkr": (42000, 58000), "desc": "Print/scan/copy, 33ppm, 5760dpi, 7500-page black ink tank, WiFi, mobile printing"},
            {"name": "Interwood Executive Office Chair Ergonomic", "brand": "Interwood", "price_pkr": (35000, 55000), "desc": "Lumbar support, adjustable armrests, breathable mesh back, height adjustment, 120kg capacity"},
            {"name": "Avery A4 Labels 100 Sheets 24 Per Sheet", "brand": "Avery", "price_pkr": (1800, 3200), "desc": "2400 labels, 63.5x33.9mm, permanent adhesive, compatible with all inkjet and laser printers"},
            {"name": "Leitz 180° Binder A4 50mm", "brand": "Leitz", "price_pkr": (1500, 2800), "desc": "50mm capacity (500 sheets), 180° opening mechanism, smooth ring action, cardboard cover"},
            {"name": "4x4ft Magnetic Whiteboard with Stand", "brand": "Deli", "price_pkr": (18500, 28000), "desc": "Magnetic surface, height-adjustable stand, includes 4 markers and eraser, folds flat for storage"},
            {"name": "Scotch Magic Tape 19mm x 33m x6 Rolls", "brand": "3M", "price_pkr": (1200, 2200), "desc": "Invisible tape, matte finish, writeable, hand-tearable, 6-roll pack, acid-free, archival safe"},
            {"name": "Stapler Heavy Duty 100-Sheet Capacity", "brand": "Rapid", "price_pkr": (4500, 7200), "desc": "Staples up to 100 sheets, uses standard 26/6 staples, 5-year warranty, built-in staple remover"},
        ],
        "base_discount_chance": 0.22,
    },
    
    "Gaming": {
        "icon": "fa-gamepad",
        "slug": "gaming",
        "color": "#673AB7",
        "subcategories": ["Consoles", "Games", "Controllers", "Gaming Chairs", "Accessories"],
        "products": [
            {"name": "PlayStation 5 Console Disc Edition", "brand": "Sony", "price_pkr": (145000, 175000), "desc": "Custom AMD CPU/GPU, 825GB SSD, 120Hz 8K output, DualSense controller, ray tracing, 3D audio"},
            {"name": "Xbox Series X 1TB Console", "brand": "Microsoft", "price_pkr": (135000, 165000), "desc": "Custom 3.8GHz AMD Zen 2, 12 teraflops GPU, 1TB NVMe SSD, Quick Resume, Game Pass ready, 4K 120Hz"},
            {"name": "Nintendo Switch OLED Model", "brand": "Nintendo", "price_pkr": (89000, 110000), "desc": "7-inch OLED screen, 64GB storage, wide adjustable stand, LAN port in dock, enhanced audio"},
            {"name": "FIFA 24 EA Sports PS5", "brand": "EA Sports", "price_pkr": (12500, 18500), "desc": "HyperMotionV technology, full 11v11 stadium data capture, Ultimate Team, career mode, Pro Clubs"},
            {"name": "Call of Duty Modern Warfare III PS5", "brand": "Activision", "price_pkr": (12500, 18500), "desc": "New open combat missions, zombies mode, all MW2 operators/weapons, massive multiplayer maps"},
            {"name": "DualSense PS5 Wireless Controller", "brand": "Sony", "price_pkr": (18500, 24000), "desc": "Haptic feedback, adaptive triggers, built-in microphone, motion sensors, USB-C, 12-hour battery"},
            {"name": "Secretlab TITAN Evo XL Gaming Chair", "brand": "Secretlab", "price_pkr": (155000, 195000), "desc": "4-way L-ADAPT lumbar support, dual XL armrests, NEO Hybrid Leatherette, 5-year warranty, 180° recliner"},
            {"name": "Razer Kraken V3 Gaming Headset", "brand": "Razer", "price_pkr": (22000, 32000), "desc": "THX Spatial Audio, HyperSense haptics, 50mm drivers, THX certified, HyperClear mic, USB connection"},
        ],
        "base_discount_chance": 0.25,
    },
    
    "Pet Supplies": {
        "icon": "fa-paw",
        "slug": "pets",
        "color": "#FF9800",
        "subcategories": ["Dog Food", "Cat Food", "Accessories", "Grooming", "Health", "Toys"],
        "products": [
            {"name": "Royal Canin Medium Adult Dog Food 15kg", "brand": "Royal Canin", "price_pkr": (18500, 26000), "desc": "Tailored for medium adult dogs 11-25kg, highly digestible proteins, omega-3 and -6, prebiotics"},
            {"name": "Pedigree Adult Dry Dog Food Chicken 10kg", "brand": "Pedigree", "price_pkr": (8500, 13500), "desc": "Chicken and vegetables, antioxidant rich, dental health support, vitamins and minerals fortified"},
            {"name": "Whiskas Ocean Fish Cat Food 1.2kg", "brand": "Whiskas", "price_pkr": (2800, 4500), "desc": "Ocean fish flavor, balanced nutrition, taurine for heart health, omega-6 for coat shine, ages 1+"},
            {"name": "Vitakraft Parrot Food Mix Premium 1kg", "brand": "Vitakraft", "price_pkr": (1800, 3200), "desc": "8 grain types, fruit and vegetables, no artificial colors, natural oils for feather health"},
            {"name": "Remu Easy Clean Litter Box with Cover", "brand": "Catit", "price_pkr": (5500, 8500), "desc": "Hooded design, door entrance, charcoal filter, includes litter scoop, large 45cm x 35cm"},
        ],
        "base_discount_chance": 0.20,
    },
}

# ═══════════════════════════════════════════════════════
# REALISTIC DESCRIPTIONS GENERATOR
# ═══════════════════════════════════════════════════════

def generate_product_description(product_name, brand, category_name, base_desc):
    """Generate extended realistic description."""
    extra_phrases = [
        f"Originally manufactured by {brand}, this product meets international quality standards.",
        "Comes with manufacturer's warranty and 30-day return policy.",
        "Authentic product — 100% original with hologram seal.",
        f"A best-seller in {category_name} category with thousands of satisfied customers.",
        "Fast delivery available across Pakistan including Lahore, Karachi, Islamabad, Peshawar, Quetta.",
        "Cash on delivery available. Easy installment plans for credit card holders.",
    ]
    return base_desc + " " + random.choice(extra_phrases)


class Command(BaseCommand):
    help = 'Seed database with Amazon-scale real-world product data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=50000,
            help='Total number of products to generate (default: 50000, max: 500000)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=1000,
            help='Number of test users to create (default: 1000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick mode: 500 products, 50 users, for testing'
        )

    def handle(self, *args, **options):
        from store.models import Category, Product, UserInteraction, Order, Feedback, Recommendation, DiscountBanner, UserProfile
        
        if options['quick']:
            options['products'] = 500
            options['users'] = 50
            self.stdout.write("⚡ Quick mode: 500 products, 50 users")
        
        total_products_target = min(options['products'], 500000)
        total_users_target = options['users']
        
        if options['clear']:
            self.stdout.write("🗑️  Clearing existing data...")
            UserInteraction.objects.all().delete()
            Recommendation.objects.all().delete()
            Order.objects.all().delete()
            Feedback.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            DiscountBanner.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("✓ Data cleared"))
        
        self.stdout.write(f"\n🚀 Starting Amazon-scale data seeding...")
        self.stdout.write(f"   Target: {total_products_target:,} products, {total_users_target:,} users\n")
        
        # ── STEP 1: CATEGORIES ──
        self.stdout.write("📂 Step 1/6: Creating categories...")
        created_categories = {}
        for cat_name, cat_data in PRODUCT_CATALOG.items():
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug': cat_data['slug'],
                    'description': f"Shop the best {cat_name} products in Pakistan. Genuine products, best prices, fast delivery.",
                    'icon': cat_data['icon'],
                }
            )
            created_categories[cat_name] = cat
        self.stdout.write(self.style.SUCCESS(f"   ✓ {len(created_categories)} categories created"))
        
        # ── STEP 2: BASE PRODUCTS (from catalog) ──
        self.stdout.write("📦 Step 2/6: Creating base real-world products...")
        base_products_created = 0
        all_base_product_ids = []
        
        for cat_name, cat_data in PRODUCT_CATALOG.items():
            category = created_categories[cat_name]
            discount_chance = cat_data['base_discount_chance']
            
            for p_data in cat_data['products']:
                price_range = p_data['price_pkr']
                if isinstance(price_range, tuple):
                    base_price = Decimal(str(random.randint(price_range[0], price_range[1])))
                else:
                    base_price = Decimal(str(price_range))
                
                original_price = base_price * Decimal(str(round(random.uniform(1.08, 1.35), 2)))
                is_discount = random.random() < discount_chance
                discount_pct = random.randint(5, 40) if is_discount else 0
                
                attrs = {
                    "brand": p_data.get('brand', ''),
                    "warranty": random.choice(["6 months", "1 year", "2 years", "No warranty"]),
                    "color": random.choice(["Black", "White", "Silver", "Gray", "Blue", "Red", "Green", ""]),
                    "condition": "Brand New",
                    "availability": "In Stock",
                }
                
                try:
                    product = Product.objects.get_or_create(
                        name=p_data['name'],
                        defaults={
                            'category': category,
                            'description': generate_product_description(p_data['name'], p_data.get('brand',''), cat_name, p_data['desc']),
                            'price': base_price,
                            'original_price': original_price.quantize(Decimal('0.01')),
                            'stock_level': random.randint(15, 500),
                            'is_available': True,
                            'is_featured': random.random() < 0.08,
                            'is_on_discount': is_discount,
                            'discount_percentage': discount_pct,
                            'rating': Decimal(str(round(random.uniform(3.2, 5.0), 1))),
                            'attributes': attrs,
                        }
                    )[0]
                    all_base_product_ids.append(product.product_id)
                    base_products_created += 1
                except Exception as e:
                    pass
        
        self.stdout.write(self.style.SUCCESS(f"   ✓ {base_products_created} base products created"))
        
        # ── STEP 3: BULK GENERATE ADDITIONAL PRODUCTS ──
        remaining_needed = total_products_target - base_products_created
        
        if remaining_needed > 0:
            self.stdout.write(f"🔄 Step 3/6: Bulk generating {remaining_needed:,} additional products...")
            
            BULK_TEMPLATES = {
                "Electronics": [
                    ("USB-C Hub {n}-Port", "Anker", (2800, 8500)),
                    ("Wireless Charger 15W Fast {n}mm", "Baseus", (2200, 6500)),
                    ("Phone Case Model {n} Premium", "Spigen", (1200, 3500)),
                    ("Screen Protector Tempered Glass {n}-Pack", "ZAGG", (800, 2200)),
                    ("Power Bank {n}0000mAh", "Anker", (5500, 18500)),
                    ("HDMI Cable 4K {n}M Premium", "AmazonBasics", (850, 3500)),
                    ("Bluetooth Speaker IP{n}7 Waterproof", "JBL", (5500, 22000)),
                    ("Smart Plug WiFi {n}-Pack", "TP-Link", (1800, 5500)),
                    ("Webcam {n}080p HD Autofocus", "Logitech", (5500, 22000)),
                    ("SSD {n}TB External Portable", "Samsung", (18500, 48000)),
                ],
                "Fashion & Clothing": [
                    ("Lawn Suit Unstitched 3PC Design-{n}", "Alkaram", (2200, 6500)),
                    ("Men's Casual Shirt Style {n}", "Bonanza", (2800, 7500)),
                    ("Women's Embroidered Dupatta {n}", "Nishat", (1200, 3500)),
                    ("Kurta Shalwar Eid Collection {n}", "Gul Ahmed", (4500, 9500)),
                    ("Sneakers Sports Model-{n}", "Nike", (8500, 22000)),
                    ("Handbag Leather Style {n}", "Guess", (8500, 28000)),
                    ("Jeans Slim Fit Shade {n}", "Levi's", (5500, 14000)),
                    ("Winter Sweater Knitted {n}", "Next", (3800, 9500)),
                ],
                "Home & Kitchen": [
                    ("Storage Box Organizer Set-{n}", "IKEA", (1800, 5500)),
                    ("Bedsheet Cotton {n}00 Thread Count", "Sapphire", (3500, 8500)),
                    ("Air Freshener Automatic Spray {n}ml", "Glade", (1200, 3200)),
                    ("Cleaning Kit {n}-Piece Multi-Surface", "Dettol", (1500, 4500)),
                    ("Cutlery Set {n}2-Piece Stainless Steel", "WMF", (3500, 12500)),
                    ("Curtains {n}x7ft Block Print Pair", "Home Centre", (2800, 8500)),
                    ("Decorative Cushion Cover {n}-Pack", "H&M Home", (1200, 3500)),
                ],
                "Books & Stationery": [
                    ("IELTS Preparation Guide Edition {n}", "Cambridge", (2200, 4500)),
                    ("Urdu Novel Classic Collection Vol.{n}", "Sang-e-Meel", (650, 1800)),
                    ("Islamic Book Hadith Collection {n}", "Maktaba", (1200, 3500)),
                    ("Children's Story Book Set {n}", "Penguin Kids", (850, 2800)),
                    ("Notebook A5 Ruled Pack of {n}", "Paperpillar", (450, 1200)),
                    ("Colored Pens Set {n}0-Pack", "Staedtler", (1200, 3500)),
                ],
                "Sports & Outdoor": [
                    ("Resistance Bands Set {n}-Levels", "Fit Simply", (1200, 3800)),
                    ("Yoga Mat Extra Thick {n}mm", "Lululemon", (3500, 9500)),
                    ("Cricket Batting Pad {n}-Piece Set", "Gray-Nicolls", (5500, 14000)),
                    ("Football Shoes Size {n}", "Adidas", (8500, 22000)),
                    ("Protein Bar Box {n}x60g", "Clif Bar", (3500, 6500)),
                    ("Jump Rope Speed Adjustable {n}cm", "RDX", (850, 3500)),
                ],
                "Food & Grocery": [
                    ("Masala Mix Pack {n} Varieties", "Shan", (650, 1800)),
                    ("Organic Honey Raw {n}00g", "Pure Land", (1200, 3500)),
                    ("Dry Fruits Gift Box {n}00g Premium", "Nutri Valley", (3500, 8500)),
                    ("Green Tea Premium {n}0 Bags", "Tapal", (450, 1500)),
                    ("Jam Spread {n} Flavors Pack", "Mitchell's", (650, 1800)),
                    ("Biscuits Assorted Pack {n}kg", "Bisconni", (850, 2200)),
                ],
            }
            
            categories_list = list(created_categories.items())
            products_to_create = []
            batch_size = 5000
            generated_count = 0
            
            while generated_count < remaining_needed:
                batch_to_generate = min(batch_size, remaining_needed - generated_count)
                
                for _ in range(batch_to_generate):
                    cat_name, category = random.choice(categories_list)
                    
                    templates = BULK_TEMPLATES.get(cat_name, [("Product Model {n}", "Generic", (1000, 15000))])
                    template = random.choice(templates)
                    n = random.randint(1, 999)
                    
                    product_name = template[0].replace('{n}', str(n))
                    brand = template[1]
                    price_range = template[2]
                    base_price = Decimal(str(random.randint(price_range[0], price_range[1])))
                    original_price = base_price * Decimal(str(round(random.uniform(1.05, 1.40), 2)))
                    is_discount = random.random() < 0.30
                    
                    products_to_create.append(Product(
                        name=product_name,
                        category=category,
                        description=f"Premium {product_name} by {brand}. Genuine product with manufacturer warranty. Fast delivery across Pakistan.",
                        price=base_price,
                        original_price=original_price.quantize(Decimal('0.01')),
                        stock_level=random.randint(5, 300),
                        is_available=True,
                        is_featured=random.random() < 0.05,
                        is_on_discount=is_discount,
                        discount_percentage=random.randint(5, 40) if is_discount else 0,
                        rating=Decimal(str(round(random.uniform(3.0, 5.0), 1))),
                        attributes={"brand": brand, "condition": "Brand New"},
                    ))
                
                with transaction.atomic():
                    created = Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
                    all_base_product_ids.extend([p.product_id for p in created if p.product_id])
                
                generated_count += len(products_to_create)
                products_to_create = []
                
                if generated_count % 50000 == 0:
                    self.stdout.write(f"   Progress: {generated_count:,} / {remaining_needed:,} ({100*generated_count//remaining_needed}%)")
            
            self.stdout.write(self.style.SUCCESS(f"   ✓ {remaining_needed:,} additional products generated"))
        
        total_products = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\n   📦 TOTAL PRODUCTS IN DATABASE: {total_products:,}"))
        
        # ── STEP 4: USERS ──
        self.stdout.write(f"\n👥 Step 4/6: Creating {total_users_target:,} users...")
        
        # Admin first
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@aishop.com', 'admin@123')
            self.stdout.write("   ✓ Admin created: username=admin, password=admin@123")
        
        # Test user
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user('testuser', 'test@aishop.com', 'test@123', first_name='Test', last_name='User')
        
        # Bulk users using Faker
        users_to_create = []
        existing_usernames = set(User.objects.values_list('username', flat=True))
        
        for i in range(total_users_target):
            username = f"user_{fake.unique.user_name()[:12]}_{i}"[:30]
            if username not in existing_usernames:
                users_to_create.append(User(
                    username=username,
                    email=f"user{i}@example.com",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_active=True,
                ))
                existing_usernames.add(username)
        
        with transaction.atomic():
            created_users = User.objects.bulk_create(users_to_create, ignore_conflicts=True)
        
        # Set passwords in bulk (simplified)
        for user in created_users[:100]:  # Only set passwords for first 100 for demo
            user.set_password('testpass123')
            user.save(update_fields=['password'])
        
        all_user_ids = list(User.objects.filter(is_superuser=False).values_list('id', flat=True))
        self.stdout.write(self.style.SUCCESS(f"   ✓ {len(all_user_ids):,} users created"))
        
        # ── STEP 5: USER INTERACTIONS (for ML training) ──
        self.stdout.write("\n🤖 Step 5/6: Creating user interactions for ML training...")
        
        all_product_ids = list(Product.objects.values_list('product_id', flat=True)[:10000])  # Use first 10k products
        interaction_types = ['view', 'view', 'view', 'cart', 'purchase', 'like', 'search']
        
        interactions_to_create = []
        INTERACTIONS_PER_USER = 25
        
        sample_users = all_user_ids[:min(5000, len(all_user_ids))]
        
        for user_id in sample_users:
            user_products = random.sample(all_product_ids, min(INTERACTIONS_PER_USER, len(all_product_ids)))
            for product_id in user_products:
                interactions_to_create.append(UserInteraction(
                    user_id=user_id,
                    product_id=product_id,
                    interaction_type=random.choice(interaction_types),
                    interaction_count=random.randint(1, 8),
                ))
        
        with transaction.atomic():
            UserInteraction.objects.bulk_create(interactions_to_create, ignore_conflicts=True, batch_size=10000)
        
        self.stdout.write(self.style.SUCCESS(f"   ✓ {len(interactions_to_create):,} interactions created"))
        
        # ── STEP 6: ORDERS + FEEDBACK ──
        self.stdout.write("\n🛒 Step 6/6: Creating orders and feedback...")
        
        CITIES = ["Lahore", "Karachi", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar", "Quetta", "Sialkot", "Hyderabad", "Gujranwala", "Abbottabad"]
        ORDER_STATUSES = ['pending', 'confirmed', 'shipped', 'delivered', 'delivered', 'delivered']
        
        orders_to_create = []
        feedback_to_create = []
        
        for user_id in sample_users[:2000]:
            num_orders = random.randint(1, 8)
            for _ in range(num_orders):
                product_id = random.choice(all_product_ids)
                try:
                    product = Product.objects.get(product_id=product_id)
                    qty = random.randint(1, 3)
                    orders_to_create.append(Order(
                        user_id=user_id,
                        product=product,
                        quantity=qty,
                        total_price=product.price * qty,
                        delivery_address=fake.address()[:200],
                        city=random.choice(CITIES),
                        status=random.choice(ORDER_STATUSES),
                    ))
                    
                    # Add feedback for delivered orders
                    if random.random() < 0.5:
                        feedback_to_create.append(Feedback(
                            user_id=user_id,
                            product=product,
                            rating=random.randint(3, 5),
                            comment=random.choice([
                                "Great product! Exactly as described. Fast delivery.",
                                "Good quality for the price. Satisfied with purchase.",
                                "Original product. Highly recommend.",
                                "Fast delivery, product quality is excellent.",
                                "Loved it! Will buy again.",
                                "Good value for money. Works perfectly.",
                                "Product is genuine. Happy with purchase.",
                                "Excellent quality. Delivery was on time.",
                                "",  # Some without comment
                            ]),
                        ))
                except Product.DoesNotExist:
                    continue
        
        with transaction.atomic():
            Order.objects.bulk_create(orders_to_create, ignore_conflicts=True, batch_size=5000)
            Feedback.objects.bulk_create(feedback_to_create, ignore_conflicts=True, batch_size=5000)
        
        self.stdout.write(self.style.SUCCESS(f"   ✓ {len(orders_to_create):,} orders + {len(feedback_to_create):,} reviews created"))
        
        # ── DISCOUNT BANNERS ──
        DiscountBanner.objects.get_or_create(
            title="MEGA SALE - Pakistan's Biggest Online Sale!",
            defaults={
                'description': "Up to 70% off on Electronics, Fashion, Home & more. Limited time offer!",
                'discount_percentage': 70,
                'start_time': timezone.now(),
                'end_time': timezone.now() + timedelta(days=7),
                'is_active': True,
            }
        )
        DiscountBanner.objects.get_or_create(
            title="Eid Special: 40% OFF on All Fashion",
            defaults={
                'description': "Eid Mubarak! Flat 40% off on all lawn suits, kurtas, and footwear.",
                'discount_percentage': 40,
                'start_time': timezone.now(),
                'end_time': timezone.now() + timedelta(days=14),
                'is_active': True,
            }
        )
        
        # ── GENERATE AI RECOMMENDATIONS ──
        self.stdout.write("\n🤖 Generating AI recommendations...")
        try:
            from store.recommendation_engine import RecommendationEngine
            engine = RecommendationEngine()
            count = engine.generate_all_recommendations()
            self.stdout.write(self.style.SUCCESS(f"   ✓ Recommendations generated for {count} users"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠ Recommendations skipped (run manually): {e}"))
        
        # ── FINAL SUMMARY ──
        self.stdout.write("\n" + "="*55)
        self.stdout.write(self.style.SUCCESS("🎉 DATABASE SEEDING COMPLETE!"))
        self.stdout.write("="*55)
        self.stdout.write(f"📦 Products:     {Product.objects.count():>10,}")
        self.stdout.write(f"📂 Categories:   {Category.objects.count():>10,}")
        self.stdout.write(f"👥 Users:        {User.objects.count():>10,}")
        self.stdout.write(f"🔄 Interactions: {UserInteraction.objects.count():>10,}")
        self.stdout.write(f"🛒 Orders:       {Order.objects.count():>10,}")
        self.stdout.write(f"⭐ Reviews:      {Feedback.objects.count():>10,}")
        self.stdout.write("="*55)
        self.stdout.write("\n🔐 LOGIN CREDENTIALS:")
        self.stdout.write("   Admin:    username=admin,    password=admin@123")
        self.stdout.write("   Test User: username=testuser, password=test@123")
        self.stdout.write("\n🌐 Start server: python manage.py runserver")
        self.stdout.write("   Website: http://127.0.0.1:8000/")
        self.stdout.write("   Admin:   http://127.0.0.1:8000/django-admin/\n")
```

---

## ALSO CREATE: store/management/commands/add_search_api.py

This adds a search suggestions API endpoint used by the autocomplete JS:

```python
# In store/views.py add this view:
def search_suggestions_api(request):
    """
    AJAX API: Returns product name suggestions for search autocomplete.
    URL: /api/search-suggestions/?q=samsung
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = Product.objects.filter(
        name__icontains=query,
        is_available=True
    ).values('name', 'product_id', 'category__name').distinct()[:8]
    
    return JsonResponse({
        'suggestions': [
            {
                'name': s['name'],
                'id': s['product_id'],
                'category': s['category__name'],
                'url': f'/products/{s["product_id"]}/'
            }
            for s in suggestions
        ]
    })
```

Add to urls.py:
path('api/search-suggestions/', views.search_suggestions_api, name='search_suggestions'),

Write COMPLETE management command code. Every line of code. Production quality.
```

---

---

# ═══════════════════════════════════════════════
# 📋 HOW TO RUN — COMPLETE COMMANDS
# ═══════════════════════════════════════════════

## Quick Test (500 products, takes ~30 seconds):
```bash
pip install Faker tqdm
python manage.py seed_database --quick
python manage.py runserver
```

## Medium Scale (50,000 products, takes ~3 minutes):
```bash
python manage.py seed_database --products 50000 --users 1000
```

## Full Amazon Scale (500,000 products, takes ~20 minutes):
```bash
python manage.py seed_database --products 500000 --users 5000
```

## Clear and reseed:
```bash
python manage.py seed_database --clear --products 50000
```

---

## WHAT YOU GET:
```
📦 500,000 products with real names, brands, descriptions, prices in PKR
📂 13 Amazon-like categories (Electronics, Fashion, Home, Books, etc.)
🏷️  Real brands: Samsung, Apple, Gul Ahmed, Dawlance, L'Oreal, etc.
💰 Realistic Pakistani prices (Rs. 120 to Rs. 459,000)
👥 1000+ test users with interaction history
🛒 Realistic orders with Pakistani cities
⭐ Product reviews and ratings
🤖 AI recommendations pre-generated for all users
```

---

---

---

# ═══════════════════════════════════════════════════════════
# PROMPT 15 — FINAL INTEGRATION, TESTING & DEPLOYMENT
# ═══════════════════════════════════════════════════════════

```
You are a senior Django developer. The entire project is built. 
Now do the COMPLETE final integration, testing, and deployment preparation.

=== PART A: FINAL INTEGRATION CHECKLIST ===

Check and fix ALL these points:

### 1. Image Display Verification
In ai_product_platform/urls.py, confirm this line exists:
urlpatterns = [...] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

In settings.py confirm:
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

Test: Upload a product image in admin → visit product page → image should show.
If image NOT showing: most likely cause is missing static() line in urls.py.

### 2. Template Tag Loading
Every template that uses store_tags MUST have:
{% load static store_tags %}

### 3. Context Processor for Cart
Add custom context processor for cart count (available in ALL templates):

In store/context_processors.py:
def cart_context(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    return {'cart_count': cart_count}

In settings.py TEMPLATES > OPTIONS > context_processors, add:
'store.context_processors.cart_context',

### 4. Categories in All Templates
Add to context processor:
from .models import Category
def global_context(request):
    return {
        'all_categories': Category.objects.all()[:8],
        'cart_count': cart_count,
    }

### 5. Messages Framework
Confirm in settings.py:
MIDDLEWARE includes: 'django.contrib.messages.middleware.MessageMiddleware'
TEMPLATES context_processors includes: 'django.contrib.messages.context_processors.messages'

=== PART B: FINAL VIEWS.PY CLEANUP ===

Make sure ALL imports at top of views.py are present:
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from .models import (Category, Product, UserInteraction, Recommendation, 
                     Order, Feedback, UserProfile)
from .forms import (UserSignupForm, UserLoginForm, UserProfileUpdateForm,
                    ProductSearchForm, OrderForm, FeedbackForm, ProductForm)
from .recommendation_engine import RecommendationEngine, get_quick_recommendations

=== PART C: RUN EVERYTHING IN ORDER ===

Give me the EXACT commands to run after setup:

1. python manage.py makemigrations
2. python manage.py migrate
3. python manage.py createsuperuser
4. python manage.py seed_data
5. python manage.py generate_recommendations
6. python manage.py collectstatic (for production)
7. python manage.py runserver

=== PART D: DEPLOYMENT CHECKLIST ===

For hosting on Heroku or Railway.app:

1. Procfile:
   web: gunicorn ai_product_platform.wsgi

2. requirements.txt (generate with pip freeze > requirements.txt)

3. settings.py production changes:
   - DEBUG = False
   - ALLOWED_HOSTS = ['your-domain.com', 'your-app.herokuapp.com']
   - Use environment variables for SECRET_KEY:
     import os
     SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key-for-dev')
   - Static files: install whitenoise + add to MIDDLEWARE
   - Database: optionally upgrade to PostgreSQL on Heroku

4. Media files for production:
   - Option A: Cloudinary (free tier, best for images)
   - Option B: AWS S3
   - Add django-cloudinary-storage or django-storages

5. Environment variables needed:
   SECRET_KEY, DATABASE_URL, DEBUG=False

=== PART E: COMPLETE TEST CHECKLIST ===

Test every feature:

AUTHENTICATION:
☐ Signup creates User + UserProfile
☐ Login works, session persists
☐ Logout clears session
☐ Profile update saves correctly

PRODUCTS:
☐ Product list shows all available products
☐ Product images display (CRITICAL CHECK)
☐ Category filter works
☐ Search works
☐ Sorting works (price, rating, discount)
☐ Pagination works

AI RECOMMENDATIONS:
☐ seed_data ran with interactions
☐ generate_recommendations ran
☐ Logged-in user sees "For You" recommendations on home page
☐ Visiting a product logs 'view' interaction
☐ Adding to cart logs 'cart' interaction
☐ Placing order logs 'purchase' interaction
☐ /recommendations/ page shows personalized products with ML scores
☐ Refresh recommendations AJAX works
☐ Guest users see popular products instead

ORDERS:
☐ Add to cart (AJAX, cart badge updates)
☐ Cart page shows items correctly
☐ Place order decreases stock
☐ Order history shows all orders

FEEDBACK:
☐ Only purchased users can submit feedback
☐ Can't submit twice
☐ Rating updates product average rating
☐ Feedback logs 'like' interaction

ADMIN PANEL:
☐ /admin-panel/ requires staff login
☐ Add product with image upload works
☐ Edit product preserves existing image if none uploaded
☐ Delete product works
☐ Analytics charts display

=== PART F: QUICK START COMMANDS REFERENCE ===

# Full reset and fresh start:
python manage.py flush --no-input
python manage.py migrate
python manage.py seed_data
python manage.py generate_recommendations
python manage.py runserver

# Then visit:
# http://127.0.0.1:8000/          ← Home page
# http://127.0.0.1:8000/django-admin/   ← Django built-in admin
# http://127.0.0.1:8000/admin-panel/    ← Custom admin panel
# Login: testuser1 / password123

Write ALL fix code completely. Every file fully corrected and production-ready.
```

---

---

# 📊 COMPLETE PROJECT SUMMARY

## What This Project Builds:
A **full-stack AI-powered e-commerce website** with:

| Feature | Technology |
|---------|-----------|
| Web Framework | Django 4.2 |
| Database | SQLite (upgradeable to PostgreSQL) |
| ML Engine | Scikit-learn (Collaborative + Content-Based + Hybrid) |
| Frontend | HTML5 + CSS3 + Bootstrap 5 + JavaScript |
| Image Storage | Django MediaFiles (local) |
| Auth | Django built-in + custom UserProfile |
| Admin | Django Admin + Custom Admin Panel |

## Database Tables:
1. `store_category` — Product categories
2. `store_product` — Products with images
3. `store_userprofile` — Extended user profiles
4. `store_userinteraction` — ML training data
5. `store_recommendation` — ML-generated recommendations
6. `store_order` — Customer orders
7. `store_feedback` — Product reviews/ratings

## AI Recommendation Flow:
```
User visits product → view logged → 
RecommendationEngine runs → 
Collaborative Filtering + Content-Based Filtering →
Hybrid merge → Saved to DB →
Displayed as "For You" section on home + product pages
```

## Image Display (How It Works):
```
Admin uploads image via Django Admin
→ Saved to: media/products/filename.jpg
→ In template: {{ product.image.url }} = "/media/products/filename.jpg"
→ Django serves via: + static(MEDIA_URL, document_root=MEDIA_ROOT) in urls.py
→ Browser displays correctly ✅
```

---
