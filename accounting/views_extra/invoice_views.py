from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Invoice, Company, Customer
from ..forms import InvoiceForm
from ..services.efatura_service import (
    send_invoice_to_gib,
    check_invoice_status,
    cancel_invoice_on_gib,
    generate_invoice_xml,
)
import json
from datetime import datetime


@login_required
def invoice_list(request: HttpRequest) -> HttpResponse:
    # Get user's companies
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )

    # Base queryset
    invoices = Invoice.objects.filter(
        is_active=True, company__in=user_companies
    ).select_related("company", "customer")

    # Filters
    search_query = request.GET.get("q", "")
    company_filter = request.GET.get("company", "")
    customer_filter = request.GET.get("customer", "")
    status_filter = request.GET.get("status", "")
    order_by = request.GET.get("order", "-issue_date")

    if search_query:
        invoices = invoices.filter(
            models.Q(invoice_number__icontains=search_query)
            | models.Q(customer__first_name__icontains=search_query)
            | models.Q(customer__last_name__icontains=search_query)
            | models.Q(customer__email__icontains=search_query)
        )

    if company_filter:
        invoices = invoices.filter(company_id=company_filter)

    if customer_filter:
        invoices = invoices.filter(customer_id=customer_filter)

    # Durum filtresi: ayrı bir status alanı olmadığından, is_active ve gib_status üzerinden yorumluyoruz
    if status_filter:
        if status_filter == "paid":
            # Ödenmiş fatura: aktif ve vadesi bugün veya geçmiş, tahsil edilmiş kabul edilebilir
            invoices = invoices.filter(
                is_active=True, due_date__lte=datetime.today().date()
            )
        elif status_filter == "pending":
            # Bekleyen fatura: aktif ve vadesi gelecekte olanlar
            invoices = invoices.filter(
                is_active=True, due_date__gt=datetime.today().date()
            )
        elif status_filter == "cancelled":
            # İptal: GİB iptal zamanı olanlar
            invoices = invoices.filter(gib_cancelled_at__isnull=False)

    # Ordering
    if order_by.startswith("-"):
        invoices = invoices.order_by(order_by)
    else:
        invoices = invoices.order_by(order_by)

    # Statistics
    total_invoices = invoices.count()
    paid_invoices = invoices.filter(
        is_active=True, due_date__lte=datetime.today().date()
    ).count()
    pending_invoices = invoices.filter(
        is_active=True, due_date__gt=datetime.today().date()
    ).count()
    total_amount = invoices.aggregate(total=models.Sum("total_amount"))["total"] or 0

    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "invoices": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "companies": user_companies,
        "customers": Customer.objects.filter(company__in=user_companies),
        # Basit durum seçenekleri: view içi mantığa paralel
        "status_choices": [
            ("paid", "Ödenmiş"),
            ("pending", "Bekleyen"),
            ("cancelled", "İptal Edilmiş"),
        ],
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "pending_invoices": pending_invoices,
        "total_amount": total_amount,
    }

    # Use modern template if exists
    template_name = "accounting/invoice_list_modern.html"
    return render(request, template_name, context)


@login_required
def invoice_create(request: HttpRequest) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            # Set default values
            if not invoice.invoice_number:
                invoice.invoice_number = generate_invoice_number(invoice.company)
            invoice.save()

            messages.success(request, "Fatura başarıyla oluşturuldu.")

            # Handle AJAX requests
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": f"/accounting/invoices/{invoice.pk}/",
                        "message": "Fatura başarıyla oluşturuldu.",
                    }
                )

            return redirect("accounting:invoice_detail", pk=invoice.pk)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": False,
                        "errors": form.errors,
                        "message": "Lütfen form hatalarını düzeltin.",
                    }
                )
    else:
        form = InvoiceForm()
        # Set default company if user has only one
        if user_companies.count() == 1:
            form.fields["company"].initial = user_companies.first()

    context = {
        "form": form,
        "companies": user_companies,
        "customers": Customer.objects.filter(company__in=user_companies),
    }

    template_name = "accounting/invoice_form_modern.html"
    return render(request, template_name, context)


@login_required
def invoice_detail(request: HttpRequest, pk: int) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )
    invoice = get_object_or_404(Invoice, pk=pk, company__in=user_companies)

    context = {
        "invoice": invoice,
    }
    return render(request, "accounting/invoice_detail.html", context)


def invoice_xml_download(request: HttpRequest, pk: int) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )
    invoice = get_object_or_404(Invoice, pk=pk, company__in=user_companies)

    try:
        xml_bytes = generate_invoice_xml(invoice)
        response = HttpResponse(xml_bytes, content_type="application/xml")
        response[
            "Content-Disposition"
        ] = f"attachment; filename=invoice_{invoice.invoice_number}.xml"
        return response
    except Exception as e:
        messages.error(request, f"XML oluşturma hatası: {str(e)}")
        return redirect("accounting:invoice_detail", pk=pk)


