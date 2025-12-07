# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü - Formlar

Bu modül, muhasebe modellerinin formlarını içerir.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from typing import cast

from .models import (
    AccountType,
    Account,
    VoucherType,
    Voucher,
    VoucherLine,
    Currency,
    FinancialReport,
)


class AccountTypeForm(forms.ModelForm):
    """Hesap türü formu"""

    class Meta:
        model = AccountType
        fields = ["code", "name", "description", "is_active"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class AccountForm(forms.ModelForm):
    """Hesap formu"""

    class Meta:
        model = Account
        fields = [
            "code",
            "name",
            "type",
            "parent",
            "description",
            "is_bank_account",
            "is_cash_account",
            "is_tax_account",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        if self.company:
            # Kullanıcının şirketine ait hesapları filtrele (üst hesap seçimi için)
            parent_field = cast(forms.ModelChoiceField, self.fields["parent"])
            parent_field.queryset = Account.objects.filter(company=self.company)


class VoucherTypeForm(forms.ModelForm):
    """Fiş türü formu"""

    class Meta:
        model = VoucherType
        fields = ["code", "name", "description", "prefix"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "prefix": forms.TextInput(attrs={"class": "form-control"}),
        }


class VoucherForm(forms.ModelForm):
    """Muhasebe fişi formu"""

    class Meta:
        model = Voucher
        fields = [
            "fiscal_year",
            "type",
            "number",
            "date",
            "description",
            "reference",
            "currency",
            "exchange_rate",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "number": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "exchange_rate": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.000001"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        if self.company:
            # Kullanıcının şirketine ait mali yılları filtrele
            fy_field = cast(forms.ModelChoiceField, self.fields["fiscal_year"])
            fy_field.queryset = fy_field.queryset.filter(company=self.company)

        # Aktif para birimlerini filtrele
        if "currency" in self.fields:
            currency_field = cast(forms.ModelChoiceField, self.fields["currency"])
            currency_field.queryset = Currency.objects.filter(is_active=True)

            # Varsayılan para birimi seçili gelsin
            if not self.instance.pk:
                try:
                    default_currency = Currency.objects.get(is_default=True)
                    currency_field.initial = default_currency
                except Currency.DoesNotExist:
                    pass


class VoucherLineForm(forms.ModelForm):
    """Muhasebe fişi satırı formu"""

    class Meta:
        model = VoucherLine
        fields = [
            "account",
            "description",
            "debit_amount",
            "credit_amount",
            "foreign_debit_amount",
            "foreign_credit_amount",
        ]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "debit_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "credit_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "foreign_debit_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "foreign_credit_amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        debit_amount = cleaned_data.get("debit_amount")
        credit_amount = cleaned_data.get("credit_amount")
        foreign_debit_amount = cleaned_data.get("foreign_debit_amount")
        foreign_credit_amount = cleaned_data.get("foreign_credit_amount")

        # Borç ve alacak kontrolü
        if debit_amount and credit_amount:
            if debit_amount > 0 and credit_amount > 0:
                raise forms.ValidationError(_("Borç ve alacak aynı anda dolu olamaz."))

        # Dövizli borç ve alacak kontrolü
        if foreign_debit_amount and foreign_credit_amount:
            if foreign_debit_amount > 0 and foreign_credit_amount > 0:
                raise forms.ValidationError(
                    _("Dövizli borç ve alacak aynı anda dolu olamaz.")
                )

        return cleaned_data


# Django formset fabrikası
VoucherLineFormSet = forms.inlineformset_factory(
    Voucher,
    VoucherLine,
    form=VoucherLineForm,
    extra=5,
    can_delete=True,
)


class CurrencyForm(forms.ModelForm):
    """Para birimi formu"""

    class Meta:
        model = Currency
        fields = ["code", "name", "symbol", "is_default", "is_active"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "symbol": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_is_default(self):
        is_default = self.cleaned_data.get("is_default")

        # Eğer bu para birimi varsayılan olarak işaretlendiyse, diğer varsayılan para birimlerini kontrol et
        if is_default and not self.instance.pk:
            if Currency.objects.filter(is_default=True).exists():
                raise forms.ValidationError(
                    _(
                        "Zaten varsayılan bir para birimi mevcut. Lütfen önce mevcut varsayılan para birimini değiştirin."
                    )
                )

        return is_default


class FinancialReportForm(forms.ModelForm):
    """Finansal rapor formu"""

    class Meta:
        model = FinancialReport
        fields = ["company", "name", "type", "start_date", "end_date", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

        if self.company:
            self.fields["company"].initial = self.company
            self.fields["company"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Başlangıç tarihi bitiş tarihinden sonra olamaz
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(
                _("Başlangıç tarihi bitiş tarihinden sonra olamaz.")
            )

        return cleaned_data
