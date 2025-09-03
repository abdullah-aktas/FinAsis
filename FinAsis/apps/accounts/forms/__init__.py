from django.contrib.auth.forms import UserCreationForm
from FinAsis.apps.accounts.models import CustomUser, UserType
from FinAsis.apps.accounting.models import Company
from django import forms
from django.contrib.auth.models import Group

class RegisterForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')