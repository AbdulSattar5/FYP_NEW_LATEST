from store.models import Category


def global_context(request):
    """
    Global context processor - makes categories and cart count 
    available in all templates
    """
    # Get all categories
    categories = Category.objects.all().order_by('name')
    
    # Calculate cart count from session
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 1) for item in cart.values())
    
    return {
        'all_categories': categories,
        'cart_count': cart_count,
    }
