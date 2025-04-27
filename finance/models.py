"""
Finance Modülü - Model Sınıfları
---------------------
Bu dosya, Finance modülünün model sınıflarını içerir.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Transaction(models.Model):
    """
    Finansal işlem modeli.
    """
    TRANSACTION_TYPES = (
        ('income', _('Gelir')),
        ('expense', _('Gider')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Miktar')
    )
    type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        verbose_name=_('İşlem Türü')
    )
    category = models.CharField(
        max_length=50,
        verbose_name=_('Kategori')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Açıklama')
    )
    date = models.DateField(
        verbose_name=_('Tarih')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        app_label = 'finance'
        verbose_name = _('İşlem')
        verbose_name_plural = _('İşlemler')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} ({self.category})"

class Budget(models.Model):
    """
    Bütçe modeli.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.CharField(
        max_length=50,
        verbose_name=_('Kategori')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Bütçe Miktarı')
    )
    start_date = models.DateField(
        verbose_name=_('Başlangıç Tarihi')
    )
    end_date = models.DateField(
        verbose_name=_('Bitiş Tarihi')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Oluşturulma Tarihi')
    )
    
    class Meta:
        app_label = 'finance'
        verbose_name = _('Bütçe')
        verbose_name_plural = _('Bütçeler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category} - {self.amount}" 