from django import template

register = template.Library()

@register.filter(name="has_user_type")
def has_user_type(user, expected_code: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    user_type = getattr(user, "user_type", None)
    if not user_type:
        return False
    # user_type has fields: code, name
    return str(getattr(user_type, "code", "")).lower() == str(expected_code or "").lower()

@register.filter(name="has_subscription")
def has_subscription(user, expected_code: str) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    subscription = getattr(user, "subscription", None)
    if not subscription:
        return False
    if hasattr(subscription, "is_active") and not subscription.is_active:
        return False
    subscription_type = getattr(subscription, "subscription_type", None)
    if not subscription_type:
        return False
    return str(getattr(subscription_type, "code", "")).lower() == str(expected_code or "").lower()
