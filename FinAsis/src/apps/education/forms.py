from django import forms
from .models import FinancialTermCard

class FinancialTermCardForm(forms.ModelForm):
    class Meta:
        model = FinancialTermCard
        fields = ['term', 'description', 'example'] 