from decimal import Decimal
from core.models import BaseModel
from django.conf import settings

class Invoice(BaseModel):
    """Fatura modeli"""
    customer = models.ForeignKey(
        'crm.Customer',  # String referans kullanarak circular import'u engelliyoruz
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    invoice_number = models.CharField(_('Fatura No'), max_length=50, unique=True)
    amount = models.DecimalField(
        _('Tutar'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )