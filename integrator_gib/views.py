# -*- coding: utf-8 -*-
"""
GIB Integrator Views
Gelir İdaresi Başkanlığı Entegrasyon Görünümleri
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import timezone

from .models import (
    IntegratorConfig,
    AccessToken,
    GIBCertificate,
    GIBSubmissionLog
)


@login_required
def gib_dashboard(request):
    """
    GIB entegrasyon ana dashboard
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    # Entegrasyon yapılandırması
    try:
        config = IntegratorConfig.objects.filter(is_active=True).first()
    except IntegratorConfig.DoesNotExist:
        config = None
    
    # Son gönderimler (GIBSubmissionLog modelinden)
    recent_submissions = GIBSubmissionLog.objects.all().order_by('-submitted_at')[:10]
    
    # Bekleyen gönderimler
    pending_submissions = GIBSubmissionLog.objects.filter(
        status='PENDING'
    )
    
    # Sertifikalar
    certificates = GIBCertificate.objects.filter(is_active=True)
    
    context = {
        'company': company,
        'config': config,
        'recent_submissions': recent_submissions,
        'pending_submissions': pending_submissions,
        'certificates': certificates,
        'total_submissions': GIBSubmissionLog.objects.all().count(),
        'successful_submissions': GIBSubmissionLog.objects.filter(
            status='ACCEPTED'
        ).count(),
    }
    
    return render(request, 'integrator_gib/dashboard.html', context)


@login_required
def config_edit(request):
    """
    GIB entegrasyon yapılandırması
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    # Mevcut yapılandırmayı al veya oluştur  
    config = IntegratorConfig.objects.filter(is_active=True).first()
    if not config:
        config = IntegratorConfig.objects.create(
            name='GIB Integration',
            base_url='https://efatura.gov.tr',
            client_id='',
            client_secret='',
            is_active=False
        )
    
    if request.method == 'POST':
        try:
            config.client_id = request.POST.get('gib_username', '')
            config.client_secret = request.POST.get('gib_password', '')
            config.base_url = request.POST.get('base_url', config.base_url)
            config.is_active = request.POST.get('is_active') == 'on'
            config.save()
            
            messages.success(request, _('GIB yapılandırması başarıyla kaydedildi.'))
            return redirect('integrator_gib:dashboard')
            
        except Exception as e:
            messages.error(request, _('Yapılandırma kaydedilirken hata: ') + str(e))
    
    context = {
        'config': config,
    }
    
    return render(request, 'integrator_gib/config_edit.html', context)


@login_required
def submission_list(request):
    """
    GIB gönderim listesi
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    submissions = GIBSubmissionLog.objects.all().order_by('-submitted_at')
    
    # Filtreleme
    status_filter = request.GET.get('status')
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    document_type_filter = request.GET.get('document_type')
    # document_type field yok, declaration_code kullanılabilir
    
    context = {
        'submissions': submissions,
        'status_filter': status_filter,
        'document_type_filter': document_type_filter,
    }
    
    return render(request, 'integrator_gib/submission_list.html', context)


@login_required
def submission_detail(request, submission_id):
    """
    GIB gönderim detayı
    """
    company = getattr(request.user, 'company', None)
    
    try:
        submission = GIBSubmissionLog.objects.get(id=submission_id)
    except GIBSubmissionLog.DoesNotExist:
        messages.error(request, _('Gönderim bulunamadı.'))
        return redirect('integrator_gib:submission_list')
    
    # Bu submission'ın kendisi log
    logs = [submission]
    
    context = {
        'submission': submission,
        'logs': logs,
    }
    
    return render(request, 'integrator_gib/submission_detail.html', context)


@login_required
def certificate_list(request):
    """
    GIB sertifika listesi
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    certificates = GIBCertificate.objects.all().order_by('-valid_until')
    
    context = {
        'certificates': certificates,
    }
    
    return render(request, 'integrator_gib/certificate_list.html', context)


@login_required
def ajax_test_connection(request):
    """
    AJAX: GIB bağlantı testi
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': _('Sadece POST istekleri kabul edilir')
        }, status=405)
    
    company = getattr(request.user, 'company', None)
    
    try:
        config = IntegratorConfig.objects.filter(is_active=True).first()
        if not config:
            raise IntegratorConfig.DoesNotExist
        
        # Burada gerçek GIB API bağlantı testi yapılacak
        # Şimdilik simüle ediyoruz
        
        if config.is_active:
            return JsonResponse({
                'success': True,
                'message': _('GIB bağlantısı başarılı.'),
                'environment': 'PRODUCTION',  # config.environment field yok
            })
        else:
            return JsonResponse({
                'success': False,
                'error': _('GIB entegrasyonu aktif değil.')
            })
            
    except IntegratorConfig.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('GIB yapılandırması bulunamadı.')
        }, status=404)


@login_required
def ajax_retry_submission(request, submission_id):
    """
    AJAX: Başarısız gönderimleri yeniden dene
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': _('Sadece POST istekleri kabul edilir')
        }, status=405)
    
    company = getattr(request.user, 'company', None)
    
    try:
        submission = GIBSubmissionLog.objects.get(id=submission_id)
        
        # Sadece başarısız gönderimleri yeniden dene
        if submission.status not in ['ERROR', 'REJECTED']:
            return JsonResponse({
                'success': False,
                'error': _('Sadece başarısız gönderimler yeniden denenebilir.')
            })
        
        # Burada gerçek yeniden deneme mantığı olacak
        submission.status = 'PENDING'
        submission.save()
        
        return JsonResponse({
            'success': True,
            'message': _('Gönderim yeniden deneniyor.'),
            'submission_id': submission.id,
        })
        
    except GIBSubmissionLog.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Gönderim bulunamadı.')
        }, status=404)


@login_required
def ajax_dashboard_stats(request):
    """
    AJAX: Dashboard istatistikleri
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        return JsonResponse({
            'success': False,
            'error': _('Şirket bilgisi bulunamadı')
        }, status=400)
    
    stats = {
        'total_submissions': GIBSubmissionLog.objects.all().count(),
        'successful_submissions': GIBSubmissionLog.objects.filter(
            status='ACCEPTED'
        ).count(),
        'pending_submissions': GIBSubmissionLog.objects.filter(
            status='PENDING'
        ).count(),
        'failed_submissions': GIBSubmissionLog.objects.filter(
            status__in=['ERROR', 'REJECTED']
        ).count(),
    }
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })

