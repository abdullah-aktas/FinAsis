# permissions/decorators.py - FinAsis için kapsamlı yetkilendirme sistemi

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin


def requires_role(required_roles, allow_higher_hierarchy=True):
    """
    Belirli rolleri gerekli kılan decorator

    Args:
        required_roles (list): Gerekli roller listesi
        allow_higher_hierarchy (bool): Daha yüksek hiyerarşi seviyesindeki rolleri kabul et
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user_profile = getattr(request.user, "profile", None)

            if not user_profile:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "error": "Yetki yok",
                            "message": "Kullanıcı profili bulunamadı",
                        },
                        status=403,
                    )

                messages.error(request, "Kullanıcı profili bulunamadı.")
                return redirect("accounts:user_profile")

            user_role = user_profile.role.name
            user_hierarchy = user_profile.role.hierarchy_level

            # Doğrudan rol kontrolü
            if user_role in required_roles:
                return view_func(request, *args, **kwargs)

            # Hiyerarşi kontrolü (eğer izin verilirse)
            if allow_higher_hierarchy:
                # Gerekli rollerden en düşük hiyerarşi seviyesini bul
                from accounts.role_models import UserRole

                required_hierarchy_levels = UserRole.objects.filter(
                    name__in=required_roles
                ).values_list("hierarchy_level", flat=True)

                if required_hierarchy_levels:
                    min_required_level = min(required_hierarchy_levels)
                    if user_hierarchy <= min_required_level:
                        return view_func(request, *args, **kwargs)

            # Erişim reddedildi
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "error": "Yetki yok",
                        "message": f'Bu işlem için {", ".join(required_roles)} rollerinden birine sahip olmanız gerekir.',
                    },
                    status=403,
                )

            return render(
                request,
                "errors/403.html",
                {
                    "error_message": f'Bu işlem için {", ".join(required_roles)} rollerinden birine sahip olmanız gerekir.',
                    "required_roles": required_roles,
                    "user_role": user_role,
                },
                status=403,
            )

        return _wrapped_view

    return decorator


def requires_permission(permission_attr, error_message=None):
    """
    Belirli bir izni gerekli kılan decorator

    Args:
        permission_attr (str): UserRole modelindeki izin alanı adı
        error_message (str): Özel hata mesajı
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user_profile = getattr(request.user, "profile", None)

            if not user_profile:
                raise PermissionDenied("Kullanıcı profili bulunamadı")

            # İzni kontrol et
            has_permission = getattr(user_profile.role, permission_attr, False)

            if not has_permission:
                default_message = (
                    f"Bu işlem için '{permission_attr}' iznine sahip olmanız gerekir."
                )
                message = error_message or default_message

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Yetki yok", "message": message}, status=403
                    )

                return render(
                    request, "errors/403.html", {"error_message": message}, status=403
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def requires_plan_feature(feature_attr, error_message=None):
    """
    Belirli bir plan özelliğini gerekli kılan decorator

    Args:
        feature_attr (str): SubscriptionPlan modelindeki özellik alanı adı
        error_message (str): Özel hata mesajı
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            subscription = getattr(request.user, "subscription", None)

            if not subscription or not subscription.is_active:
                message = "Bu özelliği kullanmak için aktif bir aboneliğe sahip olmanız gerekir."
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "error": "Abonelik gerekli",
                            "message": message,
                            "redirect": "/billing/plans/",
                        },
                        status=402,
                    )  # Payment Required

                messages.warning(request, message)
                return redirect("billing:plans")

            # Özelliği kontrol et
            has_feature = getattr(subscription.plan, feature_attr, False)

            if not has_feature:
                default_message = "Bu özellik sizin planınızda bulunmuyor. Planınızı yükseltmek için tıklayın."
                message = error_message or default_message

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "error": "Plan yükseltme gerekli",
                            "message": message,
                            "redirect": "/billing/plans/",
                        },
                        status=402,
                    )

                messages.warning(request, message)
                return redirect("billing:plans")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def check_transaction_limit(view_func):
    """İşlem limitini kontrol eden decorator"""

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        subscription = getattr(request.user, "subscription", None)

        if subscription and subscription.is_active:
            if not subscription.can_perform_action("transaction"):
                message = "Bu ay işlem limitinizi doldurdunuz. Planınızı yükseltebilir veya önümüzdeki ay bekleyebilirsiniz."

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "error": "İşlem limiti",
                            "message": message,
                            "redirect": "/billing/plans/",
                        },
                        status=429,
                    )  # Too Many Requests

                messages.warning(request, message)
                return redirect("billing:plans")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


# Kısayol decorator'lar
def admin_required(view_func):
    """Admin yetkisi gerekli kılan decorator"""
    return requires_role(["super_admin", "admin"])(view_func)


def financial_access_required(view_func):
    """Mali veri erişimi gerekli kılan decorator"""
    return requires_permission("can_view_all_finances")(view_func)


def financial_edit_required(view_func):
    """Mali veri düzenleme yetkisi gerekli kılan decorator"""
    return requires_permission("can_edit_finances")(view_func)


def user_management_required(view_func):
    """Kullanıcı yönetimi yetkisi gerekli kılan decorator"""
    return requires_permission("can_manage_users")(view_func)


def ai_access_required(view_func):
    """AI asistan erişimi gerekli kılan decorator"""
    return requires_plan_feature("has_ai_assistant")(view_func)


def blockchain_access_required(view_func):
    """Blockchain modülü erişimi gerekli kılan decorator"""
    return requires_plan_feature("has_blockchain")(view_func)


# Class-based view mixinleri
class RoleRequiredMixin(LoginRequiredMixin, View):
    """Class-based view'lar için rol gereksinimi mixin'i"""

    required_roles = []
    allow_higher_hierarchy = True

    def dispatch(self, request, *args, **kwargs):
        user_profile = getattr(request.user, "profile", None)

        if not user_profile:
            raise PermissionDenied("Kullanıcı profili bulunamadı")

        user_role = user_profile.role.name
        user_hierarchy = user_profile.role.hierarchy_level

        # Doğrudan rol kontrolü
        if user_role in self.required_roles:
            return super().dispatch(request, *args, **kwargs)

        # Hiyerarşi kontrolü
        if self.allow_higher_hierarchy and self.required_roles:
            from accounts.role_models import UserRole

            required_hierarchy_levels = UserRole.objects.filter(
                name__in=self.required_roles
            ).values_list("hierarchy_level", flat=True)

            if required_hierarchy_levels:
                min_required_level = min(required_hierarchy_levels)
                if user_hierarchy <= min_required_level:
                    return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied(
            f"Bu işlem için {', '.join(self.required_roles)} rollerinden birine sahip olmanız gerekir."
        )


class PermissionRequiredMixin(LoginRequiredMixin, View):
    """Class-based view'lar için izin gereksinimi mixin'i"""

    required_permission = None

    def dispatch(self, request, *args, **kwargs):
        if not self.required_permission:
            raise ValueError("required_permission belirtilmeli")

        user_profile = getattr(request.user, "profile", None)
        if not user_profile:
            raise PermissionDenied("Kullanıcı profili bulunamadı")

        has_permission = getattr(user_profile.role, self.required_permission, False)
        if not has_permission:
            raise PermissionDenied(
                f"Bu işlem için '{self.required_permission}' iznine sahip olmanız gerekir."
            )

        return super().dispatch(request, *args, **kwargs)


# Özel izin kontrolleri
def can_manage_user(current_user, target_user):
    """Bir kullanıcının başka bir kullanıcıyı yönetip yönetemeyeceğini kontrol eder"""
    current_profile = getattr(current_user, "profile", None)
    target_profile = getattr(target_user, "profile", None)

    if not current_profile or not target_profile:
        return False

    return current_profile.can_manage_user(target_user)


def can_access_company(user, company):
    """Kullanıcının belirli bir şirkete erişip erişemeyeceğini kontrol eder"""
    user_profile = getattr(user, "profile", None)

    if not user_profile:
        return False

    # Süper admin ve sistem admini her şirkete erişebilir
    if user_profile.role.name in ["super_admin", "admin"]:
        return True

    # Şirket sahibi kontrol
    if hasattr(company, "owner") and company.owner == user:
        return True

    # Şirket çalışanı kontrol
    if hasattr(company, "employees") and user in company.employees.all():
        return True

    # Mali müşavir kontrol (müşteri şirketleri)
    if (
        user_profile.role.name == "financial_advisor"
        and hasattr(company, "financial_advisor")
        and company.financial_advisor == user
    ):
        return True

    return False


# Eski decorator'lar (geriye uyumluluk için)
def permission_required(perm, login_url=None, raise_exception=True):
    """Django'nun varsayılan permission_required decorator'ı"""

    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm

        if user.has_perms(perms):
            return True

        if raise_exception:
            raise PermissionDenied
        return False

    return user_passes_test(check_perms, login_url=login_url)


def has_finance_permission(permission_name):
    """Finans modülü izin kontrolü decorator'ı"""
    return permission_required(f"finance.{permission_name}")


def has_permission(permission_name):
    """Kullanıcının belirtilen izne sahip olup olmadığını kontrol eden decorator"""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return wrapped

    return decorator


def is_finance_manager(function=None):
    """Finans yöneticisi kontrolü"""
    actual_decorator = user_passes_test(
        lambda u: u.groups.filter(name="Finance Manager").exists() or u.is_superuser
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def can_manage_transactions(function=None):
    """Kullanıcının işlem yönetimi yetkisine sahip olup olmadığını kontrol eden decorator"""
    actual_decorator = user_passes_test(
        lambda u: u.has_perm("finance.manage_transactions")
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
