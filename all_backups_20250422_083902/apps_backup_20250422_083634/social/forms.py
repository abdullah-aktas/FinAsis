from django import forms
from .models import Post, Comment, UserProfile

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'location', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        } 