from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from .models import Post, Comment, UserProfile, Tag
import re

class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Ne düşünüyorsunuz?')
        }),
        validators=[
            MinLengthValidator(1, _('Gönderi en az 1 karakter içermelidir.')),
            MaxLengthValidator(5000, _('Gönderi en fazla 5000 karakter içerebilir.'))
        ]
    )
    
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    video = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'data-placeholder': _('Etiketler seçin')
        })
    )
    
    class Meta:
        model = Post
        fields = ['content', 'image', 'video', 'tags']
        
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            # Spam kontrolü
            spam_patterns = [
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            ]
            
            for pattern in spam_patterns:
                if re.search(pattern, content):
                    raise ValidationError(_('Gönderiniz spam içerik içeriyor.'))
        
        return content
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        
        if image and video:
            raise ValidationError(_('Bir gönderi hem resim hem de video içeremez.'))
        
        return cleaned_data

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Yorumunuzu yazın...')
        }),
        validators=[
            MinLengthValidator(1, _('Yorum en az 1 karakter içermelidir.')),
            MaxLengthValidator(1000, _('Yorum en fazla 1000 karakter içerebilir.'))
        ]
    )
    
    class Meta:
        model = Comment
        fields = ['content']
        
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            # Spam kontrolü
            spam_patterns = [
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            ]
            
            for pattern in spam_patterns:
                if re.search(pattern, content):
                    raise ValidationError(_('Yorumunuz spam içerik içeriyor.'))
        
        return content

class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Kendinizi tanıtın...')
        }),
        validators=[
            MaxLengthValidator(500, _('Biyografi en fazla 500 karakter içerebilir.'))
        ]
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    cover_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    location = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Konum')
        })
    )
    
    website = forms.URLField(
        required=False,
        max_length=200,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': _('Website URL')
        })
    )
    
    is_private = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    notification_settings = forms.JSONField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'cover_image', 'location',
            'website', 'is_private', 'notification_settings'
        ]
        
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(_('Profil fotoğrafı 5MB\'dan büyük olamaz.'))
        return avatar
        
    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            if cover_image.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError(_('Kapak fotoğrafı 10MB\'dan büyük olamaz.'))
        return cover_image
        
    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        return website

class TagForm(forms.ModelForm):
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Etiket adı')
        })
    )
    
    class Meta:
        model = Tag
        fields = ['name']
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Etiket adı sadece harf, rakam ve alt çizgi içerebilir
            if not re.match(r'^[a-zA-Z0-9_]+$', name):
                raise ValidationError(_('Etiket adı sadece harf, rakam ve alt çizgi içerebilir.'))
        return name 