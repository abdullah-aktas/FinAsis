from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def role_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_permission(permission):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Bu sayfaya erişim yetkiniz bulunmamaktadır.")
        return _wrapped_view
    return decorator 