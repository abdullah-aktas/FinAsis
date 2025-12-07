from __future__ import annotations

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django_otp import devices_for_user

from common.services import audit_logger
from .utils_redirect import get_redirect_after_login


class OTPLoginView(LoginView):
    """
    Standart giriş formundan sonra MFA cihazı varsa doğrulama adımına yönlendirir.
    Kullanıcıyı tipine göre uygun dashboard'a yönlendirir.
    """

    def get_success_url(self):
        """
        Kullanıcı tipine göre dinamik olarak dashboard URL'ini belirler
        """
        return get_redirect_after_login(self.request, self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        confirmed_devices = list(devices_for_user(user, confirmed=True))
        if confirmed_devices:
            success_url = self.get_success_url()
            self.request.session["post_otp_redirect"] = success_url
            audit_logger.log_security_event(
                action="auth.mfa.challenge",
                actor=user,
                request=self.request,
                resource=f"user:{user.pk}",
                metadata={"redirect": success_url},
            )
            return redirect("accounts:otp_verify")

        # MFA yoksa direkt kullanıcı tipine göre yönlendir
        audit_logger.log_security_event(
            action="auth.login.success",
            actor=user,
            request=self.request,
            resource=f"user:{user.pk}",
            metadata={"redirect": self.get_success_url()},
        )
        return response
