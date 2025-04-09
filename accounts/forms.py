from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):
    """Kullanıcı kaydı formu"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
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