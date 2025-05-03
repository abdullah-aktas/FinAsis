from django.contrib.auth.mixins import UserPassesTestMixin
from functools import wraps

def check_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator

class HasModelPermissionMixin(UserPassesTestMixin):
    permission_type = None # 'add', 'change', 'delete', 'view'
    
    def test_func(self):
        if not self.permission_type:
            return False
            
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        permission = f"{app_label}.{self.permission_type}_{model_name}"
        
        return self.request.user.has_perm(permission)
