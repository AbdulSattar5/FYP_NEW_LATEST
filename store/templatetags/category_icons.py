from django import template

from store.utils.category_icons import icon_for_category_slug

register = template.Library()


@register.filter
def category_icon(slug):
    """Return Font Awesome icon class suffix for a category slug (e.g. fa-laptop)."""
    return icon_for_category_slug(str(slug or ''))
