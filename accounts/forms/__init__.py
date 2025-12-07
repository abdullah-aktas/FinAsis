from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from accounts.models import CustomUser, UserType, Subscription, SubscriptionType
from accounting.models import Company
from django.db import transaction
import random
import re


class RegisterForm(UserCreationForm):
    """Genişletilmiş kayıt formu.

    Özellikler:
      - Var olan şirket seçimi veya yeni şirket oluşturma
      - Kullanıcı tipi seçimi (opsiyonel)
      - Otomatik varsayılan abonelik atama
    """

    company = forms.ModelChoiceField(
        queryset=Company.objects.all(), required=False, label="Mevcut Şirket"
    )
    new_company_name = forms.CharField(
        max_length=255, required=False, label="Yeni Şirket Adı"
    )
    new_company_tax_number = forms.CharField(
        max_length=10, required=False, label="Yeni Şirket Vergi No (10 hane)"
    )
    user_type = forms.ModelChoiceField(
        queryset=UserType.objects.all(), required=False, label="Kullanıcı Tipi"
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "company",
            "new_company_name",
            "new_company_tax_number",
            "user_type",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email") or self.data.get("email")
        if not email:
            return email
        # Format validation
        try:
            validate_email(email)
        except Exception:
            raise ValidationError("Geçersiz e-posta adresi.")
        # Disposable / geçici e-posta engelleme
        try:
            domain = email.split("@", 1)[1].lower().strip()
        except Exception:
            raise ValidationError("Geçersiz e-posta adresi.")
        blocked_domains = {
            "tempmail.com",
            "throwaway.email",
            "10minutemail.com",
            "guerrillamail.com",
            "mailinator.com",
            "trashmail.com",
            "yopmail.com",
            "temp-mail.org",
            "getnada.com",
            "dispostable.com",
        }
        blocked_keywords = (
            "tempmail",
            "throwaway",
            "mailinator",
            "guerrilla",
            "10minutemail",
            "yopmail",
            "trashmail",
            "temp-mail",
            "getnada",
            "dispostable",
        )
        if domain in blocked_domains or any(kw in domain for kw in blocked_keywords):
            raise ValidationError("Geçici e-posta alan adları kabul edilmez.")
        return email

    def clean(self):
        cleaned = super().clean()
        # Şifre güçlülük kontrolü (temel kurallar)
        pw = cleaned.get("password1") or self.data.get("password")
        if pw is not None:
            pw_str = str(pw)
            if not pw_str.strip():
                self.add_error("password1", "Şifre boş olamaz.")
            elif len(pw_str) < 8:
                self.add_error("password1", "Şifre en az 8 karakter olmalıdır.")
            elif pw_str.lower() in {
                "password",
                "qwerty",
                "letmein",
                "12345678",
                "123456789",
            }:
                self.add_error(
                    "password1", "Şifre çok yaygın, lütfen daha güçlü bir şifre seçin."
                )
            elif pw_str.isdigit():
                self.add_error("password1", "Şifre sadece rakamlardan oluşamaz.")
            elif pw_str.isalpha():
                self.add_error("password1", "Şifre sadece harflerden oluşamaz.")
            else:
                # En az bir harf ve bir rakam
                has_letter = bool(re.search(r"[A-Za-z]", pw_str))
                has_digit = bool(re.search(r"\d", pw_str))
                if not (has_letter and has_digit):
                    self.add_error(
                        "password1", "Şifre en az bir harf ve bir rakam içermelidir."
                    )
        company = cleaned.get("company")
        new_company_name = cleaned.get("new_company_name")
        new_company_tax_number = cleaned.get("new_company_tax_number")
        if company and (new_company_name or new_company_tax_number):
            self.add_error(
                "new_company_name",
                "Hem mevcut şirket hem yeni şirket alanı doldurulamaz.",
            )
        if new_company_name and not new_company_tax_number:
            self.add_error(
                "new_company_tax_number", "Yeni şirket için vergi numarası zorunlu."
            )
        if new_company_tax_number and len(new_company_tax_number) != 10:
            self.add_error(
                "new_company_tax_number", "Vergi numarası 10 haneli olmalıdır."
            )
        # Vergi no mevcut bir şirkete aitse, otomatik mevcut şirkete bağla
        if new_company_tax_number and len(new_company_tax_number) == 10 and not company:
            existing = Company.objects.filter(tax_number=new_company_tax_number).first()
            if existing:
                cleaned["company"] = existing
                cleaned["new_company_name"] = ""
        return cleaned

    def _generate_dummy_tax_number(self):
        return "".join(str(random.randint(0, 9)) for _ in range(10))

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        cleaned = self.cleaned_data
        company = cleaned.get("company")
        new_company_name = cleaned.get("new_company_name")
        new_company_tax_number = cleaned.get("new_company_tax_number")
        user_type = cleaned.get("user_type")

        # Yeni şirket oluşturma (mevcutsa kullan)
        if not company and new_company_name:
            tax_no = new_company_tax_number or self._generate_dummy_tax_number()
            company, _ = Company.objects.get_or_create(
                tax_number=tax_no,
                defaults={"name": new_company_name},
            )
        user.company = company
        if user_type:
            user.user_type = user_type
        if commit:
            user.save()
            # Varsayılan kullanıcı tipi aboneliği
            if (
                user_type
                and user_type.default_subscription
                and not hasattr(user, "subscription")
            ):
                Subscription.objects.create(
                    user=user, subscription_type=user_type.default_subscription
                )
        return user


class OTPVerifyForm(forms.Form):
    token = forms.CharField(
        label="Doğrulama Kodu",
        max_length=6,
        min_length=4,
        widget=forms.TextInput(
            attrs={"autocomplete": "one-time-code", "class": "form-control"}
        ),
    )


class OTPSetupForm(forms.Form):
    token = forms.CharField(
        label="Authenticator Kodunuz",
        max_length=6,
        min_length=4,
        widget=forms.TextInput(
            attrs={"autocomplete": "one-time-code", "class": "form-control"}
        ),
        help_text="Authenticator uygulamasındaki 6 haneli kodu girin.",
    )
