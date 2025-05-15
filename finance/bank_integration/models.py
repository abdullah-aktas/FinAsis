from django.db import models

class IntegratedBankAccount(models.Model):
    # ... aynı alanlar ...
    pass 

class BankAccount(models.Model):
    # ... mevcut alanlar ...
    class Meta:
        app_label = 'bank_integration' 