from __future__ import annotations

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django_otp import devices_for_user, login as otp_login
from django_otp.plugins.otp_totp.models import TOTPDevice

from accounts.forms import OTPSetupForm, OTPVerifyForm
from common.services import audit_logger


def _get_safe_redirect(request, fallback=None):
    next_url = request.GET.get("next") or request.session.pop("post_otp_redirect", None)
    if not next_url:
        fallback = fallback or settings.LOGIN_REDIRECT_URL
        return resolve_url(fallback)
    if url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
        return next_url
    return resolve_url(fallback or settings.LOGIN_REDIRECT_URL)


@login_required
def otp_verify(request):
    confirmed_devices = [device for device in devices_for_user(request.user, confirmed=True)]
    if not confirmed_devices:
        return redirect(_get_safe_redirect(request))

    if getattr(request, "otp_device", None) is not None:
        return redirect(_get_safe_redirect(request))

    form = OTPVerifyForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            token = form.cleaned_data["token"]
            for device in confirmed_devices:
                if device.verify_token(token):
                    otp_login(request, device)
                    audit_logger.log_security_event(
                        action="auth.mfa.success",
                        actor=request.user,
                        request=request,
                        resource=f"TOTPDevice:{device.pk}",
                        metadata={"device_name": device.name},
                    )
                    messages.success(request, "Çok faktörlü doğrulama tamamlandı.")
                    return redirect(_get_safe_redirect(request))
            audit_logger.log_security_event(
                action="auth.mfa.failure",
                actor=request.user,
                request=request,
                resource=f"user:{request.user.pk}",
                metadata={"reason": "invalid_token"},
                success=False,
            )
            form.add_error(None, "Doğrulama kodu hatalı veya süresi dolmuş.")

    context = {
        "form": form,
        "has_devices": bool(confirmed_devices),
        "next": request.GET.get("next"),
    }
    return render(request, "accounts/otp_verify.html", context)


@login_required
def otp_setup(request):
    confirmed_device = next((d for d in devices_for_user(request.user, confirmed=True)), None)
    pending_device = None

    if not confirmed_device:
        pending_device = next(
            (d for d in devices_for_user(request.user, confirmed=False)),
            None,
        )
        if pending_device is None:
            pending_device = TOTPDevice.objects.create(
                user=request.user,
                name="Authenticator",
                confirmed=False,
            )

    form = OTPSetupForm(request.POST or None)
    if request.method == "POST" and pending_device:
        if form.is_valid():
            token = form.cleaned_data["token"]
            if pending_device.verify_token(token):
                pending_device.confirmed = True
                pending_device.save()
                otp_login(request, pending_device)
                audit_logger.log_security_event(
                    action="auth.mfa.activated",
                    actor=request.user,
                    request=request,
                    resource=f"TOTPDevice:{pending_device.pk}",
                    metadata={"device_name": pending_device.name},
                )
                messages.success(request, "Çok faktörlü doğrulama etkinleştirildi.")
                return redirect("accounts:otp_setup")
            form.add_error(None, "Doğrulama kodu hatalı veya süresi dolmuş.")

    context = {
        "confirmed_device": confirmed_device,
        "pending_device": pending_device,
        "provisioning_uri": getattr(pending_device, "config_url", None),
        "secret_key": getattr(pending_device, "key", None),
        "form": form,
    }
    return render(request, "accounts/otp_setup.html", context)


@login_required
def otp_disable(request):
    confirmed_devices = list(devices_for_user(request.user, confirmed=True))
    if not confirmed_devices:
        messages.info(request, "Aktif MFA cihazınız bulunmuyor.")
        return redirect("accounts:otp_setup")

    if request.method == "POST":
        for device in confirmed_devices:
            audit_logger.log_security_event(
                action="auth.mfa.deactivated",
                actor=request.user,
                request=request,
                resource=f"TOTPDevice:{device.pk}",
                metadata={"device_name": device.name},
            )
            device.delete()
        messages.success(request, "Çok faktörlü doğrulama devre dışı bırakıldı.")
        return redirect("accounts:otp_setup")

    return render(request, "accounts/otp_disable.html", {"device_count": len(confirmed_devices)})

