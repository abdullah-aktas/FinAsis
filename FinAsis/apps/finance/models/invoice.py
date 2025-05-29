# -*- coding: utf-8 -*-
"""
Bu dosyada Invoice (Fatura) modeli tanımlanır.
"""
from decimal import Decimal
from django.db import models
from core.models import BaseModel

class Invoice(BaseModel):
    """Fatura modeli"""
    customer = models.ForeignKey(
        'finance.Customer',
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Müşteri'
    )
    invoice_number = models.CharField('Fatura No', max_length=50, unique=True)
    amount = models.DecimalField(
        'Tutar',
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    kdv_rate = models.DecimalField('KDV Oranı', max_digits=4, decimal_places=2, default=0.18)