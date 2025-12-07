# -*- coding: utf-8 -*-
from django import forms
from .models import Game, Player, Transaction, Challenge


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "description", "start_date", "end_date", "is_active"]
        labels = {
            "name": "Oyun Adı",
            "description": "Açıklama",
            "start_date": "Başlangıç Tarihi",
            "end_date": "Bitiş Tarihi",
            "is_active": "Aktif mi?",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Oyunla ilgili kısa açıklama giriniz...",
                }
            ),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["company_name", "initial_balance"]
        labels = {
            "company_name": "Şirket Adı",
            "initial_balance": "Başlangıç Bakiyesi",
        }
        widgets = {
            "initial_balance": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["transaction_type", "amount", "description"]
        labels = {
            "transaction_type": "İşlem Türü",
            "amount": "Tutar",
            "description": "Açıklama",
        }
        widgets = {
            "amount": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "İşlem detaylarını yazınız..."}
            ),
        }


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ["name", "description", "level", "is_active"]
        labels = {
            "name": "Görev Adı",
            "description": "Açıklama",
            "level": "Zorluk Seviyesi",
            "is_active": "Aktif",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "level": forms.NumberInput(attrs={"min": 1}),
        }
