# -*- coding: utf-8 -*-
"""
Mali Müşavirlik Modülü Formları
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from datetime import date

from .models_marketplace import ConsultationBooking, ConsultantService


class ConsultationBookingForm(forms.ModelForm):
    """Randevu oluşturma formu"""

    class Meta:
        model = ConsultationBooking
        fields = [
            "service",
            "meeting_type",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "subject",
            "description",
            "meeting_address",
        ]
        widgets = {
            "scheduled_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "scheduled_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "duration_minutes": forms.NumberInput(
                attrs={"class": "form-control", "min": 15, "step": 15}
            ),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "meeting_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "service": forms.Select(attrs={"class": "form-select"}),
            "meeting_type": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, consultant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.consultant = consultant

        if consultant:
            # Sadece bu mali müşavirin aktif hizmetlerini göster
            self.fields["service"].queryset = ConsultantService.objects.filter(
                consultant=consultant, is_active=True
            )
            self.fields["service"].empty_label = _("Hizmet seçin")

        # Varsayılan değerler
        if not self.instance.pk:
            self.fields["duration_minutes"].initial = 60
            self.fields["meeting_type"].initial = "online"

    def clean_scheduled_date(self):
        """Tarih kontrolü"""
        scheduled_date = self.cleaned_data.get("scheduled_date")
        if scheduled_date:
            if scheduled_date < date.today():
                raise forms.ValidationError(_("Geçmiş bir tarih seçemezsiniz."))
        return scheduled_date

    def clean(self):
        """Form genel validasyonu"""
        cleaned_data = super().clean()
        meeting_type = cleaned_data.get("meeting_type")
        meeting_address = cleaned_data.get("meeting_address")

        # Yüz yüze görüşme için adres zorunlu
        if meeting_type == "in_person" and not meeting_address:
            raise forms.ValidationError(
                {"meeting_address": _("Yüz yüze görüşme için adres gereklidir.")}
            )

        return cleaned_data
