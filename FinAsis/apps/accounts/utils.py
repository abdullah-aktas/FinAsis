from django.http import HttpResponseForbidden

def user_type_required(*allowed_types):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.user_type and request.user.user_type.code in allowed_types:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('Bu sayfaya erişim yetkiniz yok.')
        return _wrapped_view
    return decorator


def subscription_type_required(*allowed_types):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and hasattr(request.user, 'subscription') and request.user.subscription.subscription_type and request.user.subscription.subscription_type.code in allowed_types:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden('Bu sayfaya erişim yetkiniz yok.')
        return _wrapped_view
    return decorator 