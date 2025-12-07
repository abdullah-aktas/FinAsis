from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import PartnerApplication


class PartnerApplicationForm(forms.ModelForm):
    consent_marketing = forms.BooleanField(
        label=_("FinAsis ekibinin benimle iletişime geçmesine izin veriyorum."),
        required=True,
    )

    class Meta:
        model = PartnerApplication
        fields = [
            "company_name",
            "partner_type",
            "integration_focus",
            "target_customer_segments",
            "regions",
            "contact_name",
            "contact_email",
            "contact_phone",
            "website_url",
            "sandbox_url",
            "compliance_notes",
            "go_to_market_plan",
            "additional_notes",
        ]
        widgets = {
            "integration_focus": forms.TextInput(
                attrs={
                    "placeholder": _("Örn. e-Fatura, KOBİ finans, eğitim içerikleri"),
                }
            ),
            "target_customer_segments": forms.TextInput(
                attrs={"placeholder": _("Örn. KOBİ, eğitim kurumları, fintech")}
            ),
            "regions": forms.TextInput(
                attrs={"placeholder": _("Örn. Türkiye, AB, MENA")}
            ),
            "compliance_notes": forms.Textarea(attrs={"rows": 3}),
            "go_to_market_plan": forms.Textarea(attrs={"rows": 3}),
            "additional_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_contact_email(self):
        email = self.cleaned_data["contact_email"]
        if email.endswith("@example.com"):
            raise forms.ValidationError(
                _("Lütfen geçerli bir şirket e-posta adresi girin.")
            )
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        control_fields = [
            "company_name",
            "integration_focus",
            "target_customer_segments",
            "regions",
            "contact_name",
            "contact_email",
            "contact_phone",
            "website_url",
            "sandbox_url",
            "compliance_notes",
            "go_to_market_plan",
            "additional_notes",
        ]
        for name in control_fields:
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("class", "form-control")

        if "partner_type" in self.fields:
            self.fields["partner_type"].widget.attrs.setdefault("class", "form-select")

        if "consent_marketing" in self.fields:
            self.fields["consent_marketing"].widget.attrs.setdefault(
                "class", "form-check-input"
            )
