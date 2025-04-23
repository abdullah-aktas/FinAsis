from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
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
    """Kullanıcı tercihleri formu"""
    class Meta:
        model = UserPreferences
        fields = ('language', 'timezone', 'theme', 'email_notifications', 
                 'push_notifications', 'sms_notifications')
        widgets = {
            'language': forms.Select(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserSettingsForm(forms.ModelForm):
    """Kullanıcı ayarları formu."""
    
    class Meta:
        model = UserSettings
        fields = ('email_notifications', 'push_notifications', 'dark_mode', 'newsletter_subscription')
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'newsletter_subscription': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """Özelleştirilmiş şifre değiştirme formu."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class TwoFactorSetupForm(forms.Form):
    """İki faktörlü doğrulama kurulum formu."""
    
    verification_code = forms.CharField(
        label=_('Doğrulama Kodu'),
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError(_('Geçerli bir doğrulama kodu giriniz.'))
        return code

class TwoFactorVerifyForm(forms.Form):
    """İki faktörlü kimlik doğrulama doğrulama formu"""
    code = forms.CharField(
        label=_('Doğrulama Kodu'),
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class EmailVerificationForm(forms.Form):
    """E-posta doğrulama formu"""
    email = forms.EmailField(
        label=_('E-posta'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

class PasswordResetForm(forms.Form):
    """Şifre sıfırlama formu"""
    email = forms.EmailField(
        label=_('E-posta'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

class PasswordResetConfirmForm(forms.Form):
    """Şifre sıfırlama onay formu"""
    new_password1 = forms.CharField(
        label=_('Yeni Şifre'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label=_('Yeni Şifre (Tekrar)'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class UserSearchForm(forms.Form):
    """Kullanıcı arama formu"""
    query = forms.CharField(
        label=_('Arama'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Kullanıcı adı veya e-posta')})
    )
    role = forms.ChoiceField(
        label=_('Rol'),
        required=False,
        choices=[('', _('Tümü'))] + User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        label=_('Aktif Kullanıcılar'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    ) 