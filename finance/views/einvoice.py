# -*- coding: utf-8 -*-
"""
E-Fatura/E-Arşiv Fatura işlemleri ile ilgili görünümler
"""

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from ..models import EInvoice, Customer
from permissions.decorators import permission_required

import json
import uuid
from datetime import datetime


class EInvoiceListView(ListView):
    """E-fatura ve E-arşiv fatura listesi görünümü"""

    model = EInvoice
    template_name = "finance/einvoice_list.html"
    context_object_name = "einvoices"
    paginate_by = 20

    def get_queryset(self):
        queryset = EInvoice.objects.all().order_by("-issue_date")

        # Filtreleme
        invoice_type = self.request.GET.get("invoice_type")
        if invoice_type:
            queryset = queryset.filter(invoice_type=str(invoice_type).upper())

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=str(status).upper())

        customer = self.request.GET.get("customer")
        if customer:
            queryset = queryset.filter(customer__id=customer)

        date_from = self.request.GET.get("date_from")
        if date_from:
            queryset = queryset.filter(issue_date__gte=date_from)

        date_to = self.request.GET.get("date_to")
        if date_to:
            queryset = queryset.filter(issue_date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customers"] = Customer.objects.all()
        context["invoice_types"] = EInvoice.INVOICE_TYPE_CHOICES
        context["statuses"] = EInvoice.STATUS_CHOICES

        # İstatistikler
        context["total_invoice_count"] = EInvoice.objects.count()
        context["draft_count"] = EInvoice.objects.filter(status="DRAFT").count()
        context["sent_count"] = EInvoice.objects.filter(status="SENT").count()
        context["accepted_count"] = EInvoice.objects.filter(status="ACCEPTED").count()

        return context


class EInvoiceDetailView(DetailView):
    """E-fatura detay görünümü"""

    model = EInvoice
    template_name = "finance/einvoice_detail.html"
    context_object_name = "einvoice"

    def get_queryset(self):
        return EInvoice.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        einvoice = self.get_object()
        # Fatura öğeleri (varsa)
        items_qs = getattr(einvoice, "items", None)
        context["items"] = items_qs.all() if items_qs is not None else []

        return context


class EInvoiceCreateView(CreateView):
    """E-fatura oluşturma görünümü"""

    model = EInvoice
    template_name = "finance/einvoice_form.html"
    fields = ["invoice_type", "customer", "issue_date", "due_date", "note"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customers"] = Customer.objects.all()
        context["action"] = "create"
        return context

    def form_valid(self, form):
        form.instance.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        form.instance.status = "DRAFT"
        # Initialize required monetary fields before first save
        form.instance.subtotal = form.instance.subtotal or 0
        form.instance.tax_total = form.instance.tax_total or 0
        form.instance.total = form.instance.total or 0

        response = super().form_valid(form)

        # Fatura öğelerini kaydet (AJAX ile gönderilecek)

        messages.success(self.request, _("E-fatura başarıyla oluşturuldu."))
        return response

    def get_success_url(self):
        return reverse_lazy("finance:einvoice_detail", kwargs={"pk": self.object.pk})


class EInvoiceUpdateView(UpdateView):
    """E-fatura güncelleme görünümü"""

    model = EInvoice
    template_name = "finance/einvoice_form.html"
    fields = ["invoice_type", "customer", "issue_date", "due_date", "note"]

    def get_queryset(self):
        # Sadece taslak durumundaki faturalar düzenlenebilir
        return EInvoice.objects.filter(status="DRAFT")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customers"] = Customer.objects.all()
        items_qs = getattr(self.object, "items", None)
        context["items"] = items_qs.all() if items_qs is not None else []
        context["action"] = "edit"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Fatura öğelerini güncelle (AJAX ile gönderilecek)

        messages.success(self.request, _("E-fatura başarıyla güncellendi."))
        return response

    def get_success_url(self):
        return reverse_lazy("finance:einvoice_detail", kwargs={"pk": self.object.pk})


class EInvoiceDeleteView(DeleteView):
    """E-fatura silme görünümü"""

    model = EInvoice
    template_name = "finance/einvoice_confirm_delete.html"
    success_url = reverse_lazy("finance:einvoice_list")

    def get_queryset(self):
        # Sadece taslak durumundaki faturalar silinebilir
        return EInvoice.objects.filter(status="DRAFT")

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("E-fatura başarıyla silindi."))
        return super().delete(request, *args, **kwargs)


# Function-based views
@login_required
@permission_required("finance.send_einvoice")
def send_einvoice(request, pk):
    """E-faturayı gönderme işlemi"""
    einvoice = get_object_or_404(EInvoice, pk=pk, status="DRAFT")

    try:
        # E-fatura API entegrasyonu ve gönderim işlemi
        # Bu örnek için basit bir durum güncellemesi yapılıyor
        einvoice.status = "SENT"
        einvoice.sent_at = datetime.now()
        einvoice.save()

        # İşlem kaydı (history modeli yoksa atla)

        messages.success(request, _("E-fatura başarıyla gönderildi."))
    except Exception as e:
        messages.error(request, _(f"E-fatura gönderilirken hata oluştu: {str(e)}"))

    return redirect("finance:einvoice_detail", pk=einvoice.pk)


@login_required
@permission_required("finance.download_einvoice")
def download_einvoice(request, pk):
    """E-faturayı PDF olarak indirme"""
    einvoice = get_object_or_404(EInvoice, pk=pk)

    try:
        # PDF oluşturma ve indirme işlemi
        # Bu örnek için PDF oluşturma işlemi yapılmıyor

        # İşlem kaydı (history modeli yoksa atla)

        messages.success(request, _("E-fatura PDF olarak indirildi."))
    except Exception as e:
        messages.error(request, _(f"E-fatura indirilirken hata oluştu: {str(e)}"))

    return redirect("finance:einvoice_detail", pk=einvoice.pk)


@csrf_exempt
@login_required
def add_invoice_item(request, invoice_id):
    """E-faturaya öğe ekleme (AJAX)"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    einvoice = get_object_or_404(EInvoice, pk=invoice_id, status="DRAFT")

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            if hasattr(einvoice, "items"):
                item = einvoice.items.create(
                    description=data.get("description") or "",
                    quantity=data.get("quantity"),
                    unit_price=data.get("unit_price"),
                    tax_rate=data.get("tax_rate"),
                )
            else:
                raise Exception("Invoice items relation is not available")

            # Fatura toplamını güncelle
            # EInvoiceItem.save() already updates totals

        return JsonResponse({"status": "success", "item_id": item.id})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


@csrf_exempt
@login_required
def update_invoice_status(request, invoice_id):
    """E-fatura durumunu güncelleme (AJAX)"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    einvoice = get_object_or_404(EInvoice, pk=invoice_id)

    try:
        data = json.loads(request.body)
        new_status = data.get("status")

        if str(new_status).upper() not in dict(EInvoice.STATUS_CHOICES):
            return JsonResponse({"status": "error", "message": "Invalid status"})

        einvoice.status = str(new_status).upper()
        einvoice.save()

        # İşlem kaydı (history modeli yoksa atla)

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
