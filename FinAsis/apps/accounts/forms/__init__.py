from django.contrib.auth.forms import UserCreationForm
from FinAsis.apps.accounts.models import CustomUser, UserType
from FinAsis.apps.accounting.models import Company
from django import forms
from django.contrib.auth.models import Group

class RegisterForm(UserCreationForm):
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all(), label='Kullanıcı Tipi')
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False, label='Şirket (varsa)')
    new_company_name = forms.CharField(max_length=255, required=False, label='Yeni Şirket Adı')
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, label='Yetki Grubu')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'company', 'new_company_name', 'groups', 'password1', 'password2') 