from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse

# Admin yetkisi kontrolü
def is_admin(user):
    return user.is_staff or user.is_superuser

# Tüm admin görünümlerinde kullanılan decorator
def admin_required(view_func):
    decorated_view = login_required(user_passes_test(is_admin)(view_func))
    return decorated_view

@admin_required
def admin_index(request):
    """Admin paneli ana sayfası."""
    context = {
        'active_menu': 'dashboard',
    }
    return render(request, 'admin/index.html', context)

@admin_required
def admin_users_list(request):
    """Kullanıcı listesi sayfası."""
    # Bu fonksiyon normalde User modelinden kullanıcıları çeker
    # Ancak basitlik için şu an context'i boş bırakıyoruz
    context = {
        'active_menu': 'users',
        'active_submenu': 'users_list',
    }
    return render(request, 'admin/users/list.html', context)

@admin_required
def admin_users_add(request):
    """Kullanıcı ekleme sayfası."""
    context = {
        'active_menu': 'users',
        'active_submenu': 'users_add',
    }
    return render(request, 'admin/users/add.html', context)

@admin_required
def admin_permissions(request):
    """İzinler sayfası."""
    context = {
        'active_menu': 'users',
        'active_submenu': 'permissions',
    }
    return render(request, 'admin/users/permissions.html', context)

@admin_required
def admin_transactions(request):
    """İşlemler sayfası."""
    context = {
        'active_menu': 'finance',
        'active_submenu': 'transactions',
    }
    return render(request, 'admin/finance/transactions.html', context)

@admin_required
def admin_reports(request):
    """Raporlar sayfası."""
    context = {
        'active_menu': 'finance',
        'active_submenu': 'reports',
    }
    return render(request, 'admin/finance/reports.html', context)

@admin_required
def admin_settings(request):
    """Ayarlar sayfası."""
    context = {
        'active_menu': 'system',
        'active_submenu': 'settings',
    }
    return render(request, 'admin/system/settings.html', context)

@admin_required
def admin_logs(request):
    """Sistem kayıtları sayfası."""
    context = {
        'active_menu': 'system',
        'active_submenu': 'logs',
    }
    return render(request, 'admin/system/logs.html', context)

@admin_required
def admin_backups(request):
    """Yedekleme sayfası."""
    context = {
        'active_menu': 'system',
        'active_submenu': 'backups',
    }
    return render(request, 'admin/system/backups.html', context)

@admin_required
def admin_integrations(request):
    """Entegrasyonlar sayfası."""
    context = {
        'active_menu': 'integrations',
    }
    return render(request, 'admin/integrations.html', context)

@admin_required
def admin_ai_assistant(request):
    """AI Asistan ayarları sayfası."""
    context = {
        'active_menu': 'ai_assistant',
    }
    return render(request, 'admin/ai_assistant.html', context)

@admin_required
def admin_notifications(request):
    """Bildirimler sayfası."""
    context = {
        'active_menu': 'notifications',
    }
    return render(request, 'admin/notifications.html', context)

@admin_required
def admin_help(request):
    """Yardım merkezi sayfası."""
    context = {}
    return render(request, 'admin/help/index.html', context)

@admin_required
def admin_documentation(request):
    """Dokümantasyon sayfası."""
    context = {}
    return render(request, 'admin/help/documentation.html', context)

@admin_required
def admin_support(request):
    """Destek talebi sayfası."""
    context = {}
    return render(request, 'admin/help/support.html', context)

@admin_required
def admin_profile(request):
    """Kullanıcı profili sayfası."""
    context = {}
    return render(request, 'admin/profile.html', context) 