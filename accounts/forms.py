from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    """Kullanıcı kaydı formu"""
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
        fields = ('username', 'email', 'role', 'password1', 'password2')
        
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

class UserUpdateForm(UserChangeForm):
    """Kullanıcı güncelleme formu"""
    password = None  # Şifre alanını kaldır
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        } 