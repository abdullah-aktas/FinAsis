from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from accounting.models import Invoice
from .models import UserSettings, CustomUser, SubscriptionType, SubscriptionLog
from django.utils import timezone
from django.contrib import messages
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from .forms import RegisterForm
from .presenters import UserDashboardPresenter
from .utils import user_type_required, subscription_type_required
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


# Create your views here.
@user_type_required("kobi", "egitimci")
@login_required
def user_invoices(request):
    invoices = Invoice.objects.filter(customer__company=request.user.company)
    return render(request, "invoices/list.html", {"invoices": invoices})


@login_required
def user_profile(request):
    presenter = UserDashboardPresenter(request)
    return presenter.render()


@login_required
def company_detail(request):
    company = getattr(request.user, "company", None)
    if not company:
        messages.error(request, "Şirket bilgisi bulunamadı.")
        return redirect("accounts:user_profile")
    return render(request, "accounts/company_detail.html", {"company": company})


@login_required
def company_edit(request):
    company = getattr(request.user, "company", None)
    if not company:
        messages.error(request, "Şirket bilgisi bulunamadı.")
        return redirect("accounts:user_profile")
    if request.method == "POST":
        company.name = request.POST.get("name", company.name)
        company.sector = request.POST.get("sector", company.sector)
        company.tax_number = request.POST.get("tax_number", company.tax_number)
        company.address = request.POST.get("address", company.address)
        company.phone = request.POST.get("phone", company.phone)
        company.email = request.POST.get("email", company.email)
        if "logo" in request.FILES:
            company.logo = request.FILES["logo"]
        company.save()
        messages.success(request, "Şirket bilgileri başarıyla güncellendi.")
        return redirect("accounts:user_profile")
    return render(request, "accounts/company_edit.html", {"company": company})


@login_required
def user_settings(request):
    user = request.user
    settings = getattr(user, "settings", None)
    if not settings:
        try:
            user_obj = CustomUser.objects.get(pk=user.pk)
            settings = UserSettings.objects.create(user=user_obj)
        except CustomUser.DoesNotExist:
            messages.error(
                request, "Kullanıcı hesabınız bulunamadı. Lütfen tekrar giriş yapın."
            )
            return redirect("accounts:login")
        except Exception as e:
            messages.error(request, f"Ayar kaydı oluşturulamadı: {e}")
            return redirect("accounts:login")
    if request.method == "POST":
        settings.email_notifications = bool(request.POST.get("email_notifications"))
        settings.dark_mode = bool(request.POST.get("dark_mode"))
        settings.save()
        messages.success(request, "Ayarlarınız başarıyla güncellendi.")
        return redirect("accounts:user_profile")
    return render(request, "accounts/user_settings.html", {"settings": settings})


def accounts_home(request):
    return redirect("accounts:user_profile")


def home(request):
    return render(request, "accounting/home.html")


def register(request):
    """Kayıt view (basitleştirilmiş ve sağlam)."""
    if request.method == "POST":
        # Testlerin gönderdiği alan adlarıyla uyum: password/password_confirm -> password1/password2
        data = request.POST.copy()
        if "password" in data and "password1" not in data:
            data["password1"] = data.get("password", "")
            data["password2"] = data.get("password_confirm", data.get("password", ""))
        form = RegisterForm(data)
        if form.is_valid():
            user = form.save()
            # Kullanıcı ayar kaydı oluştur (idempotent)
            UserSettings.objects.get_or_create(user=user)
            # Login: backend parametresi ile
            try:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
            except Exception:
                # backend attribute yoksa fallback
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
            messages.success(request, "Kayıt başarılı, hoş geldiniz!")
            # Hedef kitle seçimini planlar sayfasına taşı
            audience = request.POST.get("audience")
            plans_url = reverse("billing:plans")
            if audience in ("sme", "edu"):
                plans_url = f"{plans_url}?audience={audience}"
            return redirect(plans_url)
        else:
            # Zayıf şifre vb. durumlarda 400 döndür
            messages.error(request, "Form hataları var, lütfen düzeltin.")
            return render(
                request, "registration/register.html", {"form": form}, status=400
            )
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def report_redirect(request):
    return redirect("accounting:summary_report")


def summary_report(request):
    return render(request, "accounting/summary_report.html")


def income_expense_chart_data(request):
    return render(request, "accounting/income_expense_chart.html")


def chart_dashboard(request):
    return render(request, "accounting/chart_dashboard.html")


@user_type_required("kobi")
@login_required
def modul_kobi(request):
    return render(request, "accounts/modul_kobi.html")


@user_type_required("egitimci")
@login_required
def modul_egitimci(request):
    return render(request, "accounts/modul_egitimci.html")


@user_type_required("ogrenci")
@login_required
def modul_ogrenci(request):
    return render(request, "accounts/modul_ogrenci.html")


@user_type_required("oyuncu")
@login_required
def modul_oyuncu(request):
    return render(request, "accounts/modul_oyuncu.html")


