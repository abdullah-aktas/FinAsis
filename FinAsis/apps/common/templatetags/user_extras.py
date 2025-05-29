from django import template

register = template.Library()

@register.filter
def has_user_type(user, type_code):
    return user.is_authenticated and user.user_type and user.user_type.code == type_code

@register.filter
def has_subscription(user, sub_code):
    return user.is_authenticated and hasattr(user, 'subscription') and user.subscription.subscription_type and user.subscription.subscription_type.code == sub_code 