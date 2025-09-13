from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from FinAsis.apps.accounting.models import Invoice, Expense, BankAccount, BankTransaction, Company
from django.contrib.auth import get_user_model
from .models import Achievement, UserSettings, CustomUser, Subscription, SubscriptionType, SubscriptionLog
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from .forms import RegisterForm
from .utils import user_type_required, subscription_type_required
from django.core.mail import send_mail

# Create your views here.
@user_type_required('kobi', 'egitimci')
@login_required
def user_invoices(request):
    invoices = Invoice.objects.filter(customer__company=request.user.company)
    return render(request, "invoices/list.html", {"invoices": invoices})

@login_required
def user_profile(request):
    company = getattr(request.user, 'company', None)
    finans_ozet = {}
    son_faturalar = []
    son_giderler = []
    trend_aylar = []
    trend_gelirler = []
    trend_giderler = []
    son_basari = []
    son_banka = []
    gider_kategori_labels = []
    gider_kategori_data = []
    if company:
        toplam_fatura = Invoice.objects.filter(company=company).aggregate(toplam=Sum('total_amount'))['toplam'] or 0
        toplam_gider = Expense.objects.filter(company=company).aggregate(toplam=Sum('amount'))['toplam'] or 0
        toplam_bakiye = BankAccount.objects.filter(company=company).aggregate(toplam=Sum('balance'))['toplam'] or 0
        finans_ozet = {
            'toplam_fatura': toplam_fatura,
            'toplam_gider': toplam_gider,
            'toplam_bakiye': toplam_bakiye,
        }
        son_faturalar = Invoice.objects.filter(company=company).order_by('-issue_date')[:5]
        son_giderler = Expense.objects.filter(company=company).order_by('-expense_date')[:5]
        # Son 6 ay için trend verisi
        today = timezone.now().date().replace(day=1)
        for i in range(5, -1, -1):
            ay_baslangic = (today - timedelta(days=i*31)).replace(day=1)
            ay_son = (ay_baslangic + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            ay_label = ay_baslangic.strftime('%b %Y')
            ay_gelir = Invoice.objects.filter(company=company, issue_date__gte=ay_baslangic, issue_date__lte=ay_son).aggregate(toplam=Sum('total_amount'))['toplam'] or 0
            ay_gider = Expense.objects.filter(company=company, expense_date__gte=ay_baslangic, expense_date__lte=ay_son).aggregate(toplam=Sum('amount'))['toplam'] or 0
            trend_aylar.append(ay_label)
            trend_gelirler.append(float(ay_gelir))
            trend_giderler.append(float(ay_gider))
        son_basari = Achievement.objects.filter(company=company).order_by('-date_earned')[:5]
        banka_hesaplari = BankAccount.objects.filter(company=company)
        son_banka = BankTransaction.objects.filter(account__in=banka_hesaplari).order_by('-date')[:5]
        # Gider kategorisi dağılımı (son 6 ay)
        six_months_ago = today - timedelta(days=180)
        kategori_qs = Expense.objects.filter(company=company, expense_date__gte=six_months_ago)
        kategori_aggregate = kategori_qs.values('category').annotate(toplam=Sum('amount')).order_by('-toplam')
        gider_kategori_labels = [Expense.EXPENSE_CATEGORIES_DICT.get(item['category'], item['category']) for item in kategori_aggregate]
        gider_kategori_data = [float(item['toplam']) for item in kategori_aggregate]
    context = {
        "user": request.user,
        "finans_ozet": finans_ozet,
        "son_faturalar": son_faturalar,
        "son_giderler": son_giderler,
        "trend_aylar": trend_aylar,
        "trend_gelirler": trend_gelirler,
        "trend_giderler": trend_giderler,
        "son_basari": son_basari,
        "son_banka": son_banka,
        "gider_kategori_labels": gider_kategori_labels,
        "gider_kategori_data": gider_kategori_data,
    }
    utype = getattr(request.user, 'user_type', None)
    code = getattr(utype, 'code', None)
    template_map = {
        'kobi': 'accounts/dashboard_kobi.html',
        'egitimci': 'accounts/dashboard_egitimci.html',
        'ogrenci': 'accounts/dashboard_ogrenci.html',
        'oyuncu': 'accounts/dashboard_oyuncu.html',
    }
    dashboard_template = template_map.get(code or '', 'accounts/profile.html')
    return render(request, dashboard_template, context)

@login_required
def company_detail(request):
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, 'Şirket bilgisi bulunamadı.')
        return redirect('accounts:user_profile')
    return render(request, "accounts/company_detail.html", {"company": company})

