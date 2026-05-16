from __future__ import annotations

from django.utils.text import slugify

# slug -> Font Awesome 6 icon name (without fa-solid prefix)
CATEGORY_ICON_MAP: dict[str, str] = {
    'all-products': 'fa-table-cells',
    'beauty': 'fa-spa',
    'cameras': 'fa-camera',
    'clothes': 'fa-shirt',
    'clothing': 'fa-shirt',
    'fragrances': 'fa-spray-can-sparkles',
    'furniture': 'fa-couch',
    'groceries': 'fa-basket-shopping',
    'grocery': 'fa-basket-shopping',
    'home-decoration': 'fa-house',
    'home-decor': 'fa-house',
    'kitchen-accessories': 'fa-utensils',
    'kitchen': 'fa-utensils',
    'laptops': 'fa-laptop',
    'mens-shirts': 'fa-shirt',
    'mens-shoes': 'fa-shoe-prints',
    'mens-watches': 'fa-clock',
    'mobile-accessories': 'fa-mobile-screen-button',
    'phones': 'fa-mobile-screen',
    'smartphones': 'fa-mobile-screen',
    'printers-scanners': 'fa-print',
    'storage': 'fa-hard-drive',
    'tv-display': 'fa-tv',
    'television': 'fa-tv',
    'miscellaneous': 'fa-box',
    'electronics': 'fa-laptop',
    'accessories': 'fa-plug',
    'womens-dresses': 'fa-person-dress',
    'womens-shoes': 'fa-shoe-prints',
    'womens-watches': 'fa-clock',
    'womens-bags': 'fa-bag-shopping',
    'sports': 'fa-football',
    'books': 'fa-book',
    'food': 'fa-utensils',
    'toys': 'fa-gamepad',
    'automotive': 'fa-car',
    'uncategorized': 'fa-box',
    'general': 'fa-tag',
}

DEFAULT_CATEGORY_ICON = 'fa-box'


def icon_for_category_slug(slug: str) -> str:
    key = slugify(slug or '').strip().lower()
    if not key:
        return DEFAULT_CATEGORY_ICON
    if key in CATEGORY_ICON_MAP:
        return CATEGORY_ICON_MAP[key]
    for part in key.split('-'):
        if part in CATEGORY_ICON_MAP:
            return CATEGORY_ICON_MAP[part]
    return DEFAULT_CATEGORY_ICON


def icon_for_category_name(name: str) -> str:
    return icon_for_category_slug(slugify(name or ''))
