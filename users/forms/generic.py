from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile

class UserRegistrationForm(UserCreationForm):
    """Kullanıcı kayıt formu"""
    
    email = forms.EmailField(
        label=_('E-posta'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('E-posta adresiniz')}),
        help_text=_('Geçerli bir e-posta adresi girin.')
    )
    username = forms.CharField(
        label=_('Kullanıcı Adı'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Kullanıcı adınız')}),
        help_text=_('Kullanıcı adınızı yazın.')
    )
    first_name = forms.CharField(
        label=_('Ad'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Adınız')}),
    )
    last_name = forms.CharField(
        label=_('Soyad'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Soyadınız')}),
    )
    password1 = forms.CharField(
        label=_('Şifre'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Şifreniz')}),
        help_text=_('En az 8 karakter uzunluğunda, rakam ve harf içeren bir şifre belirleyin.')
    )
    password2 = forms.CharField(
        label=_('Şifre Onayı'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Şifrenizi tekrar yazın')}),
        help_text=_('Doğrulama için şifrenizi tekrar girin.')
    )
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Bu e-posta adresi zaten kullanılıyor.'))
        return email

class UserLoginForm(forms.Form):
    """Kullanıcı giriş formu"""
    
    email = forms.EmailField(
        label=_('E-posta'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('E-posta adresiniz')})
    )
    password = forms.CharField(
        label=_('Şifre'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Şifreniz')})
    )
    remember_me = forms.BooleanField(
        label=_('Beni hatırla'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class UserUpdateForm(forms.ModelForm):
    """Kullanıcı bilgilerini güncelleme formu"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'})
        }

class UserProfileForm(forms.ModelForm):
    """Kullanıcı profili formu"""
    
    birth_date = forms.DateField(
        label=_('Doğum Tarihi'),
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'birth_date', 'address', 'company_name', 'job_title']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'})
        } 