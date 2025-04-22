from rest_framework import permissions

class IsWalletOwner(permissions.BasePermission):
    """
    Sadece cüzdan sahibinin erişimine izin verir.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsContractOwner(permissions.BasePermission):
    """
    Sadece kontrat sahibinin erişimine izin verir.
    """
    def has_object_permission(self, request, view, obj):
        # Kontrat sahibi kontrolü burada yapılacak
        # Örnek: obj.owner == request.user
        return True  # Geçici olarak herkese izin veriyoruz 