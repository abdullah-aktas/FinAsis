from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Sadece admin kullanıcıların yazma izni vardır.
    Diğer kullanıcılar sadece okuma yapabilir.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsCheckOwner(permissions.BasePermission):
    """
    Sadece kontrol sahibi veya admin kullanıcıların
    yazma izni vardır.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or obj.created_by == request.user

class CanRunChecks(permissions.BasePermission):
    """
    Kontrol çalıştırma izni olan kullanıcılar için.
    """
    def has_permission(self, request, view):
        if request.method == 'POST' and view.action == 'run':
            return request.user.has_perm('checks.run_checks')
        return True

class CanScheduleChecks(permissions.BasePermission):
    """
    Kontrol zamanlama izni olan kullanıcılar için.
    """
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.has_perm('checks.schedule_checks')
        return True

class CanViewCheckResults(permissions.BasePermission):
    """
    Kontrol sonuçlarını görüntüleme izni olan kullanıcılar için.
    """
    def has_permission(self, request, view):
        if view.action == 'statistics':
            return request.user.has_perm('checks.view_check_results')
        return True 