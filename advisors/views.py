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

from .models import (
    TaxpayerProfile,
    AdvisorProfile,
    Engagement,
    ConsultationSession,
    ClientDocument,
    ClientContract,
    AdvisorTask,
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
    recent_sessions = (
        ConsultationSession.objects.filter(advisor=advisor).order_by("-scheduled_date")[
            :5
        ]
        if advisor
        else []
    )

    # Aktif görevler
    active_tasks = (
        AdvisorTask.objects.filter(advisor=advisor, is_completed=False).order_by(
            "due_date"
        )[:10]
        if advisor
        else []
    )

    context = {
        "clients": clients,
        "total_clients": clients.count() if clients else 0,
        "upcoming_declarations": [],  # Placeholder
        "recent_sessions": recent_sessions,
        "active_alerts": active_tasks,  # Görevleri uyarı gibi göster
        "pending_invoices": [],
        "total_pending_amount": 0,
    }

    return render(request, "advisors/dashboard.html", context)


@login_required
def client_list(request):
    """Müşteri listesi"""
    clients = TaxpayerProfile.objects.all().select_related("company")

    context = {
        "clients": clients,
        "status_filter": None,
    }

    return render(request, "advisors/client_list.html", context)


@login_required
def client_detail(request, client_id):
    """Müşteri detay sayfası"""
    client = get_object_or_404(TaxpayerProfile, id=client_id)

    sessions = ConsultationSession.objects.filter(taxpayer=client).order_by(
        "-scheduled_date"
    )
    documents = ClientDocument.objects.filter(taxpayer=client).order_by("-uploaded_at")
    contracts = ClientContract.objects.filter(taxpayer=client)

    context = {
        "client": client,
        "declarations": [],  # Placeholder
        "sessions": sessions,
        "documents": documents,
        "contracts": contracts,
    }

    return render(request, "advisors/client_detail.html", context)


@login_required
def declaration_list(request):
    """Beyanname listesi"""
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
        # Advisor'ın aktif müşterileri
        engagements = Engagement.objects.filter(
            advisor=advisor,
            status='active'
        )
        clients = [e.taxpayer for e in engagements]
        
        # Declaration modelini import et
        try:
            from accounting.models import Declaration
            # Müşterilerin şirketlerinin beyannameleri
            declarations = Declaration.objects.filter(
                company__in=[c.company for c in clients if c.company]
            ).select_related('company')
            
            # Filtreleme
            status = request.GET.get('status')
            if status:
                declarations = declarations.filter(status=status)
            
            tax_type = request.GET.get('tax_type')
            if tax_type:
                declarations = declarations.filter(tax_type=tax_type)
        except ImportError:
            # Declaration modeli yoksa boş liste
            declarations = []
            status = None
            tax_type = None
    except AdvisorProfile.DoesNotExist:
        declarations = []
        status = None
        tax_type = None
    
    context = {
        "declarations": declarations,
        "status_filter": status,
        "tax_type_filter": tax_type,
    }
    return render(request, "advisors/declaration_list.html", context)


@login_required
def declaration_create(request):
    """Yeni beyanname oluştur"""
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
        # Advisor'ın aktif müşterileri
        engagements = Engagement.objects.filter(
            advisor=advisor,
            status='active'
        )
        clients = [e.taxpayer for e in engagements]
    except AdvisorProfile.DoesNotExist:
        clients = []
        messages.warning(request, _("Mali müşavir profili bulunamadı."))
        return redirect("advisors:dashboard")
    
    # Declaration modelini import et
    try:
        from accounting.models import Declaration
        
        if request.method == "POST":
            company_id = request.POST.get('company')
            declaration_type = request.POST.get('declaration_type')
            period = request.POST.get('period')
            
            try:
                from accounting.models import Company
                company = Company.objects.get(id=company_id)
                
                _declaration = Declaration.objects.create(
                    company=company,
                    declaration_type=declaration_type,
                    period=period,
                    status='draft'
                )
                messages.success(request, _("Beyanname oluşturuldu."))
                return redirect("advisors:declaration_list")
            except Company.DoesNotExist:
                messages.error(request, _("Şirket bulunamadı."))
            except Exception as e:
                messages.error(request, _("Hata: {}").format(str(e)))
        
        # GET request
        tax_types = Declaration.DECLARATION_TYPES
        
        context = {
            "clients": clients,
            "tax_types": tax_types,
        }
        
        return render(request, "advisors/declaration_create.html", context)
        
    except ImportError:
        messages.warning(request, _("Beyanname modeli henüz aktif değil."))
        return redirect("advisors:declaration_list")


@login_required
def consultation_list(request):
    """Danışmanlık oturumları listesi"""
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
        sessions = ConsultationSession.objects.filter(advisor=advisor).order_by(
            "-scheduled_date"
        )
    except AdvisorProfile.DoesNotExist:
        sessions = []

    context = {"sessions": sessions}
    return render(request, "advisors/consultation_list.html", context)


@login_required
def document_list(request):
    """Müşteri dokümanları listesi"""
    documents = (
        ClientDocument.objects.all().select_related("taxpayer").order_by("-uploaded_at")
    )

    context = {
        "documents": documents,
        "doc_type_filter": None,
    }

    return render(request, "advisors/document_list.html", context)


@login_required
def alert_list(request):
    """Danışman uyarıları listesi (görev listesi)"""
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
        alerts = AdvisorTask.objects.filter(advisor=advisor).order_by("-due_date")
    except AdvisorProfile.DoesNotExist:
        alerts = []

    context = {
        "alerts": alerts,
        "severity_filter": None,
        "resolved_filter": None,
    }

    return render(request, "advisors/alert_list.html", context)


@login_required
def invoice_list(request):
    """Fatura listesi"""
    try:
        advisor = AdvisorProfile.objects.get(user=request.user)
        # Advisor'ın aktif müşterileri
        engagements = Engagement.objects.filter(
            advisor=advisor,
            status='active'
        )
        clients = [e.taxpayer for e in engagements]
        
        # Invoice modelini import et
        from accounting.models import Invoice
        from django.db.models import Sum
        
        # Müşterilerin şirketlerinin faturaları
        invoices = Invoice.objects.filter(
            company__in=[c.company for c in clients if c.company]
        ).select_related('company', 'customer')
        
        # Filtreleme
        status = request.GET.get('status')
        if status:
            invoices = invoices.filter(status=status)
        
        # İstatistikler
        total_pending = invoices.filter(status='pending').aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
        
        total_paid = invoices.filter(status='paid').aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
        
    except AdvisorProfile.DoesNotExist:
        invoices = []
        total_pending = 0
        total_paid = 0
        status = None
    except ImportError:
        # Invoice modeli yoksa boş liste
        invoices = []
        total_pending = 0
        total_paid = 0
        status = None
    
    context = {
        "invoices": invoices,
        "status_filter": status,
        "total_pending": total_pending,
        "total_paid": total_paid,
    }

    return render(request, "advisors/invoice_list.html", context)


@login_required
def ajax_client_compliance(request, client_id):
    """AJAX: Müşteri uyum durumu (placeholder)"""
    data = {
        "success": True,
        "compliance_status": "COMPLIANT",
        "last_declaration_date": None,
        "risk_level": "LOW",
    }
    return JsonResponse(data)


@login_required
def ajax_dashboard_stats(request):
    """AJAX: Dashboard istatistikleri"""
    stats = {
        "total_clients": TaxpayerProfile.objects.all().count(),
        "pending_declarations": 0,
        "unresolved_alerts": 0,
        "pending_invoices": 0,
    }

    return JsonResponse({"success": True, "stats": stats})
