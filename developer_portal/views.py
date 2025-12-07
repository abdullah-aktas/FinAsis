from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View

import json

from developer_portal import selectors
from developer_portal.forms import (
    APIKeyCreateForm,
    APIKeyRevokeForm,
    APIKeyRotateForm,
    WebhookTestForm,
)
from developer_portal.services import key_manager, usage_service, webhook_tester
from common.services import audit_logger


class DeveloperPortalPermissionMixin(PermissionRequiredMixin):
    permission_required = "developer_portal.manage_keys"

    def has_permission(self):
        # Superuser veya explicit izin verilmiş kullanıcılar portala erişir.
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or super().has_permission()


class DeveloperPortalDashboardView(
    LoginRequiredMixin, DeveloperPortalPermissionMixin, TemplateView
):
    template_name = "developer_portal/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        keys = selectors.user_api_keys(self.request.user)[:5]
        context["api_keys"] = keys
        context["usage_summaries"] = {
            key.id: usage_service.usage_summary(key) for key in keys
        }
        return context


class APIKeyListView(LoginRequiredMixin, DeveloperPortalPermissionMixin, TemplateView):
    template_name = "developer_portal/api_key_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["api_keys"] = selectors.user_api_keys(self.request.user)
        context["create_form"] = APIKeyCreateForm()
        return context

    def post(self, request, *args, **kwargs):
        form = APIKeyCreateForm(request.POST)
        if form.is_valid():
            organization = getattr(self.request.user, "company", None)
            if organization is None:
                messages.error(
                    request,
                    _("Bir şirkete bağlı olmadan API anahtarı oluşturamazsınız."),
                )
                return redirect("developer_portal:api_keys")

            key, raw_secret = key_manager.create_api_key(
                owner=request.user,
                organization=organization,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                rate_limit_plan=form.cleaned_data["rate_limit_plan"],
                allowed_ips=form.cleaned_data["allowed_ips"],
                expires_at=form.cleaned_data["expires_at"],
                actor=request.user,
            )
            audit_logger.log_security_event(
                action="developer_portal.api_key.create",
                actor=request.user,
                request=request,
                resource=f"DeveloperAPIKey:{key.pk}",
                metadata={
                    "plan": key.rate_limit_plan,
                    "allowed_ips": key.allowed_ips,
                },
            )
            request.session["last_created_api_key"] = raw_secret
            messages.success(
                request,
                _("API anahtarı oluşturuldu. Anahtarı güvenli bir yerde saklayın."),
            )
            return redirect("developer_portal:api_key_detail", pk=key.pk)
        messages.error(request, _("Form verileri doğrulanamadı."))
        return redirect("developer_portal:api_keys")


class APIKeyDetailView(
    LoginRequiredMixin, DeveloperPortalPermissionMixin, TemplateView
):
    template_name = "developer_portal/api_key_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_key = get_object_or_404(
            selectors.user_api_keys(self.request.user), pk=self.kwargs["pk"]
        )
        context["api_key"] = api_key
        context["usage_logs"] = api_key.usage_logs.all()[:25]
        context["usage_summary"] = usage_service.usage_summary(api_key, hours=24)
        context["rotate_form"] = APIKeyRotateForm()
        context["revoke_form"] = APIKeyRevokeForm()
        context["raw_secret"] = self.request.session.pop("last_created_api_key", None)
        return context


