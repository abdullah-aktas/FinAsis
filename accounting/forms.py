"""
Muhasebe ile ilgili formlar burada tanımlanır.
"""

from django import forms

class AccountingForm(forms.Form):
    """Muhasebe formu açıklaması."""
    hesap_adi = forms.CharField(max_length=255)

# class AccountingForm(forms.Form):
#     """Muhasebe formu açıklaması."""
#     hesap_adi = forms.CharField(max_length=255) 