@login_required
def company_edit(request):
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, 'Şirket bilgisi bulunamadı.')
        return redirect('accounts:user_profile')
    if request.method == 'POST':
        company.name = request.POST.get('name', company.name)
        company.sector = request.POST.get('sector', company.sector)
        company.tax_number = request.POST.get('tax_number', company.tax_number)
        company.address = request.POST.get('address', company.address)
        company.phone = request.POST.get('phone', company.phone)
        company.email = request.POST.get('email', company.email)
        if 'logo' in request.FILES:
            company.logo = request.FILES['logo']
        company.save()
        messages.success(request, 'Şirket bilgileri başarıyla güncellendi.')
        return redirect('accounts:user_profile')
    return render(request, 'accounts/company_edit.html', {'company': company})

@login_required
def user_settings(request):
    user = request.user
    settings = getattr(user, 'settings', None)
    if not settings:
        try:
            user_obj = CustomUser.objects.get(pk=user.pk)
            settings = UserSettings.objects.create(user=user_obj)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Kullanıcı hesabınız bulunamadı. Lütfen tekrar giriş yapın.')
            return redirect('accounts:login')
        except Exception as e:
            messages.error(request, f'Ayar kaydı oluşturulamadı: {e}')
            return redirect('accounts:login')
    if request.method == 'POST':
        settings.email_notifications = bool(request.POST.get('email_notifications'))
        settings.dark_mode = bool(request.POST.get('dark_mode'))
        settings.save()
        messages.success(request, 'Ayarlarınız başarıyla güncellendi.')
        return redirect('accounts:user_profile')
    return render(request, 'accounts/user_settings.html', {'settings': settings})

def accounts_home(request):
    return redirect('accounts:user_profile')

def home(request):
    return render(request, 'accounting/home.html')

def register(request):
    """Kayıt view (basitleştirilmiş ve sağlam)."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Kullanıcı ayar kaydı oluştur (idempotent)
            UserSettings.objects.get_or_create(user=user)
            # Login: backend parametresi ile
            try:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            except Exception:
                # backend attribute yoksa fallback
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
            messages.success(request, 'Kayıt başarılı, hoş geldiniz!')
            return redirect('accounts:user_profile')
        else:
            messages.error(request, 'Form hataları var, lütfen düzeltin.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def report_redirect(request):
    return redirect('accounting:summary_report')

def summary_report(request):
    return render(request, 'accounting/summary_report.html')

def income_expense_chart_data(request):
    return render(request, 'accounting/income_expense_chart.html')

def chart_dashboard(request):   
    return render(request, 'accounting/chart_dashboard.html')

@user_type_required('kobi')
@login_required
def modul_kobi(request):
    return render(request, 'accounts/modul_kobi.html')

@user_type_required('egitimci')
@login_required
def modul_egitimci(request):
    return render(request, 'accounts/modul_egitimci.html')

@user_type_required('ogrenci')
@login_required
def modul_ogrenci(request):
    return render(request, 'accounts/modul_ogrenci.html')

@user_type_required('oyuncu')
@login_required
def modul_oyuncu(request):
    return render(request, 'accounts/modul_oyuncu.html')

# Not: 'invoices/list.html' template dosyasını 'FinAsisV1/apps/accounts/templates/invoices/list.html' olarak oluşturmalısınız.

@receiver(post_save, sender=CustomUser)
def create_user_settings(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'settings'):
        UserSettings.objects.create(user=instance)

class SubscriptionChangeForm(forms.Form):
    subscription_type = forms.ModelChoiceField(queryset=SubscriptionType.objects.all(), label='Abonelik Tipi')

@login_required
def change_subscription(request):
    user = request.user
    if not hasattr(user, 'subscription'):
        return redirect('accounts:user_profile')
    if request.method == 'POST':
        form = SubscriptionChangeForm(request.POST)
        if form.is_valid():
            new_type = form.cleaned_data['subscription_type']
            old_type = user.subscription.subscription_type
            user.subscription.subscription_type = new_type
            user.subscription.save()
            SubscriptionLog.objects.create(
                user=user,
                old_subscription=old_type,
                new_subscription=new_type,
                note='Kullanıcı tarafından değiştirildi.'
            )
            # E-posta bildirimi gönder
            send_mail(
                subject='Abonelik Değişikliği Bildirimi',
                message=f"Sayın {user.get_full_name() or user.username},\n\nAbonelik tipiniz başarıyla değiştirildi.\n\nEski abonelik: {old_type.name if old_type else '-'}\nYeni abonelik: {new_type.name if new_type else '-'}\nTarih: {timezone.now().strftime('%d.%m.%Y %H:%M')}\n\nFinAsis Ekibi", 
                from_email=None, # settings.DEFAULT_FROM_EMAIL kullanılır
                recipient_list=[user.email],
                fail_silently=True
            )
            messages.success(request, 'Abonelik tipiniz başarıyla güncellendi.')
            return redirect('accounts:user_profile')
    else:
        form = SubscriptionChangeForm(initial={'subscription_type': user.subscription.subscription_type})
    return render(request, 'accounts/change_subscription.html', {'form': form})

@subscription_type_required('premium')
@login_required
def premium_feature(request):
    return render(request, 'accounts/premium_feature.html')
