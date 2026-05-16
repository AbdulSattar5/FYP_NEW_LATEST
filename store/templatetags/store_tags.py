from django import template
from django.templatetags.static import static

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply two values - useful for calculating subtotals"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def currency(value):
    """Format value as currency (Rs.)"""
    try:
        return f"Rs. {float(value):,.0f}"
    except (ValueError, TypeError):
        return "Rs. 0"


@register.filter
def star_range(rating):
    """Return range for star rating loop (1 to 5)"""
    return range(1, 6)


@register.simple_tag
def get_cart_count(request):
    """Get total item count in cart from session"""
    cart = request.session.get('cart', {})
    return sum(item.get('quantity', 1) for item in cart.values())


@register.filter
def category_color(category_name):
    """Return color code for category badge"""
    colors = {
        'Electronics': '#6C63FF',
        'Clothing': '#FF6584',
        'Books': '#43AA8B',
        'Food': '#F8961E',
        'Beauty': '#F72585',
        'Sports': '#4CC9F0',
        'Home & Garden': '#90BE6D',
        'Toys': '#F9C74F',
        'Automotive': '#577590',
        'Phones': '#3F8EFC',
        'Laptops': '#6C63FF',
        'Hi-Fi Speakers': '#00BCD4',
        'Other Electronics': '#607D8B',
    }
    return colors.get(str(category_name), '#6C63FF')


@register.filter
def product_image_url(product):
    """Return a safe product image URL with a default fallback."""
    try:
        if product and getattr(product, 'image', None):
            return product.image.url
        if product:
            attrs = getattr(product, 'attributes', {}) or {}
            if isinstance(attrs, dict):
                external_image = (attrs.get('external_image_url') or attrs.get('image_url') or '').strip()
                if external_image:
                    return external_image
    except (ValueError, AttributeError):
        pass
    return static('images/default-product.svg')
