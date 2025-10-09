from rest_framework.permissions import BasePermission


class IsCompanyScoped(BasePermission):
    """Kullanıcının bir şirkete bağlı ve authenticated olmasını şart koşar.
    Viewset içinde queryset şirketle sınırlandırılmış olmalı; bu permission
    yalnızca authenticated + company var mı onu garanti eder.
    """
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'company', None))
