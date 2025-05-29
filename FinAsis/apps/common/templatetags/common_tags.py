from django import template

register = template.Library()

@register.filter
def currency(value):
    """Değeri TL formatında gösterir."""
    return f"₺{value:,.2f}".replace(",", ".") 