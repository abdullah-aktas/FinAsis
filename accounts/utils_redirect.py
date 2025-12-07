"""
Kullanıcı yönlendirme yardımcı fonksiyonları
Kullanıcı tipine göre uygun dashboard'a yönlendirir
"""

from django.urls import reverse


def get_user_dashboard_url(user):
    """
    Kullanıcının tipine ve rolüne göre uygun dashboard URL'ini döndürür

    Args:
        user: CustomUser instance

    Returns:
        str: Dashboard URL
    """
    if not user or not user.is_authenticated:
        return reverse("home")

    # Eğer kullanıcının user_type'ı varsa ona göre yönlendir
    if hasattr(user, "user_type") and user.user_type:
        user_type_code = user.user_type.code.lower()

        # KOBİ kullanıcıları
        if user_type_code in ["kobi", "sme", "business"]:
            return reverse("accounts:modul_kobi")

        # Mali Müşavir / Muhasebeci
        elif user_type_code in ["mali_musavir", "accountant", "advisor"]:
            return reverse("accounts:user_profile")

        # Muhasebe Elemanı
        elif user_type_code in [
            "muhasebe_elemani",
            "accounting_staff",
            "accountant_staff",
        ]:
            return reverse("accounts:modul_muhasebe")

        # Satış Elemanı
        elif user_type_code in ["satis_elemani", "sales_staff", "salesperson"]:
            return reverse("accounts:modul_satis")

        # Depo Elemanı
        elif user_type_code in ["depo_elemani", "warehouse_staff", "warehouse"]:
            return reverse("accounts:modul_depo")

        # Eğitimci
        elif user_type_code in ["egitimci", "teacher", "instructor"]:
            return reverse("accounts:modul_egitimci")

        # Öğrenci
        elif user_type_code in ["ogrenci", "student"]:
            return reverse("accounts:modul_ogrenci")

        # Yatırımcı
        elif user_type_code in ["yatirimci", "investor"]:
            return reverse("accounts:user_profile")

        # Oyuncu
        elif user_type_code in ["oyuncu", "gamer"]:
            return reverse("accounts:modul_oyuncu")

    # Role göre yönlendirme (fallback)
    if hasattr(user, "role"):
        if user.role == "admin":
            return reverse("accounts:user_profile")
        elif user.role == "staff":
            return reverse("accounts:user_profile")

    # Şirket varsa muhasebe dashboard'a
    if hasattr(user, "company") and user.company:
        return reverse("accounting:dashboard")

    # Varsayılan: profil sayfası
    return reverse("accounts:user_profile")


def get_redirect_after_login(request, user):
    """
    Giriş sonrası yönlendirme URL'ini belirler

    Args:
        request: HttpRequest
        user: CustomUser instance

    Returns:
        str: Redirect URL
    """
    # 1. Öncelik: 'next' parametresi (güvenli URL kontrolü ile)
    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url:
        # Güvenlik: Sadece internal URL'lere izin ver
        if next_url.startswith("/") and not next_url.startswith("//"):
            return next_url

    # 2. Session'da kaydedilmiş redirect varsa
    if "post_login_redirect" in request.session:
        redirect_url = request.session.pop("post_login_redirect")
        return redirect_url

    # 3. Kullanıcı tipine göre dashboard
    return get_user_dashboard_url(user)


def set_post_login_redirect(request, url):
    """
    Giriş sonrası yönlendirme URL'ini session'a kaydeder

    Args:
        request: HttpRequest
        url: str - Redirect URL
    """
    request.session["post_login_redirect"] = url
