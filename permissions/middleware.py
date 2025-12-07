# permissions/middleware.py - Güvenlik middleware'i

import logging
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
import json

logger = logging.getLogger(__name__)


class RoleSecurityMiddleware:
    """Rol tabanlı güvenlik middleware'i"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pre-process
        self.process_request(request)

        # İstek işle
        response = self.get_response(request)

        # Post-process
        self.process_response(request, response)

        return response

    def process_request(self, request):
        """İstek öncesi güvenlik kontrolleri"""

        # Authenticated kullanıcılar için kontroller
        if request.user.is_authenticated:
            self._check_profile_exists(request)
            self._check_subscription_status(request)
            self._check_account_security(request)
            self._log_user_activity(request)

    def process_response(self, request, response):
        """İstek sonrası güvenlik kontrolleri"""

        if request.user.is_authenticated:
            self._update_last_activity(request)

        return response

    def _check_profile_exists(self, request):
        """Kullanıcı profilinin varlığını kontrol et"""
        try:
            profile = request.user.profile
            if not profile.role:
                logger.warning(f"User {request.user.username} has no role assigned")
                messages.warning(
                    request,
                    "Hesabınız için rol tanımlanmamış. Lütfen yönetici ile iletişime geçin.",
                )
        except (AttributeError, Exception):
            logger.error(f"User {request.user.username} has no profile")
            # Profil yoksa oluştur
            from accounts.role_models import UserRole, RoleBasedUserProfile

            try:
                default_role = UserRole.objects.get(name="viewer")
                RoleBasedUserProfile.objects.create(
                    user=request.user, role=default_role
                )
                logger.info(f"Created default profile for user {request.user.username}")
            except (Exception, AttributeError):
                logger.error(
                    f"Failed to create profile for user {request.user.username}"
                )

    def _check_subscription_status(self, request):
        """Abonelik durumunu kontrol et"""
        try:
            subscription = request.user.subscription

            if not subscription.is_active:
                # Süresi dolmuş abonelik uyarısı
                if subscription.status == "expired":
                    if "subscription_warning_shown" not in request.session:
                        messages.error(
                            request,
                            "Aboneliğinizin süresi dolmuştur. Bazı özelliklere erişiminiz kısıtlanmıştır.",
                        )
                        request.session["subscription_warning_shown"] = True

                # Kritik sayfalarda erişimi engelle
                restricted_paths = ["/ai/", "/blockchain/", "/premium/"]
                if any(request.path.startswith(path) for path in restricted_paths):
                    messages.error(
                        request, "Bu özellik için aktif abonelik gereklidir."
                    )
                    return redirect("/billing/upgrade/")

        except (AttributeError, Exception):
            # Abonelik yoksa
            logger.warning(f"User {request.user.username} has no subscription")

    def _check_account_security(self, request):
        """Hesap güvenlik kontrolleri"""
        try:
            profile = request.user.profile

            # Hesap kilitli mi?
            if profile.is_locked:
                messages.error(request, "Hesabınız güvenlik nedeniyle kilitlenmiştir.")
                from django.contrib.auth import logout

                logout(request)
                return redirect("/accounts/login/")

            # Çok fazla başarısız giriş denemesi var mı?
            if profile.login_attempts >= 5:
                profile.is_locked = True
                profile.save()
                logger.warning(
                    f"Account locked for user {request.user.username} due to failed login attempts"
                )

            # Şifre değişimi gerekli mi? (90 gün)
            if profile.last_password_change:
                days_since_change = (timezone.now() - profile.last_password_change).days
                if days_since_change > 90:
                    if "password_change_warning_shown" not in request.session:
                        messages.warning(
                            request,
                            "Şifrenizi 90 gündür değiştirmiyorsunuz. Güvenliğiniz için şifrenizi güncelleyin.",
                        )
                        request.session["password_change_warning_shown"] = True

        except Exception as e:
            logger.error(
                f"Security check failed for user {request.user.username}: {str(e)}"
            )

    def _log_user_activity(self, request):
        """Kullanıcı aktivitesini kaydet"""
        try:
            # Kritik işlemler için detaylı log
            critical_paths = ["/admin/", "/accounts/users/", "/billing/", "/api/"]

            if any(request.path.startswith(path) for path in critical_paths):
                logger.info(
                    f"Critical access: User {request.user.username} accessed {request.path} from IP {self._get_client_ip(request)}"
                )

            # Rate limiting kontrolü
            self._check_rate_limit(request)

        except Exception as e:
            logger.error(f"Activity logging failed: {str(e)}")

    def _update_last_activity(self, request):
        """Son aktivite zamanını güncelle"""
        try:
            cache_key = f"user_activity_{request.user.id}"
            cache.set(cache_key, timezone.now(), timeout=300)  # 5 dakika
        except Exception:
            pass

    def _check_rate_limit(self, request):
        """Rate limiting kontrolleri"""
        try:
            ip = self._get_client_ip(request)
            user_id = request.user.id

            # IP bazlı rate limit (saatte 1000 istek)
            ip_key = f"rate_limit_ip_{ip}"
            ip_requests = cache.get(ip_key, 0)

            if ip_requests > 1000:
                logger.warning(f"Rate limit exceeded for IP {ip}")
                raise TooManyRequests("Too many requests from this IP")

            cache.set(ip_key, ip_requests + 1, timeout=3600)

            # Kullanıcı bazlı rate limit (saatte 500 istek)
            user_key = f"rate_limit_user_{user_id}"
            user_requests = cache.get(user_key, 0)

            if user_requests > 500:
                logger.warning(f"Rate limit exceeded for user {request.user.username}")
                raise TooManyRequests("Too many requests from this user")

            cache.set(user_key, user_requests + 1, timeout=3600)

        except Exception as e:
            if "TooManyRequests" in str(e):
                raise
            logger.error(f"Rate limit check failed: {str(e)}")

    def _get_client_ip(self, request):
        """İstemci IP adresini al"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class PermissionAuditMiddleware:
    """İzin denetim middleware'i"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # İzin kontrolü öncesi
        violation = self._check_permission_violations(request)
        if violation:
            return self._handle_violation(request, violation)

        response = self.get_response(request)

        # İzin kullanımını kaydet
        self._log_permission_usage(request, response)

        return response

    def _check_permission_violations(self, request):
        """İzin ihlallerini kontrol et"""
        if not request.user.is_authenticated:
            return None

        try:
            # URL bazlı izin kontrolleri
            url_permissions = {
                "/admin/": "can_manage_users",
                "/accounting/edit/": "can_edit_finances",
                "/finance/approve/": "can_approve_transactions",
                "/reports/generate/": "can_generate_reports",
                "/ai/": "can_access_ai",
                "/blockchain/": "can_use_blockchain",
            }

            for url_pattern, required_permission in url_permissions.items():
                if request.path.startswith(url_pattern):
                    if not self._user_has_permission(request.user, required_permission):
                        return {
                            "type": "permission_denied",
                            "permission": required_permission,
                            "url": request.path,
                            "user": request.user.username,
                        }

            # Rol hiyerarşi kontrolü
            if "/users/" in request.path and request.method in [
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            ]:
                target_user_id = self._extract_user_id_from_path(request.path)
                if target_user_id and not self._can_manage_target_user(
                    request.user, target_user_id
                ):
                    return {
                        "type": "hierarchy_violation",
                        "url": request.path,
                        "user": request.user.username,
                        "target_user": target_user_id,
                    }

            # Abonelik özellik kontrolü
            subscription_features = {
                "/ai/": "has_ai_assistant",
                "/blockchain/": "has_blockchain",
                "/api/": "has_api_access",
                "/education/premium/": "has_education",
            }

            for url_pattern, required_feature in subscription_features.items():
                if request.path.startswith(url_pattern):
                    if not self._user_has_subscription_feature(
                        request.user, required_feature
                    ):
                        return {
                            "type": "subscription_required",
                            "feature": required_feature,
                            "url": request.path,
                            "user": request.user.username,
                        }

        except Exception as e:
            logger.error(f"Permission check failed: {str(e)}")

        return None

    def _handle_violation(self, request, violation):
        """İzin ihlalini handle et"""
        # Log kaydet
        logger.warning(f"Permission violation: {json.dumps(violation)}")

        # Güvenlik event'i kaydet
        self._log_security_event(request, violation)

        # Kullanıcıya uygun response döndür
        if request.path.startswith("/api/"):
            return JsonResponse(
                {
                    "error": "Permission denied",
                    "code": violation["type"],
                    "message": self._get_violation_message(violation),
                },
                status=403,
            )
        else:
            messages.error(request, self._get_violation_message(violation))

            if violation["type"] == "subscription_required":
                return redirect("/billing/upgrade/")
            else:
                return redirect("/dashboard/")

    def _get_violation_message(self, violation):
        """İhlal mesajı oluştur"""
        if violation["type"] == "permission_denied":
            return (
                f"Bu işlem için '{violation['permission']}' yetkisine sahip değilsiniz."
            )
        elif violation["type"] == "hierarchy_violation":
            return "Bu kullanıcı üzerinde işlem yapma yetkiniz bulunmamaktadır."
        elif violation["type"] == "subscription_required":
            return f"Bu özellik '{violation['feature']}' abonelik planında mevcuttur."
        else:
            return "Bu işlem için yetkiniz bulunmamaktadır."

    def _user_has_permission(self, user, permission):
        """Kullanıcının izni var mı?"""
        try:
            return getattr(user.profile.role, permission, False)
        except (AttributeError, Exception):
            return False

    def _user_has_subscription_feature(self, user, feature):
        """Kullanıcının abonelik özelliği var mı?"""
        try:
            subscription = user.subscription
            return subscription.is_active and getattr(subscription.plan, feature, False)
        except (AttributeError, Exception):
            return False

    def _can_manage_target_user(self, manager_user, target_user_id):
        """Hedef kullanıcıyı yönetebilir mi?"""
        try:
            from django.contrib.auth import get_user_model
            from accounts.role_models import RoleBasedUserProfile

            User = get_user_model()

            target_user = User.objects.get(pk=target_user_id)

            # Profile'lar var mı kontrol et
            try:
                manager_profile = RoleBasedUserProfile.objects.get(user=manager_user)
                target_profile = RoleBasedUserProfile.objects.get(user=target_user)
            except RoleBasedUserProfile.DoesNotExist:
                return False

            manager_level = manager_profile.role.hierarchy_level
            target_level = target_profile.role.hierarchy_level

            return (
                manager_profile.role.can_manage_users
                and manager_level < target_level
                and manager_user.pk != target_user.pk
            )
        except (AttributeError, Exception):
            return False

    def _extract_user_id_from_path(self, path):
        """URL'den kullanıcı ID'si çıkar"""
        try:
            import re

            match = re.search(r"/users/(\d+)/", path)
            return int(match.group(1)) if match else None
        except (ValueError, AttributeError, Exception):
            return None

    def _log_permission_usage(self, request, response):
        """İzin kullanımını kaydet"""
        try:
            if request.user.is_authenticated and response.status_code == 200:
                # Başarılı işlemler için audit log
                if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                    logger.info(
                        f"Permission usage: User {request.user.username} performed {request.method} on {request.path}"
                    )
        except (AttributeError, Exception):
            pass

    def _log_security_event(self, request, violation):
        """Güvenlik olayını kaydet"""
        try:
            # SecurityEvent modeli yoksa basit log kaydet
            logger.error(
                f"Security violation: {json.dumps(violation)} by user {request.user.username} from IP {self._get_client_ip(request)}"
            )

            # İsteğe bağlı: SecurityEvent modeli varsa kullan
            # from audit.models import SecurityEvent
            # SecurityEvent.objects.create(
            #     user=request.user,
            #     event_type='permission_violation',
            #     description=json.dumps(violation),
            #     ip_address=self._get_client_ip(request),
            #     user_agent=request.META.get('HTTP_USER_AGENT', ''),
            #     severity='medium' if violation['type'] == 'permission_denied' else 'high'
            # )
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")

    def _get_client_ip(self, request):
        """İstemci IP adresini al"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class TooManyRequests(Exception):
    """Rate limit aşımı exception'ı"""

    pass


# Middleware'leri settings.py'ye eklemek için:
"""
MIDDLEWARE = [
    # ... diğer middleware'ler
    'permissions.middleware.RoleSecurityMiddleware',
    'permissions.middleware.PermissionAuditMiddleware',
    # ... 
]
"""