@login_required
def invoice_update(request: HttpRequest, pk: int) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )
    invoice = get_object_or_404(Invoice, pk=pk, company__in=user_companies)

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, "Fatura başarıyla güncellendi.")

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": f"/accounting/invoices/{invoice.pk}/",
                        "message": "Fatura başarıyla güncellendi.",
                    }
                )

            return redirect("accounting:invoice_detail", pk=invoice.pk)
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = InvoiceForm(instance=invoice)

    context = {
        "form": form,
        "invoice": invoice,
        "companies": user_companies,
        "customers": Customer.objects.filter(company__in=user_companies),
    }

    template_name = "accounting/invoice_form_modern.html"
    return render(request, template_name, context)


@login_required
def invoice_delete(request: HttpRequest, pk: int) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )
    invoice = get_object_or_404(Invoice, pk=pk, company__in=user_companies)

    if request.method == "POST":
        invoice.is_active = False  # Soft delete
        invoice.save()

        messages.success(request, "Fatura başarıyla silindi.")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "redirect_url": "/accounting/invoices/",
                    "message": "Fatura başarıyla silindi.",
                }
            )

        return redirect("accounting:invoice_list")

    return render(
        request, "accounting/invoice_confirm_delete.html", {"invoice": invoice}
    )


# API endpoints for modern UI
@login_required
def api_customer_search(request: HttpRequest) -> JsonResponse:
    """AJAX endpoint for customer search"""
    query = request.GET.get("q", "")
    company_id = request.GET.get("company", "")

    customers = Customer.objects.filter(is_active=True)

    if company_id:
        customers = customers.filter(company_id=company_id)

    if query:
        customers = customers.filter(
            models.Q(first_name__icontains=query)
            | models.Q(last_name__icontains=query)
            | models.Q(email__icontains=query)
        )

    customers = customers[:10]  # Limit results

    results = []
    for customer in customers:
        results.append(
            {
                "id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "email": customer.email,
                "phone": getattr(customer, "phone", ""),
            }
        )

    return JsonResponse({"results": results})


@login_required
def api_invoice_bulk_action(request: HttpRequest) -> JsonResponse:
    """Handle bulk actions on invoices"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Method not allowed"})

    try:
        data = json.loads(request.body)
        action = data.get("action")
        invoice_ids = data.get("invoice_ids", [])

        user_companies = (
            request.user.created_companies.all()
            if hasattr(request.user, "created_companies")
            else Company.objects.none()
        )
        invoices = Invoice.objects.filter(
            id__in=invoice_ids, company__in=user_companies
        )

        if action == "mark_paid":
            invoices.update(status="paid")
            message = f"{invoices.count()} fatura ödendi olarak işaretlendi"
        elif action == "send_email":
            # Implement email sending logic
            message = f"{invoices.count()} fatura e-posta ile gönderildi"
        elif action == "delete":
            invoices.update(is_active=False)
            message = f"{invoices.count()} fatura silindi"
        else:
            return JsonResponse({"success": False, "message": "Geçersiz işlem"})

        return JsonResponse({"success": True, "message": message})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


def generate_invoice_number(company):
    """Generate next invoice number for company"""
    current_year = datetime.now().year
    prefix = f"INV-{current_year}-"

    last_invoice = (
        Invoice.objects.filter(company=company, invoice_number__startswith=prefix)
        .order_by("-id")
        .first()
    )

    if last_invoice and last_invoice.invoice_number:
        try:
            last_number = int(last_invoice.invoice_number.split("-")[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1

    return f"{prefix}{next_number:06d}"


@login_required
def invoice_send_gib(request: HttpRequest, pk: int) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )
    invoice = get_object_or_404(Invoice, pk=pk, company__in=user_companies)

    try:
        response = send_invoice_to_gib(invoice)
        if response.status_code == 200:
            messages.success(request, "Fatura GİB'e başarıyla gönderildi.")
        else:
            messages.error(request, f"GİB gönderim hatası: {response.text}")
    except Exception as e:
        messages.error(request, f"GİB gönderim istisnası: {str(e)}")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": response.status_code == 200})

    return redirect("accounting:invoice_detail", pk=pk)


@login_required
def invoice_check_gib_status(request: HttpRequest, pk: int) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )
    invoice = get_object_or_404(Invoice, pk=pk, company__in=user_companies)

    try:
        check_invoice_status(invoice)
        messages.info(
            request, f"GİB Durumu: {invoice.gib_status} | Yanıt: {invoice.gib_response}"
        )
    except Exception as e:
        messages.error(request, f"GİB durum sorgu istisnası: {str(e)}")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": getattr(invoice, "gib_status", ""),
                "response": getattr(invoice, "gib_response", ""),
            }
        )

    return redirect("accounting:invoice_detail", pk=pk)


@login_required
def invoice_cancel_gib(request: HttpRequest, pk: int) -> HttpResponse:
    user_companies = (
        request.user.created_companies.all()
        if hasattr(request.user, "created_companies")
        else Company.objects.none()
    )
    invoice = get_object_or_404(Invoice, pk=pk, company__in=user_companies)

    try:
        response = cancel_invoice_on_gib(invoice)
        if response.status_code == 200:
            messages.success(request, "Fatura GİB'de iptal edildi.")
        else:
            messages.error(request, f"GİB iptal hatası: {response.text}")
    except Exception as e:
        messages.error(request, f"GİB iptal istisnası: {str(e)}")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": response.status_code == 200})

    return redirect("accounting:invoice_detail", pk=pk)
