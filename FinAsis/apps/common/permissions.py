from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Sadece objenin sahibi düzenleme yapabilir, diğer kullanıcılar sadece okuyabilir.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.owner == request.user 