# pyright: reportIncompatibleMethodOverride=false
from rest_framework.permissions import BasePermission
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.conf import settings

class SubscriptionActive(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, 'billing_profile', None)
        return bool(profile and profile.status == 'active')


def subscription_required(view_func):
    """Basit abonelik kontrolü (function-based views için).

    Kullanıcı giriş yapmamışsa login'e, aboneliği aktif değilse planlara yönlendirir.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            try:
                login_url = reverse('login')
            except NoReverseMatch:
                login_url = getattr(settings, 'LOGIN_URL', '/accounts/login/')
            return redirect(f"{login_url}?next={request.path}")
        profile = getattr(user, 'billing_profile', None)
        if not (profile and profile.status == 'active'):
            return redirect('billing:plans')
        return view_func(request, *args, **kwargs)
    return _wrapped
