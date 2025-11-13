from __future__ import annotations

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django_otp import devices_for_user

from common.services import audit_logger


class OTPLoginView(LoginView):
    """
    Standart giriş formundan sonra MFA cihazı varsa doğrulama adımına yönlendirir.
    """

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
        return response

