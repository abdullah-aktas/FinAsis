from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags', 'language']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'title': _('Başlık'),
            'content': _('İçerik'),
            'tags': _('Etiketler'),
            'language': _('Dil')
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }
        labels = {
            'content': _('Yorum')
        } 