@user_type_required("muhasebe_elemani")
@login_required
def modul_muhasebe(request):
    """Muhasebe elemanı dashboard"""
    company = getattr(request.user, "company", None)

    # Bugün, bu hafta ve bu ay istatistikleri
    from datetime import datetime, timedelta

    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    stats = {
        "today_invoices": 0,
        "week_invoices": 0,
        "month_invoices": 0,
        "pending_tasks": 0,
    }

    if company:
        stats["today_invoices"] = Invoice.objects.filter(
            company=company, issue_date=today
        ).count()

        stats["week_invoices"] = Invoice.objects.filter(
            company=company, issue_date__gte=week_start
        ).count()

        stats["month_invoices"] = Invoice.objects.filter(
            company=company, issue_date__gte=month_start
        ).count()

    context = {
        "stats": stats,
        "company": company,
        "recent_invoices": (
            Invoice.objects.filter(company=company).order_by("-issue_date")[:10]
            if company
            else []
        ),
    }

    return render(request, "accounts/modul_muhasebe.html", context)


@user_type_required("satis_elemani")
@login_required
def modul_satis(request):
    """Satış elemanı dashboard"""
    company = getattr(request.user, "company", None)

    from datetime import datetime
    from django.db.models import Sum, Count

    today = datetime.now().date()
    month_start = today.replace(day=1)

    stats = {
        "month_sales": 0,
        "month_count": 0,
        "pending_orders": 0,
        "customer_count": 0,
    }

    if company:
        month_invoices = Invoice.objects.filter(
            company=company, issue_date__gte=month_start
        )

        month_aggregate = month_invoices.aggregate(
            total=Sum("total_amount"), count=Count("id")
        )

        stats["month_sales"] = float(month_aggregate["total"] or 0)
        stats["month_count"] = month_aggregate["count"] or 0
        stats["customer_count"] = (
            Invoice.objects.filter(company=company)
            .values("customer")
            .distinct()
            .count()
        )

    context = {
        "stats": stats,
        "company": company,
        "recent_sales": (
            Invoice.objects.filter(company=company).order_by("-issue_date")[:10]
            if company
            else []
        ),
    }

    return render(request, "accounts/modul_satis.html", context)


@user_type_required("depo_elemani")
@login_required
def modul_depo(request):
    """Depo elemanı dashboard"""
    company = getattr(request.user, "company", None)

    # Depo ve stok istatistikleri
    stats = {
        "low_stock_items": 0,
        "pending_shipments": 0,
        "today_movements": 0,
        "total_items": 0,
    }

    # Eğer stok modülü varsa, buradan verileri çek
    # Şimdilik placeholder

    context = {
        "stats": stats,
        "company": company,
    }

    return render(request, "accounts/modul_depo.html", context)


# Not: 'invoices/list.html' template dosyasını 'FinAsisV1/apps/accounts/templates/invoices/list.html' olarak oluşturmalısınız.


@receiver(post_save, sender=CustomUser)
def create_user_settings(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "settings"):
        UserSettings.objects.create(user=instance)


class SubscriptionChangeForm(forms.Form):
    subscription_type = forms.ModelChoiceField(
        queryset=SubscriptionType.objects.all(), label="Abonelik Tipi"
    )


@login_required
def change_subscription(request):
    user = request.user
    if not hasattr(user, "subscription"):
        return redirect("accounts:user_profile")
    if request.method == "POST":
        form = SubscriptionChangeForm(request.POST)
        if form.is_valid():
            new_type = form.cleaned_data["subscription_type"]
            old_type = user.subscription.subscription_type
            user.subscription.subscription_type = new_type
            user.subscription.save()
            SubscriptionLog.objects.create(
                user=user,
                old_subscription=old_type,
                new_subscription=new_type,
                note="Kullanıcı tarafından değiştirildi.",
            )
            # E-posta bildirimi gönder
            send_mail(
                subject="Abonelik Değişikliği Bildirimi",
                message=f"Sayın {user.get_full_name() or user.username},\n\nAbonelik tipiniz başarıyla değiştirildi.\n\nEski abonelik: {old_type.name if old_type else '-'}\nYeni abonelik: {new_type.name if new_type else '-'}\nTarih: {timezone.now().strftime('%d.%m.%Y %H:%M')}\n\nFinAsis Ekibi",
                from_email=None,  # settings.DEFAULT_FROM_EMAIL kullanılır
                recipient_list=[user.email],
                fail_silently=True,
            )
            messages.success(request, "Abonelik tipiniz başarıyla güncellendi.")
            return redirect("accounts:user_profile")
    else:
        form = SubscriptionChangeForm(
            initial={"subscription_type": user.subscription.subscription_type}
        )
    return render(request, "accounts/change_subscription.html", {"form": form})


@subscription_type_required("premium")
@login_required
def premium_feature(request):
    return render(request, "accounts/premium_feature.html")


def custom_logout(request):
    """
    Özel logout view - session temizleme ve redirect kontrolü
    GET ve POST request'lerini destekler
    """
    if request.user.is_authenticated:
        username = request.user.username
        logger.info(f"Kullanıcı çıkış yapıyor: {username} (Method: {request.method})")

        # Session'ı temizle
        request.session.flush()

        # Logout işlemi
        logout(request)

        messages.success(request, "Başarıyla çıkış yaptınız.")
        logger.info(f"Kullanıcı {username} başarıyla çıkış yaptı")
    else:
        logger.warning("Çıkış yapmaya çalışan kullanıcı zaten giriş yapmamış")

    # Ana sayfaya yönlendir
    return redirect("home")
