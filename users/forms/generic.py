# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from ..models import UserProfile

class UserRegistrationForm(UserCreationForm):
    """
    Kullanıcı kayıt formu.
    """
    email = forms.EmailField(
        label=_('E-posta'),
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserLoginForm(AuthenticationForm):
    """
    Kullanıcı giriş formu.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserProfileForm(forms.ModelForm):
    """
    Kullanıcı profil formu.
    """
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'birth_date', 'phone_number', 'address')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserUpdateForm(forms.ModelForm):
    """
    Kullanıcı güncelleme formu.
    """
    email = forms.EmailField(
        label=_('E-posta'),
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        } 