# -*- coding: utf-8 -*-
"""
Tenancy Views
Multi-Tenant Yönetim Görünümleri
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import timezone

from .models import (
    Tenant,
    TenantSettings,
    TenantBilling,
    TenantAudit,
    TenantUsage
)


@login_required
def tenant_dashboard(request):
    """
    Tenant yönetim dashboard (sadece superuser)
    """
    if not request.user.is_superuser:
        messages.error(request, _('Bu sayfaya erişim yetkiniz yok.'))
        return redirect('dashboard')
    
    # Tüm tenant'lar
    tenants = Tenant.objects.all().order_by('-created_at')
    
    # İstatistikler
    total_tenants = tenants.count()
    active_tenants = tenants.filter(is_active=True).count()
    
    # Son aktiviteler
    recent_audits = TenantAudit.objects.all().order_by('-timestamp')[:20]
    
    context = {
        'tenants': tenants,
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'inactive_tenants': total_tenants - active_tenants,
        'recent_audits': recent_audits,
    }
    
    return render(request, 'tenancy/dashboard.html', context)


@login_required
def tenant_list(request):
    """
    Tenant listesi (sadece superuser)
    """
    if not request.user.is_superuser:
        messages.error(request, _('Bu sayfaya erişim yetkiniz yok.'))
        return redirect('dashboard')
    
    tenants = Tenant.objects.all().order_by('name')
    
    # Filtreleme
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        tenants = tenants.filter(is_active=True)
    elif status_filter == 'inactive':
        tenants = tenants.filter(is_active=False)
    
    plan_filter = request.GET.get('plan')
    if plan_filter:
        tenants = tenants.filter(subscription_plan=plan_filter)
    
    context = {
        'tenants': tenants,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
    }
    
    return render(request, 'tenancy/tenant_list.html', context)


@login_required
def tenant_detail(request, tenant_id):
    """
    Tenant detay sayfası (sadece superuser)
    """
    if not request.user.is_superuser:
        messages.error(request, _('Bu sayfaya erişim yetkiniz yok.'))
        return redirect('dashboard')
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # İlgili kayıtlar
    try:
        settings = TenantSettings.objects.get(tenant=tenant)
    except TenantSettings.DoesNotExist:
        settings = None
    
    billing = TenantBilling.objects.filter(tenant=tenant).order_by('-billing_date')
    audits = TenantAudit.objects.filter(tenant=tenant).order_by('-timestamp')[:50]
    usage = TenantUsage.objects.filter(tenant=tenant).order_by('-usage_date')[:30]
    
    context = {
        'tenant': tenant,
        'settings': settings,
        'billing': billing,
        'audits': audits,
        'usage': usage,
    }
    
    return render(request, 'tenancy/tenant_detail.html', context)


@login_required
def tenant_create(request):
    """
    Yeni tenant oluştur (sadece superuser)
    """
    if not request.user.is_superuser:
        messages.error(request, _('Bu sayfaya erişim yetkiniz yok.'))
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            tenant = Tenant.objects.create(
                name=request.POST.get('name'),
                slug=request.POST.get('slug'),
                domain=request.POST.get('domain', ''),
                subscription_plan=request.POST.get('subscription_plan', 'FREE'),
                is_active=request.POST.get('is_active') == 'on',
            )
            
            # Varsayılan ayarları oluştur
            TenantSettings.objects.create(tenant=tenant)
            
            messages.success(request, _('Tenant başarıyla oluşturuldu.'))
            return redirect('tenancy:tenant_detail', tenant_id=tenant.id)
            
        except Exception as e:
            messages.error(request, _('Tenant oluşturulurken hata: ') + str(e))
    
    context = {
        'subscription_plans': Tenant.SUBSCRIPTION_PLANS,
    }
    
    return render(request, 'tenancy/tenant_create.html', context)


@login_required
def tenant_settings(request, tenant_id):
    """
    Tenant ayarları (sadece superuser veya tenant yöneticisi)
    """
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Yetki kontrolü
    if not request.user.is_superuser:
        # Tenant'a ait kullanıcı mı kontrol et
        if not hasattr(request.user, 'company') or request.user.company.tenant != tenant:
            messages.error(request, _('Bu tenant\'a erişim yetkiniz yok.'))
            return redirect('dashboard')
    
    settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
    
    if request.method == 'POST':
        try:
            settings.custom_domain = request.POST.get('custom_domain', '')
            settings.theme_color = request.POST.get('theme_color', '#3B82F6')
            settings.logo_url = request.POST.get('logo_url', '')
            settings.max_users = int(request.POST.get('max_users', 10))
            settings.max_storage_gb = int(request.POST.get('max_storage_gb', 5))
            settings.features = request.POST.get('features', '{}')
            settings.save()
            
            messages.success(request, _('Ayarlar başarıyla kaydedildi.'))
            return redirect('tenancy:tenant_detail', tenant_id=tenant.id)
            
        except Exception as e:
            messages.error(request, _('Ayarlar kaydedilirken hata: ') + str(e))
    
    context = {
        'tenant': tenant,
        'settings': settings,
    }
    
    return render(request, 'tenancy/tenant_settings.html', context)


@login_required
def ajax_tenant_stats(request, tenant_id):
    """
    AJAX: Tenant istatistikleri
    """
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': _('Yetkiniz yok')
        }, status=403)
    
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        
        # İstatistikler
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        stats = {
            'total_users': User.objects.filter(company__tenant=tenant).count(),
            'active_users': User.objects.filter(
                company__tenant=tenant,
                is_active=True
            ).count(),
            'total_audits': TenantAudit.objects.filter(tenant=tenant).count(),
            'recent_activity': TenantAudit.objects.filter(
                tenant=tenant,
                timestamp__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Tenant.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Tenant bulunamadı')
        }, status=404)


@login_required
def ajax_toggle_tenant_status(request, tenant_id):
    """
    AJAX: Tenant aktif/pasif durumunu değiştir
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': _('Sadece POST istekleri kabul edilir')
        }, status=405)
    
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': _('Yetkiniz yok')
        }, status=403)
    
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        tenant.is_active = not tenant.is_active
        tenant.save()
        
        # Audit log
        TenantAudit.objects.create(
            tenant=tenant,
            action='STATUS_CHANGE',
            description=f'Tenant durumu değiştirildi: {tenant.is_active}',
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'is_active': tenant.is_active,
            'message': _('Tenant durumu başarıyla değiştirildi.')
        })
        
    except Tenant.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Tenant bulunamadı')
        }, status=404)

