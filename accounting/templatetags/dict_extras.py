from django import template

register = template.Library()


@register.filter(name="get_item")
def get_item(mapping, key):
    """Safely get a value from a dict-like object by key in templates.

    Usage in templates:
        {{ row|get_item:col }}
    """
    try:
        if mapping is None or key is None:
            return ""
        # Handle dict-like objects
        if hasattr(mapping, "get"):
            return mapping.get(key, "")
        # Fallback to attribute access
        return getattr(mapping, str(key), "")
    except Exception:
        return ""
