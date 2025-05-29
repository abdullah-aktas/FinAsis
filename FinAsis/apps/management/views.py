"""
FinAsis Yönetim Paneli - Modern, kullanıcı dostu ve fonksiyonel yönetim modülü.
Admin ve yetkili kullanıcılar için gelişmiş dashboard, kullanıcı, şirket ve fatura yönetimi sağlar.
"""
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from FinAsis.apps.accounts.models import CustomUser
from FinAsis.apps.accounting.models import Company, Invoice
from FinAsis.apps.accounts.forms import UserCreationForm
from django.contrib import messages
from django import forms
from django.core.paginator import Paginator

def is_admin(user):
    """Kullanıcının admin veya staff olup olmadığını kontrol eder."""
    return user.is_staff or user.is_superuser

def is_superadmin(user):
    """Kullanıcının süper admin olup olmadığını kontrol eder."""
    return user.is_superuser

@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_dashboard(request):
    """
    Yönetim paneli ana dashboard'u. Kullanıcı, şirket, fatura sayıları, son eklenenler ve örnek grafik verisi içerir.
    """
    user_count = CustomUser.objects.count()
    company_count = Company.objects.count()
    invoice_count = Invoice.objects.count()
    latest_users = CustomUser.objects.order_by('-date_joined')[:5]
    latest_companies = Company.objects.order_by('-created_at')[:5] if hasattr(Company, 'created_at') else []
    latest_invoices = Invoice.objects.order_by('-issue_date')[:5] if hasattr(Invoice, 'issue_date') else []
    # Örnek grafik verisi (gerçek veriye entegre edilebilir)
    chart_data = {
        'labels': ['Ocak', 'Şubat', 'Mart', 'Nisan'],
        'invoices': [12, 18, 9, 22],
        'users': [5, 7, 3, 8],
        'companies': [2, 4, 1, 5],
    }
    return render(request, "management/dashboard.html", {
        'user_count': user_count,
        'company_count': company_count,
        'invoice_count': invoice_count,
        'latest_users': latest_users,
        'latest_companies': latest_companies,
        'latest_invoices': latest_invoices,
        'chart_data': chart_data,
    })

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_list(request):
    """
    Kullanıcı listesi: Arama, filtreleme, sayfalama ve toplu silme desteği ile.
    """
    if request.method == 'POST':
        ids = request.POST.getlist('selected_users')
        if ids:
            CustomUser.objects.filter(id__in=ids).delete()
            messages.success(request, f"{len(ids)} kullanıcı silindi.")
            return redirect('user_list')
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)
    if role == 'admin':
        users = users.filter(is_staff=True)
    elif role == 'user':
        users = users.filter(is_staff=False, is_superuser=False)
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "management/user_list.html", {"page_obj": page_obj, "query": query, "role": role})

@user_passes_test(is_admin, login_url='/accounts/login/')
def company_list(request):
    """
    Şirket listesi: Arama, filtreleme ve sayfalama desteği ile.
    """
    query = request.GET.get('q', '')
    sector = request.GET.get('sector', '')
    companies = Company.objects.all().order_by('-id')
    if query:
        companies = companies.filter(name__icontains=query) | companies.filter(tax_number__icontains=query)
    if sector:
        companies = companies.filter(sector__icontains=sector)
    paginator = Paginator(companies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "management/company_list.html", {"page_obj": page_obj, "query": query, "sector": sector})

@user_passes_test(is_admin, login_url='/accounts/login/')
def invoice_list(request):
    """
    Fatura listesi: Arama, filtreleme, sayfalama ve toplu silme desteği ile.
    """
    if request.method == 'POST':
        ids = request.POST.getlist('selected_invoices')
        if ids:
            Invoice.objects.filter(id__in=ids).delete()
            messages.success(request, f"{len(ids)} fatura silindi.")
            return redirect('invoice_list')
    query = request.GET.get('q', '')
    company_name = request.GET.get('company', '')
    invoices = Invoice.objects.all().order_by('-issue_date')
    if query:
        invoices = invoices.filter(description__icontains=query) | invoices.filter(total_amount__icontains=query)
    if company_name:
        invoices = invoices.filter(company__name__icontains=company_name)
    paginator = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "management/invoice_list.html", {"page_obj": page_obj, "query": query, "company_name": company_name})

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_detail(request, user_id):
    """
    Kullanıcı detay sayfası. Kullanıcıya ait faturalar da gösterilir.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    user_invoices = Invoice.objects.filter(company__owner=user) if hasattr(Invoice, 'company') and hasattr(Company, 'owner') else []
    return render(request, "management/user_detail.html", {"user": user, "user_invoices": user_invoices})

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_add(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kullanıcı başarıyla eklendi.')
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, "management/user_form.html", {"form": form})

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kullanıcı başarıyla güncellendi.')
            return redirect('user_list')
    else:
        form = UserCreationForm(instance=user)
    return render(request, "management/user_form.html", {"form": form, "edit": True})

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Kullanıcı silindi.')
        return redirect('user_list')
    return render(request, "management/user_confirm_delete.html", {"user": user})

# Fatura Formu
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['company', 'total_amount', 'issue_date', 'due_date', 'description']

@user_passes_test(is_admin, login_url='/accounts/login/')
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, "management/invoice_detail.html", {"invoice": invoice})

@user_passes_test(is_admin, login_url='/accounts/login/')
def invoice_add(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fatura başarıyla eklendi.')
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    return render(request, "management/invoice_form.html", {"form": form})

@user_passes_test(is_admin, login_url='/accounts/login/')
def invoice_edit(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fatura başarıyla güncellendi.')
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, "management/invoice_form.html", {"form": form, "edit": True})

@user_passes_test(is_admin, login_url='/accounts/login/')
def invoice_delete(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Fatura silindi.')
        return redirect('invoice_list')
    return render(request, "management/invoice_confirm_delete.html", {"invoice": invoice})

@user_passes_test(is_superadmin, login_url='/accounts/login/')
def admin_logs(request):
    """
    Sadece süper adminlerin görebileceği örnek bir log sayfası.
    """
    # Örnek log verisi
    logs = [
        {"tarih": "2024-06-01", "olay": "Kullanıcı silindi", "kullanici": "admin"},
        {"tarih": "2024-06-02", "olay": "Fatura eklendi", "kullanici": "superuser"},
    ]
    return render(request, "management/admin_logs.html", {"logs": logs}) 