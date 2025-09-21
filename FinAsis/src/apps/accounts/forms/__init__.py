from django import forms
from django.contrib.auth.forms import UserCreationForm
from src.apps.accounts.models import CustomUser, UserType, Subscription, SubscriptionType
from src.apps.accounting.models import Company
from django.db import transaction
import random


class RegisterForm(UserCreationForm):
    """Genişletilmiş kayıt formu.

    Özellikler:
      - Var olan şirket seçimi veya yeni şirket oluşturma
      - Kullanıcı tipi seçimi (opsiyonel)
      - Otomatik varsayılan abonelik atama
    """

    company = forms.ModelChoiceField(
        queryset=Company.objects.all(), required=False, label='Mevcut Şirket'
    )
    new_company_name = forms.CharField(
        max_length=255, required=False, label='Yeni Şirket Adı'
    )
    new_company_tax_number = forms.CharField(
        max_length=10, required=False, label='Yeni Şirket Vergi No (10 hane)'
    )
    user_type = forms.ModelChoiceField(
        queryset=UserType.objects.all(), required=False, label='Kullanıcı Tipi'
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'password1', 'password2',
            'company', 'new_company_name', 'new_company_tax_number', 'user_type'
        )

    def clean(self):
        cleaned = super().clean()
        company = cleaned.get('company')
        new_company_name = cleaned.get('new_company_name')
        new_company_tax_number = cleaned.get('new_company_tax_number')
        if company and (new_company_name or new_company_tax_number):
            self.add_error('new_company_name', 'Hem mevcut şirket hem yeni şirket alanı doldurulamaz.')
        if new_company_name and not new_company_tax_number:
            self.add_error('new_company_tax_number', 'Yeni şirket için vergi numarası zorunlu.')
        if new_company_tax_number and len(new_company_tax_number) != 10:
            self.add_error('new_company_tax_number', 'Vergi numarası 10 haneli olmalıdır.')
        # Vergi no mevcut bir şirkete aitse, otomatik mevcut şirkete bağla
        if new_company_tax_number and len(new_company_tax_number) == 10 and not company:
            existing = Company.objects.filter(tax_number=new_company_tax_number).first()
            if existing:
                cleaned['company'] = existing
                cleaned['new_company_name'] = ''
        return cleaned
        return cleaned

    def _generate_dummy_tax_number(self):
        return ''.join(str(random.randint(0, 9)) for _ in range(10))

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        cleaned = self.cleaned_data
        company = cleaned.get('company')
        new_company_name = cleaned.get('new_company_name')
        new_company_tax_number = cleaned.get('new_company_tax_number')
        user_type = cleaned.get('user_type')

        # Yeni şirket oluşturma (mevcutsa kullan)
        if not company and new_company_name:
            tax_no = new_company_tax_number or self._generate_dummy_tax_number()
            company, _ = Company.objects.get_or_create(
                tax_number=tax_no,
                defaults={'name': new_company_name},
            )
        user.company = company
        if user_type:
            user.user_type = user_type
        if commit:
            user.save()
            # Varsayılan kullanıcı tipi aboneliği
            if user_type and user_type.default_subscription and not hasattr(user, 'subscription'):
                Subscription.objects.create(
                    user=user,
                    subscription_type=user_type.default_subscription
                )
        return user
