from django.db import models
from django.conf import settings
from virtual_company.models import VirtualCompany

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    virtual_company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class ChartOfAccounts(BaseModel):
    """
    Tekdüzen Hesap Planı
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[
        ('asset', 'Varlık'),
        ('liability', 'Yükümlülük'),
        ('equity', 'Özkaynak'),
        ('income', 'Gelir'),
        ('expense', 'Gider'),
    ])
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    level = models.IntegerField(default=1)
    is_leaf = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Hesap Planı'
        verbose_name_plural = 'Hesap Planı'
        ordering = ['code']

class Account(BaseModel):
    """Cari Hesap"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=[
        ('customer', 'Müşteri'),
        ('supplier', 'Tedarikçi'),
        ('employee', 'Çalışan'),
        ('other', 'Diğer'),
    ])
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Cari Hesap'
        verbose_name_plural = 'Cari Hesaplar'

class Invoice(BaseModel):
    """Fatura"""
    number = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    due_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    type = models.CharField(max_length=20, choices=[
        ('sales', 'Satış Faturası'),
        ('purchase', 'Alış Faturası'),
    ])
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.number} - {self.account.name}"

    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturalar'

class InvoiceLine(BaseModel):
    """Fatura Kalemi"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    product = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.invoice.number} - {self.product}"

    class Meta:
        verbose_name = 'Fatura Kalemi'
        verbose_name_plural = 'Fatura Kalemleri'

class Transaction(BaseModel):
    """Yevmiye Kaydı"""
    date = models.DateField()
    number = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.number} - {self.date}"

    class Meta:
        verbose_name = 'Yevmiye Kaydı'
        verbose_name_plural = 'Yevmiye Kayıtları'

class TransactionLine(BaseModel):
    """Yevmiye Kaydı Kalemi"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='lines')
    account_code = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.transaction.number} - {self.account_code}"

    class Meta:
        verbose_name = 'Yevmiye Kaydı Kalemi'
        verbose_name_plural = 'Yevmiye Kaydı Kalemleri'

class CashBox(BaseModel):
    """
    Kasa
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Kasa'
        verbose_name_plural = 'Kasalar'

class Bank(BaseModel):
    """
    Banka
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    account_number = models.CharField(max_length=50)
    iban = models.CharField(max_length=50, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Banka'
        verbose_name_plural = 'Bankalar'

class Stock(BaseModel):
    """
    Stok
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    unit = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Stok'
        verbose_name_plural = 'Stoklar'

class StockTransaction(BaseModel):
    """
    Stok Hareketi
    """
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name='transactions')
    date = models.DateField()
    type = models.CharField(max_length=20, choices=[
        ('income', 'Giriş'),
        ('expense', 'Çıkış'),
    ])
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.stock.code} - {self.date} - {self.get_type_display()}"

    class Meta:
        verbose_name = 'Stok Hareketi'
        verbose_name_plural = 'Stok Hareketleri'
        ordering = ['-date', '-created_at']
