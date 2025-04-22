from django import forms
from .models import Game, Player, Transaction, Challenge

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['company_name', 'initial_balance']
        widgets = {
            'initial_balance': forms.NumberInput(attrs={'min': 0}),
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['title', 'description', 'points', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'points': forms.NumberInput(attrs={'min': 0}),
        } 