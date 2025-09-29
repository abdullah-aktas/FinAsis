# -*- coding: utf-8 -*-
"""Audit & Control module custom decorators"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _


def require_roles(*roles):
    """Fonksiyon bazlı view'ler için grup/rol kontrolü.

    Kullanım:
        @require_roles('Admin', 'Accountant')
        def my_view(request): ...

    Superuser her zaman geçer. Kullanıcıda belirtilen rollerden
    en az biri yoksa dashboard'a yönlendirip uyarı verir.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            user_roles = set(request.user.groups.values_list('name', flat=True))
            if not user_roles.intersection(roles):
                messages.error(request, _('Bu işlem için yetkiniz yok.'))
                return redirect('audit:control_dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
