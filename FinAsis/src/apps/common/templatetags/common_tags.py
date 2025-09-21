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