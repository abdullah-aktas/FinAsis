from django import forms
from .models import Document, Category

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'category', 'status', 'shared_with']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'shared_with': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'parent': forms.Select(attrs={'class': 'select2'}),
        } 