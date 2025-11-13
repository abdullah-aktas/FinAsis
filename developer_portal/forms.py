from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from developer_portal.models import DeveloperAPIKey
from developer_portal.services import available_event_choices

RATE_PLAN_CHOICES = [
    ("freemium", _("Freemium · 120 istek/gün")),
    ("standard", _("Standard · 1000 istek/saat")),
    ("professional", _("Professional · 5000 istek/saat")),
    ("enterprise", _("Enterprise · 20000 istek/saat")),
]


class APIKeyCreateForm(forms.ModelForm):
    allowed_ips = forms.CharField(
        required=False,
        help_text=_("Virgülle ayrılmış IP adresleri. Boş bırakılırsa tüm IP'ler için geçerlidir."),
    )
    expires_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text=_("Opsiyonel. Anahtar belirli bir tarihte devre dışı bırakılır."),
    )
    rate_limit_plan = forms.ChoiceField(
        choices=RATE_PLAN_CHOICES,
        initial="standard",
        label=_("Hız Limiti Planı"),
    )

    class Meta:
        model = DeveloperAPIKey
        fields = ["name", "description", "rate_limit_plan", "allowed_ips", "expires_at"]

    def clean_allowed_ips(self):
        raw = self.cleaned_data.get("allowed_ips", "")
        if not raw:
            return []
        ips = [value.strip() for value in raw.split(",") if value.strip()]
        return ips


class APIKeyRotateForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label=_("Bu anahtarı döndürmek istediğimi onaylıyorum."),
    )


class APIKeyRevokeForm(forms.Form):
    reason = forms.CharField(
        required=False,
        label=_("Neden"),
        widget=forms.Textarea(attrs={"rows": 2}),
    )


class WebhookTestForm(forms.Form):
    event_type = forms.ChoiceField(
        choices=(),
        label=_("Olay Türü"),
    )
    target_url = forms.URLField(
        label=_("Hedef URL"),
        help_text=_("Webhook isteğinin gönderileceği HTTPS adresi."),
    )
    signature_secret = forms.CharField(
        required=False,
        label=_("İmza Gizli Anahtarı"),
        help_text=_("FinAsis tarafından gönderilecek HMAC imzası için opsiyonel gizli anahtar."),
        widget=forms.PasswordInput(render_value=True),
    )
    custom_headers = forms.CharField(
        required=False,
        label=_("Ek HTTP Başlıkları"),
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text=_('JSON formatında başlıklar. Örn: {"X-Test": "1"}'),
    )
    payload_override = forms.CharField(
        required=False,
        label=_("Özel Payload"),
        widget=forms.Textarea(attrs={"rows": 6}),
        help_text=_("Varsayılan örneği değiştirmek için geçerli JSON girin."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event_type"].choices = list(available_event_choices())
        for name, field in self.fields.items():
            current_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{current_classes} form-control".strip()
        self.fields["event_type"].widget.attrs["class"] = (
            f'{self.fields["event_type"].widget.attrs.get("class", "")} form-select'
        ).strip()
        for name in ("custom_headers", "payload_override"):
            widget = self.fields[name].widget
            widget.attrs["class"] = f'{widget.attrs.get("class", "")} font-monospace'.strip()

