"""
Users Modülü - Dekoratörler
---------------------
Bu dosya, Users modülünün dekoratörlerini içerir.
"""

from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

def two_factor_required(view_func):
    """İki faktörlü doğrulama gerektiren view'lar için dekoratör"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        if not request.user.two_factor_enabled:
            messages.warning(request, _('Bu sayfaya erişmek için iki faktörlü doğrulamayı etkinleştirmeniz gerekiyor.'))
            return redirect('users:two_factor_setup')
        
        if not request.session.get('two_factor_verified'):
            messages.warning(request, _('Bu sayfaya erişmek için iki faktörlü doğrulama yapmanız gerekiyor.'))
            return redirect('users:two_factor_verify')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view 