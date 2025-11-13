# -*- coding: utf-8 -*-
"""
Advisors Views
Mali Müşavir ve Vergi Danışmanlığı Görünümleri
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import timezone

from .models import (
    TaxpayerProfile,
    AdvisorProfile,
    ConsultationSession,
    ClientDocument,
    ClientContract,
    AdvisorReport,
    AdvisorTask
)


@login_required
def advisor_dashboard(request):
    """Mali müşavir ana dashboard"""
    # Advisor profile'ı al
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
    except AdvisorProfile.DoesNotExist:
        advisor = None
    
    # Mükellefi müşteriler
    clients = TaxpayerProfile.objects.all()[:10] if advisor else []
    
    # Son oturumlar  
    recent_sessions = ConsultationSession.objects.filter(
        advisor=advisor
    ).order_by('-scheduled_date')[:5] if advisor else []
    
    # Aktif görevler
    active_tasks = AdvisorTask.objects.filter(
        advisor=advisor,
        is_completed=False
    ).order_by('due_date')[:10] if advisor else []
    
    context = {
        'clients': clients,
        'total_clients': clients.count() if clients else 0,
        'upcoming_declarations': [],  # Placeholder
        'recent_sessions': recent_sessions,
        'active_alerts': active_tasks,  # Görevleri uyarı gibi göster
        'pending_invoices': [],
        'total_pending_amount': 0,
    }
    
    return render(request, 'advisors/dashboard.html', context)


@login_required
def client_list(request):
    """Müşteri listesi"""
    clients = TaxpayerProfile.objects.all().select_related('company')
    
    context = {
        'clients': clients,
        'status_filter': None,
    }
    
    return render(request, 'advisors/client_list.html', context)


@login_required
def client_detail(request, client_id):
    """Müşteri detay sayfası"""
    client = get_object_or_404(TaxpayerProfile, id=client_id)
    
    sessions = ConsultationSession.objects.filter(taxpayer=client).order_by('-scheduled_date')
    documents = ClientDocument.objects.filter(taxpayer=client).order_by('-uploaded_at')
    contracts = ClientContract.objects.filter(taxpayer=client)
    
    context = {
        'client': client,
        'declarations': [],  # Placeholder
        'sessions': sessions,
        'documents': documents,
        'contracts': contracts,
    }
    
    return render(request, 'advisors/client_detail.html', context)


@login_required
def declaration_list(request):
    """Beyanname listesi (placeholder)"""
    context = {
        'declarations': [],
        'status_filter': None,
        'tax_type_filter': None,
    }
    return render(request, 'advisors/declaration_list.html', context)


@login_required
def declaration_create(request):
    """Yeni beyanname oluştur (placeholder)"""
    if request.method == 'POST':
        messages.info(request, _('Beyanname modeli henüz aktif değil.'))
        return redirect('advisors:declaration_list')
    
    clients = TaxpayerProfile.objects.all()
    
    context = {
        'clients': clients,
        'tax_types': [],
    }
    
    return render(request, 'advisors/declaration_create.html', context)


@login_required
def consultation_list(request):
    """Danışmanlık oturumları listesi"""
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
        sessions = ConsultationSession.objects.filter(advisor=advisor).order_by('-scheduled_date')
    except AdvisorProfile.DoesNotExist:
        sessions = []
    
    context = {'sessions': sessions}
    return render(request, 'advisors/consultation_list.html', context)


@login_required
def document_list(request):
    """Müşteri dokümanları listesi"""
    documents = ClientDocument.objects.all().select_related('taxpayer').order_by('-uploaded_at')
    
    context = {
        'documents': documents,
        'doc_type_filter': None,
    }
    
    return render(request, 'advisors/document_list.html', context)


@login_required
def alert_list(request):
    """Danışman uyarıları listesi (görev listesi)"""
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
        alerts = AdvisorTask.objects.filter(advisor=advisor).order_by('-due_date')
    except AdvisorProfile.DoesNotExist:
        alerts = []
    
    context = {
        'alerts': alerts,
        'severity_filter': None,
        'resolved_filter': None,
    }
    
    return render(request, 'advisors/alert_list.html', context)


@login_required
def invoice_list(request):
    """Fatura listesi (placeholder)"""
    context = {
        'invoices': [],
        'status_filter': None,
        'total_pending': 0,
        'total_paid': 0,
    }
    
    return render(request, 'advisors/invoice_list.html', context)


@login_required
def ajax_client_compliance(request, client_id):
    """AJAX: Müşteri uyum durumu (placeholder)"""
    data = {
        'success': True,
        'compliance_status': 'COMPLIANT',
        'last_declaration_date': None,
        'risk_level': 'LOW',
    }
    return JsonResponse(data)


@login_required
def ajax_dashboard_stats(request):
    """AJAX: Dashboard istatistikleri"""
    stats = {
        'total_clients': TaxpayerProfile.objects.all().count(),
        'pending_declarations': 0,
        'unresolved_alerts': 0,
        'pending_invoices': 0,
    }
    
    return JsonResponse({'success': True, 'stats': stats})

