from django import template

register = template.Library()

@register.filter
def hms_from_ms(value):
    try:
        total_ms = int(value)
    except Exception:
        return ''
    if total_ms < 0:
        total_ms = 0
    total_sec = total_ms // 1000
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    return (f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}")