class APIKeyRotateView(LoginRequiredMixin, DeveloperPortalPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        api_key = get_object_or_404(
            selectors.user_api_keys(request.user), pk=kwargs["pk"]
        )
        form = APIKeyRotateForm(request.POST)
        if not form.is_valid():
            messages.error(request, _("Anahtar döndürme onayı gerekli."))
            return redirect("developer_portal:api_key_detail", pk=api_key.pk)

        new_key, raw_secret = key_manager.rotate_api_key(api_key, actor=request.user)
        audit_logger.log_security_event(
            action="developer_portal.api_key.rotate",
            actor=request.user,
            request=request,
            resource=f"DeveloperAPIKey:{api_key.pk}",
            metadata={"new_key": str(new_key.pk)},
        )
        request.session["last_created_api_key"] = raw_secret
        messages.success(
            request,
            _("Anahtar döndürüldü. Yeni anahtar bilgisi ekranda gösteriliyor."),
        )
        return redirect("developer_portal:api_key_detail", pk=new_key.pk)


class APIKeyRevokeView(LoginRequiredMixin, DeveloperPortalPermissionMixin, View):
    def post(self, request, *args, **kwargs):
        api_key = get_object_or_404(
            selectors.user_api_keys(request.user), pk=kwargs["pk"]
        )
        form = APIKeyRevokeForm(request.POST)
        if form.is_valid():
            key_manager.revoke_api_key(
                api_key,
                actor=request.user,
                reason=form.cleaned_data.get("reason"),
            )
            audit_logger.log_security_event(
                action="developer_portal.api_key.revoke",
                actor=request.user,
                request=request,
                resource=f"DeveloperAPIKey:{api_key.pk}",
                metadata={"reason": form.cleaned_data.get("reason")},
            )
            messages.success(request, _("Anahtar devre dışı bırakıldı."))
        else:
            messages.error(request, _("İşlem başarısız oldu."))
        return redirect("developer_portal:api_keys")


class DeveloperDocsView(
    LoginRequiredMixin, DeveloperPortalPermissionMixin, TemplateView
):
    template_name = "developer_portal/docs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        swagger_url = reverse("accounting:api_docs")
        redoc_url = reverse("accounting:api_redoc")
        context.update(
            {
                "swagger_url": swagger_url,
                "redoc_url": redoc_url,
                "code_samples": [
                    {
                        "language": "Python",
                        "icon": "bi bi-filetype-py",
                        "description": _(
                            "Requests ile erişim, hata yönetimi ve yeniden deneme."
                        ),
                        "code": (
                            "import requests\n"
                            'API_KEY = "{{ API_KEY }}"\n'
                            'BASE_URL = "https://api.finasis.com.tr/v1"\n\n'
                            "response = requests.get(\n"
                            '    f"{BASE_URL}/accounting/invoices/",\n'
                            '    headers={"X-API-Key": API_KEY},\n'
                            "    timeout=10,\n"
                            ")\n"
                            "response.raise_for_status()\n"
                            "invoices = response.json()\n"
                        ),
                    },
                    {
                        "language": "JavaScript",
                        "icon": "bi bi-filetype-js",
                        "description": _("fetch API ile istemci tarafı örnek çağrı."),
                        "code": (
                            'const API_KEY = "{{ API_KEY }}";\n'
                            'const BASE_URL = "https://api.finasis.com.tr/v1";\n\n'
                            "async function listInvoices() {\n"
                            "  const response = await fetch(`${BASE_URL}/accounting/invoices/`, {\n"
                            "    headers: {\n"
                            "      'X-API-Key': API_KEY,\n"
                            "      'Accept': 'application/json'\n"
                            "    }\n"
                            "  });\n"
                            "  if (!response.ok) {\n"
                            "    throw new Error(`HTTP ${response.status}`);\n"
                            "  }\n"
                            "  return await response.json();\n"
                            "}\n"
                        ),
                    },
                    {
                        "language": "Go",
                        "icon": "bi bi-filetype-go",
                        "description": _("Go http.Client ile API çağrısı."),
                        "code": (
                            "package main\n\n"
                            "import (\n"
                            '    "fmt"\n'
                            '    "net/http"\n'
                            '    "time"\n'
                            ")\n\n"
                            "func main() {\n"
                            "    client := &http.Client{Timeout: 10 * time.Second}\n"
                            '    req, _ := http.NewRequest("GET", "https://api.finasis.com.tr/v1/accounting/invoices/", nil)\n'
                            '    req.Header.Set("X-API-Key", "{{ API_KEY }}")\n'
                            '    req.Header.Set("Accept", "application/json")\n\n'
                            "    res, err := client.Do(req)\n"
                            "    if err != nil {\n"
                            "        panic(err)\n"
                            "    }\n"
                            "    defer res.Body.Close()\n"
                            "    fmt.Println(res.Status)\n"
                            "}\n"
                        ),
                    },
                ],
                "quickstart_steps": [
                    {
                        "title": _("API Anahtarı Oluştur"),
                        "description": _(
                            "Developer Portal > API Anahtarları sekmesinden yeni anahtar oluşturun ve güvenle saklayın."
                        ),
                        "icon": "bi-key",
                    },
                    {
                        "title": _("Yetkilendirme & Rate Limit"),
                        "description": _(
                            "Her isteğe `X-API-Key` başlığını ekleyin. Planınıza göre rate limit değerlerini takip edin."
                        ),
                        "icon": "bi-shield-lock",
                    },
                    {
                        "title": _("Webhook Entegrasyonu"),
                        "description": _(
                            "Webhook Konsolu ile entegrasyonunuzu test edin, HMAC imzasını doğrulayın ve logları izleyin."
                        ),
                        "icon": "bi-diagram-3",
                    },
                ],
            }
        )
        return context


class WebhookConsoleView(
    LoginRequiredMixin, DeveloperPortalPermissionMixin, TemplateView
):
    template_name = "developer_portal/webhook_console.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form") or WebhookTestForm()
        context["event_definitions"] = [
            {
                "key": definition.key,
                "title": definition.title,
                "summary": definition.summary,
                "payload_json": json.dumps(
                    definition.sample_payload,
                    ensure_ascii=False,
                    indent=2,
                ),
            }
            for definition in webhook_tester.EVENT_DEFINITIONS
        ]
        context["webhook_logs"] = selectors.user_webhook_logs(self.request.user)[:20]
        return context

    def post(self, request, *args, **kwargs):
        form = WebhookTestForm(request.POST)
        if not form.is_valid():
            messages.error(
                request, _("Form doğrulanamadı. Lütfen alanları kontrol edin.")
            )
            return self.render_to_response(self.get_context_data(form=form))

        try:
            log_entry = webhook_tester.dispatch_webhook(
                actor=request.user,
                target_url=form.cleaned_data["target_url"],
                event_key=form.cleaned_data["event_type"],
                signature_secret=form.cleaned_data.get("signature_secret") or None,
                custom_headers_raw=form.cleaned_data.get("custom_headers") or None,
                payload_override=form.cleaned_data.get("payload_override") or None,
            )
        except ValueError as exc:
            messages.error(request, str(exc))
            return self.render_to_response(self.get_context_data(form=form))

        if log_entry.error:
            messages.warning(
                request,
                _("Webhook isteği hata ile sonuçlandı: %(error)s")
                % {"error": log_entry.error},
            )
        else:
            messages.success(
                request,
                _("Webhook isteği gönderildi. HTTP %(status)s yanıtı alındı.")
                % {"status": log_entry.response_status},
            )

        return redirect("developer_portal:webhook_console")
