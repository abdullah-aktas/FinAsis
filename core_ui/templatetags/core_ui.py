from django import template

register = template.Library()


@register.inclusion_tag("core_ui/components/messages.html", takes_context=True)
def render_messages(context):
    """Render Django messages framework messages using a unified component.
    Expects 'messages' in context.
    """
    return {"messages": context.get("messages", [])}
