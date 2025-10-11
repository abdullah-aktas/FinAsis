from django import template

register = template.Library()

@register.filter
def currency(value):
    """Değeri TL formatında gösterir."""
    return f"₺{value:,.2f}".replace(",", ".")


@register.filter
def startswith(value, prefix):
    try:
        return str(value).startswith(str(prefix))
    except Exception:
        return False 


@register.filter(name="getattr")
def getattr_filter(obj, key):
    """
    Django template-friendly getattr: {{ obj|getattr:"field" }}
    - Tries attribute access, then dict-style, then integer index access.
    - Returns empty string on failure to keep templates rendering.
    """
    try:
        return getattr(obj, str(key))
    except Exception:
        pass
    try:
        return obj[str(key)]  # type: ignore[index]
    except Exception:
        pass
    try:
        ikey = int(key)
        return obj[ikey]  # type: ignore[index]
    except Exception:
        return ""