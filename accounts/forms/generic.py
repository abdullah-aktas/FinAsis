# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from ..models import User

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    """Kullanıcı kayıt formu"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Form alanlarına Bootstrap sınıflarını ekle
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email

class UserUpdateForm(forms.ModelForm):
    """Kullanıcı güncelleme formu"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Kullanıcı Adı',
            'email': 'E-posta',
            'first_name': 'Ad',
            'last_name': 'Soyad'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        } 