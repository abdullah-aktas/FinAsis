from django import forms
from .models import StudentProgress

class AssignmentGradeForm(forms.ModelForm):
    """Ödev not verme formu"""
    class Meta:
        model = StudentProgress
        fields = ['grade', 'feedback']
        widgets = {
            'grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.5'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Öğrenciye geri bildirim yazın...'
            })
        }
        labels = {
            'grade': 'Not',
            'feedback': 'Geri Bildirim'
        } 