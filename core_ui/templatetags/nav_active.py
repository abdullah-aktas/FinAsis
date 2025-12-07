from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_active(
    context, *patterns, exact=False, startswith=True, classes="active", aria=True
):
    """Return active classes if current path matches any of the given patterns.

    Usage:
        <a class="nav-link {% nav_active '/reports/' '/reports/detail/' %}" ...>
    Options:
        exact=True -> exact path match (ignore trailing slash differences)
        startswith=False -> disable prefix logic
        classes='active current' -> custom classes
    """
    request = context.get("request")
    if not request:
        return ""
    path = request.path
    # Normalize trailing slash
    if not path.endswith("/"):
        path += "/"
    for raw in patterns:
        if not raw:
            continue
        p = raw
        if not p.endswith("/"):
            p += "/"
        matched = False
        if exact and path == p:
            matched = True
        elif startswith and path.startswith(p):
            matched = True
        elif not startswith and not exact and path == p:
            matched = True
        if matched:
            aria_attr = ' aria-current="page"' if aria else ""
            return f" {classes}{aria_attr}"
    return ""
