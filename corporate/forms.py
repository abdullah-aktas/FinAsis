from __future__ import annotations

from typing import Iterable

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import PartnerApplication, PartnerCategory


PARTNER_INTEGRATION_CHOICES: tuple[tuple[str, str], ...] = (
    ("erp", _("ERP / Muhasebe Entegrasyonu")),
    ("crm", _("CRM ve Satış Otomasyonu")),
    ("payments", _("Ödeme & Tahsilat Çözümleri")),
    ("compliance", _("Uyumluluk & RegTech")),
    ("education", _("Eğitim / LMS")),
    ("analytics", _("Analitik & BI")),
)


class PartnerApplicationForm(forms.ModelForm):
    """Partner ekosistemi başvurusu için halka açık form."""

    categories = forms.ModelMultipleChoiceField(
        queryset=PartnerCategory.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label=_("İlgilendiğiniz kategori(ler)"),
    )
    integration_focus = forms.MultipleChoiceField(
        choices=PARTNER_INTEGRATION_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
        label=_("Entegrasyon odak alanları"),
    )
    gdpr_consent = forms.BooleanField(
        label=_(
            "KVKK ve gizlilik politikasını okudum, başvuru bilgilerimin saklanmasına izin veriyorum."
        ),
        required=True,
    )

    class Meta:
        model = PartnerApplication
        fields = [
            "company_name",
            "brand_name",
            "website",
            "country",
            "city",
            "team_size",
            "contact_name",
            "contact_email",
            "contact_phone",
            "job_title",
            "primary_category",
            "categories",
            "integration_focus",
            "product_notes",
            "message",
            "go_live_timeline",
            "revenue_model",
            "sandbox_needs",
        ]
        widgets = {
            "product_notes": forms.Textarea(attrs={"rows": 3}),
            "message": forms.Textarea(attrs={"rows": 4}),
            "sandbox_needs": forms.Textarea(attrs={"rows": 3}),
            "go_live_timeline": forms.TextInput(
                attrs={"placeholder": _("Örn. 6-8 hafta")}
            ),
            "revenue_model": forms.TextInput(
                attrs={"placeholder": _("Örn. Abonelik + rev paylaşımı")}
            ),
        }
        labels = {
            "company_name": _("Şirket Adı"),
            "brand_name": _("Marka / Ürün Adı"),
            "team_size": _("Ekip Büyüklüğü"),
            "primary_category": _("Birincil kategori"),
            "product_notes": _("Ürün / entegrasyon özeti"),
            "message": _("İş birliği hedefiniz"),
            "sandbox_needs": _("Teknik gereksinimler / sandbox ihtiyaçları"),
        }
        help_texts = {
            "categories": _("Birden fazla kategori seçebilirsiniz."),
            "integration_focus": _(
                "FinAsis ile hangi alanlarda entegrasyon kurmak istediğinizi belirtin."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_categories = PartnerCategory.objects.filter(is_active=True).order_by(
            "priority", "name"
        )
        self.fields["categories"].queryset = active_categories
        self.fields["primary_category"].queryset = active_categories

        # Ön seçimleri ayarla
        if self.instance.pk:
            self.fields["categories"].initial = self.instance.categories.values_list(
                "pk", flat=True
            )
            self.fields["integration_focus"].initial = self.instance.integration_focus

    def clean_integration_focus(self) -> list[str]:
        data: Iterable[str] = self.cleaned_data.get("integration_focus") or []
        # unique and preserve order
        seen: set[str] = set()
        ordered: list[str] = []
        for item in data:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    def save(self, commit: bool = True) -> PartnerApplication:
        categories = self.cleaned_data.pop("categories", None)
        integrations = self.cleaned_data.pop("integration_focus", [])
        instance: PartnerApplication = super().save(commit=False)
        instance.integration_focus = integrations
        if commit:
            instance.save()
            if categories is not None:
                instance.categories.set(categories)
        else:
            self._pending_categories = categories
        return instance

    def save_m2m(self) -> None:
        super().save_m2m()
        categories = getattr(self, "_pending_categories", None)
        if categories is not None:
            self.instance.categories.set(categories)
