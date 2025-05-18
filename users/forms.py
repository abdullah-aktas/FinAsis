# -*- coding: utf-8 -*-
"""
Users Modülü - Form Sınıfları
--------------------------
Bu dosya, Users modülünün form sınıflarını içerir.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, PasswordChangeForm as AuthPasswordChangeForm,
    PasswordResetForm as AuthPasswordResetForm, SetPasswordForm
)
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, UserPreferences, TwoFactorAuth, User, UserSettings

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    """Kullanıcı kayıt formu"""
    email = forms.EmailField(
        label=_('E-posta'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Telefon numarası geçerli bir formatta olmalıdır.')
    )
    phone = forms.CharField(
        label=_('Telefon'),
        validators=[phone_regex],
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Bu e-posta adresi zaten kullanılıyor.'))
        return email

class UserProfileForm(forms.ModelForm):
    """Kullanıcı profil formu"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'profile_picture', 
                 'bio', 'birth_date', 'address', 'city', 'country')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserPreferencesForm(forms.ModelForm):
    """Kullanıcı tercih formu"""
    class Meta:
        model = UserPreferences
        fields = ('language', 'timezone', 'notification_preferences')

class UserSettingsForm(forms.ModelForm):
    """Kullanıcı ayarları formu"""
    class Meta:
        model = UserSettings
        fields = ('theme', 'email_notifications', 'sms_notifications', 'privacy_settings')

class CustomPasswordChangeForm(AuthPasswordChangeForm):
    """Özelleştirilmiş şifre değiştirme formu."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class TwoFactorSetupForm(forms.ModelForm):
    """İki faktörlü doğrulama kurulum formu"""
    class Meta:
        model = TwoFactorAuth
        fields = ('phone_number',)

class TwoFactorVerifyForm(forms.Form):
    """İki faktörlü doğrulama kodu formu"""
    code = forms.CharField(max_length=6, min_length=6)

class EmailVerificationForm(forms.Form):
    """E-posta doğrulama formu"""
    email = forms.EmailField()

class UserSearchForm(forms.Form):
    """Kullanıcı arama formu"""
    query = forms.CharField(required=False, label=_("Arama"))
    is_active = forms.BooleanField(required=False, label=_("Aktif Kullanıcılar"))

class PasswordChangeForm(AuthPasswordChangeForm):
    """Şifre değiştirme formu"""
    pass

class PasswordResetForm(AuthPasswordResetForm):
    """Şifre sıfırlama formu"""
    pass

class PasswordResetConfirmForm(SetPasswordForm):
    """Şifre sıfırlama onay formu"""
    new_password1 = forms.CharField(
        label=_('Yeni Şifre'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label=_('Yeni Şifre (Tekrar)'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

"""
Kullanıcı yönetimi ile ilgili formlar burada tanımlanır.
"""

# class UserForm(forms.Form):
#     """Kullanıcı formu açıklaması."""
#     username = forms.CharField(max_length=150) 