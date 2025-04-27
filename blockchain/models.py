from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import uuid
from decimal import Decimal
from virtual_company.models import VirtualCompany

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    virtual_company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class BlockchainNetwork(models.Model):
    NETWORK_CHOICES = (
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
        ('binance', 'Binance Smart Chain'),
        ('arbitrum', 'Arbitrum'),
        ('optimism', 'Optimism'),
    )

    name = models.CharField(_('Network Name'), max_length=100)
    network_id = models.CharField(_('Network ID'), max_length=50, unique=True)
    rpc_url = models.URLField(_('RPC URL'))
    chain_id = models.IntegerField(_('Chain ID'))
    currency_symbol = models.CharField(_('Currency Symbol'), max_length=10)
    block_explorer_url = models.URLField(_('Block Explorer URL'))
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        app_label = 'blockchain'
        verbose_name = _('Blockchain Network')
        verbose_name_plural = _('Blockchain Networks')
        indexes = [
            models.Index(fields=['network_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.network_id})"

class SmartContract(models.Model):
    CONTRACT_TYPES = (
        ('erc20', 'ERC-20'),
        ('erc721', 'ERC-721'),
        ('erc1155', 'ERC-1155'),
        ('custom', 'Custom'),
    )

    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='contracts')
    name = models.CharField(_('Contract Name'), max_length=100)
    address = models.CharField(_('Contract Address'), max_length=42, unique=True)
    contract_type = models.CharField(_('Contract Type'), max_length=20, choices=CONTRACT_TYPES)
    abi = models.JSONField(_('Contract ABI'))
    version = models.CharField(_('Version'), max_length=20)
    is_verified = models.BooleanField(_('Is Verified'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        app_label = 'blockchain'
        verbose_name = _('Smart Contract')
        verbose_name_plural = _('Smart Contracts')
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['contract_type']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.name} ({self.address})"

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reverted', 'Reverted'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='transactions')
    contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    from_address = models.CharField(_('From Address'), max_length=42)
    to_address = models.CharField(_('To Address'), max_length=42)
    value = models.DecimalField(_('Value'), max_digits=36, decimal_places=18, validators=[MinValueValidator(Decimal('0'))])
    gas_price = models.DecimalField(_('Gas Price'), max_digits=36, decimal_places=18)
    gas_used = models.DecimalField(_('Gas Used'), max_digits=36, decimal_places=18)
    transaction_hash = models.CharField(_('Transaction Hash'), max_length=66, unique=True)
    block_number = models.BigIntegerField(_('Block Number'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        app_label = 'blockchain'
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['from_address']),
            models.Index(fields=['to_address']),
            models.Index(fields=['status']),
            models.Index(fields=['block_number']),
        ]

    def __str__(self):
        return f"{self.transaction_hash}"

class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallets')
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='wallets')
    address = models.CharField(_('Wallet Address'), max_length=42, unique=True)
    private_key = models.CharField(_('Private Key'), max_length=66, blank=True, null=True)
    balance = models.DecimalField(_('Balance'), max_digits=36, decimal_places=18, default=0)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        app_label = 'blockchain'
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['user', 'network']

    def __str__(self):
        return f"{self.user.username} - {self.network.name} ({self.address})"

class Token(models.Model):
    contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='tokens')
    token_id = models.CharField(_('Token ID'), max_length=100)
    name = models.CharField(_('Token Name'), max_length=100)
    symbol = models.CharField(_('Token Symbol'), max_length=20)
    decimals = models.IntegerField(_('Decimals'), validators=[MinValueValidator(0), MaxValueValidator(18)])
    total_supply = models.DecimalField(_('Total Supply'), max_digits=36, decimal_places=18)
    owner = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='owned_tokens', null=True, blank=True)
    metadata = models.JSONField(_('Token Metadata'), default=dict)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        app_label = 'blockchain'
        verbose_name = _('Token')
        verbose_name_plural = _('Tokens')
        indexes = [
            models.Index(fields=['token_id']),
            models.Index(fields=['name']),
            models.Index(fields=['symbol']),
        ]
        unique_together = ['contract', 'token_id']

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class BlockchainTransaction(BaseModel):
    """
    Blockchain İşlemi
    """
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
    ]
    
    TRANSACTION_TYPES = [
        ('invoice', 'Fatura'),
        ('payment', 'Ödeme'),
        ('account', 'Cari Hesap'),
        ('other', 'Diğer'),
    ]
    
    title = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    reference_model = models.CharField(max_length=100, blank=True, null=True)
    data_hash = models.CharField(max_length=64, blank=True, null=True)
    blockchain_hash = models.CharField(max_length=66, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_transaction_type_display()}"
    
    class Meta:
        app_label = 'blockchain'
        verbose_name = 'Blockchain İşlemi'
        verbose_name_plural = 'Blockchain İşlemleri'
        ordering = ['-created_at']

class BlockchainLog(BaseModel):
    """
    Blockchain Log
    """
    transaction = models.ForeignKey(BlockchainTransaction, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20)
    message = models.TextField()
    error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction.title} - {self.status} - {self.created_at}"
    
    class Meta:
        app_label = 'blockchain'
        verbose_name = 'Blockchain Log'
        verbose_name_plural = 'Blockchain Logları'
        ordering = ['-created_at']

class TokenContract(models.Model):
    """
    FinAsis Token Sözleşmesi
    """
    CONTRACT_STATUS = [
        ('draft', 'Taslak'),
        ('active', 'Aktif'),
        ('paused', 'Duraklatıldı'),
        ('terminated', 'Sonlandırıldı'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token_contracts')
    contract_address = models.CharField(max_length=42, unique=True)
    token_name = models.CharField(max_length=100)
    token_symbol = models.CharField(max_length=10)
    total_supply = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('1000000'))
    decimals = models.IntegerField(default=18)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'blockchain'
        verbose_name = 'Token Sözleşmesi'
        verbose_name_plural = 'Token Sözleşmeleri'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.token_name} ({self.token_symbol})"

class TokenBalance(models.Model):
    """
    Token Bakiyesi
    """
    contract = models.ForeignKey(TokenContract, on_delete=models.CASCADE, related_name='balances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token_balances')
    balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    locked_balance = models.DecimalField(max_digits=36, decimal_places=18, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'blockchain'
        verbose_name = 'Token Bakiyesi'
        verbose_name_plural = 'Token Bakiyeleri'
        unique_together = ['contract', 'user']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.contract.token_symbol}: {self.balance}"

class TokenTransaction(models.Model):
    """
    Token İşlemi
    """
    TRANSACTION_TYPES = [
        ('mint', 'Token Oluşturma'),
        ('burn', 'Token Yakma'),
        ('transfer', 'Transfer'),
        ('lock', 'Kilitli Bakiye'),
        ('unlock', 'Kilit Açma'),
    ]
    
    contract = models.ForeignKey(TokenContract, on_delete=models.CASCADE, related_name='transactions')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=36, decimal_places=18)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_hash = models.CharField(max_length=66, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'blockchain'
        verbose_name = 'Token İşlemi'
        verbose_name_plural = 'Token İşlemleri'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} {self.contract.token_symbol}"
