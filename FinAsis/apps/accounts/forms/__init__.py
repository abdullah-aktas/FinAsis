from django.contrib.auth.forms import UserCreationForm
from FinAsis.apps.accounts.models import CustomUser, UserType
from FinAsis.apps.accounting.models import Company
from django import forms

class RegisterForm(UserCreationForm):
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all(), label='Kullanıcı Tipi')
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False, label='Şirket (varsa)')
    new_company_name = forms.CharField(max_length=255, required=False, label='Yeni Şirket Adı')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'company', 'new_company_name', 'password1', 'password2') 