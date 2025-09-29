"""
FinAsis Yönetim Paneli - Modern, kullanıcı dostu ve fonksiyonel yönetim modülü.
Admin ve yetkili kullanıcılar için gelişmiş dashboard, kullanıcı, şirket ve fatura yönetimi sağlar.
"""
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from src.apps.accounts.models import CustomUser
from src.apps.accounting.models import Company, Invoice
from src.apps.accounts.forms import RegisterForm
from django.contrib import messages
from django import forms
from django.core.paginator import Paginator
from src.apps.management.models import ActionLog, Notification, HelpContent
from .filters import UserFilter
from django.http import JsonResponse, HttpResponse
import csv
from django.views.decorators.cache import cache_page
from src.apps.accounting.forms import CompanyForm as AccountingCompanyForm

def is_admin(user):
    """Kullanıcının admin veya staff olup olmadığını kontrol eder."""
    return user.is_staff or user.is_superuser

def is_superadmin(user):
    """Kullanıcının süper admin olup olmadığını kontrol eder."""
    return user.is_superuser

@cache_page(60 * 10)  # 10 dakika cache
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
            deleted_users = list(CustomUser.objects.filter(id__in=ids).values_list('username', flat=True))
            CustomUser.objects.filter(id__in=ids).delete()
            ActionLog.objects.create(
                user=request.user,
                action="Toplu Kullanıcı Silme",
                detail=f"Silinen kullanıcılar: {', '.join(deleted_users)}"
            )
            messages.success(request, f"{len(ids)} kullanıcı silindi.")
            return redirect('user_list')
    users = CustomUser.objects.all().order_by('-date_joined')
    f = UserFilter(request.GET, queryset=users)
    paginator = Paginator(f.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "management/user_list.html", {"page_obj": page_obj, "filter": f})

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_list_export_csv(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    f = UserFilter(request.GET, queryset=users)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="kullanicilar.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Kullanıcı Adı', 'E-posta', 'Yetki', 'Kayıt Tarihi'])
    for user in f.qs:
        yetki = 'Süper Admin' if user.is_superuser else ('Yönetici' if user.is_staff else 'Kullanıcı')
        writer.writerow([user.id, user.username, user.email, yetki, user.date_joined.strftime('%d.%m.%Y %H:%M')])
    return response

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
    return render(request, "management/company_list.html", {"page_obj": page_obj, "companies": page_obj.object_list, "query": query, "sector": sector})

@user_passes_test(is_admin, login_url='/accounts/login/')
def company_detail(request, company_id):
    """Şirket detay sayfası."""
    company = get_object_or_404(Company, id=company_id)
    return render(request, "management/company_detail.html", {"company": company})

@user_passes_test(is_admin, login_url='/accounts/login/')
def company_add(request):
    """Yeni şirket ekleme formu."""
    if request.method == 'POST':
        form = AccountingCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            if hasattr(company, 'created_by_id'):
                company.created_by = request.user
            company.save()
            form.save_m2m()
            ActionLog.objects.create(
                user=request.user,
                action="Şirket Ekleme",
                detail=f"Eklenen şirket: {company.name}"
            )
            messages.success(request, 'Şirket başarıyla eklendi.')
            return redirect('company_list')
    else:
        form = AccountingCompanyForm()
    return render(request, "management/company_form.html", {"form": form})

@user_passes_test(is_admin, login_url='/accounts/login/')
def company_edit(request, company_id):
    """Şirket düzenleme formu."""
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        form = AccountingCompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            company = form.save(commit=False)
            if hasattr(company, 'updated_by_id'):
                company.updated_by = request.user
            company.save()
            form.save_m2m()
            ActionLog.objects.create(
                user=request.user,
                action="Şirket Güncelleme",
                detail=f"Güncellenen şirket: {company.name}"
            )
            messages.success(request, 'Şirket başarıyla güncellendi.')
            return redirect('company_list')
    else:
        form = AccountingCompanyForm(instance=company)
    return render(request, "management/company_form.html", {"form": form, "edit": True, "company": company})

@user_passes_test(is_admin, login_url='/accounts/login/')
def company_delete(request, company_id):
    """Şirket silme onayı."""
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        name = company.name
        company.delete()
        ActionLog.objects.create(
            user=request.user,
            action="Şirket Silme",
            detail=f"Silinen şirket: {name}"
        )
        messages.success(request, 'Şirket silindi.')
        return redirect('company_list')
    return render(request, "management/company_confirm_delete.html", {"company": company})

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
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            form.save_m2m()  # groups gibi M2M alanlar için
            ActionLog.objects.create(
                user=request.user,
                action="Kullanıcı Ekleme",
                detail=f"Eklenen kullanıcı: {user.username}"
            )
            # Yeni kullanıcıya hoş geldin bildirimi
            Notification.objects.create(
                user=user,
                message="Hoş geldiniz! Hesabınız başarıyla oluşturuldu.",
                link="/accounts/profile/"
            )
            messages.success(request, 'Kullanıcı başarıyla eklendi.')
            return redirect('user_list')
    else:
        form = RegisterForm()
    return render(request, "management/user_form.html", {"form": form})

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            ActionLog.objects.create(
                user=request.user,
                action="Kullanıcı Güncelleme",
                detail=f"Güncellenen kullanıcı: {user.username}"
            )
            messages.success(request, 'Kullanıcı başarıyla güncellendi.')
            return redirect('user_list')
    else:
        form = RegisterForm(instance=user)
    return render(request, "management/user_form.html", {"form": form, "edit": True})

@user_passes_test(is_admin, login_url='/accounts/login/')
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        username = user.username
        user.delete()
        ActionLog.objects.create(
            user=request.user,
            action="Kullanıcı Silme",
            detail=f"Silinen kullanıcı: {username}"
        )
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
    Sadece süper adminlerin görebileceği log sayfası.
    """
    logs = ActionLog.objects.select_related('user').order_by('-timestamp')[:100]
    return render(request, "management/admin_logs.html", {"logs": logs})

@user_passes_test(is_admin, login_url='/accounts/login/')
def help_content_api(request):
    role = request.GET.get('role', 'genel')
    page_key = request.GET.get('page_key')
    qs = HelpContent.objects.filter(role=role)
    if page_key:
        qs = qs.filter(page_key=page_key)
    data = [
        {
            'title': h.title,
            'content': h.content,
            'updated_at': h.updated_at.strftime('%d.%m.%Y %H:%M'),
        } for h in qs.order_by('-updated_at')
    ]
    return JsonResponse({'items': data}) 