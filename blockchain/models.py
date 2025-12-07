from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import hashlib
import json

User = get_user_model()


class Block(models.Model):
    """Blockchain blok yapısı - her blok birden fazla transaction içerir"""

    block_number = models.IntegerField(unique=True, db_index=True)
    previous_hash = models.CharField(max_length=64, db_index=True)
    block_hash = models.CharField(max_length=64, unique=True, db_index=True)
    timestamp = models.DateTimeField(default=timezone.now)
    nonce = models.IntegerField(default=0)
    merkle_root = models.CharField(max_length=64, blank=True)
    transactions_count = models.IntegerField(default=0)
    is_valid = models.BooleanField(default=True)
    difficulty = models.IntegerField(default=4)
    mined_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mined_blocks",
    )
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-block_number"]
        verbose_name = "Blok"
        verbose_name_plural = "Bloklar"

    def __str__(self):
        return f"Block #{self.block_number} - {self.block_hash[:8]}..."

    def calculate_hash(self):
        """Bloğun hash'ini hesapla"""
        block_string = f"{self.block_number}{self.previous_hash}{self.timestamp.isoformat()}{self.nonce}{self.merkle_root}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty=4):
        """Proof of Work - belirli sayıda sıfır ile başlayan hash bul"""
        target = "0" * difficulty
        while not self.block_hash.startswith(target):
            self.nonce += 1
            self.block_hash = self.calculate_hash()
        return self.block_hash


class Transaction(models.Model):
    """Blockchain üzerindeki transaction kayıtları"""

    TRANSACTION_TYPES = [
        ("invoice", "Fatura"),
        ("payment", "Ödeme"),
        ("expense", "Gider"),
        ("voucher", "Fiş"),
        ("contract", "Akıllı Sözleşme"),
        ("asset_transfer", "Varlık Transferi"),
        ("audit", "Denetim Kaydı"),
        ("edefter", "E-Defter"),
    ]

    STATUS_CHOICES = [
        ("pending", "Beklemede"),
        ("confirmed", "Onaylandı"),
        ("failed", "Başarısız"),
        ("cancelled", "İptal Edildi"),
    ]

    transaction_id = models.CharField(max_length=64, unique=True, db_index=True)
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, db_index=True
    )
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    payload = models.JSONField(default=dict)
    payload_hash = models.CharField(max_length=64, db_index=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    gas_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    signature = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # İlişkili kayıt bilgileri
    reference_model = models.CharField(
        max_length=50, blank=True
    )  # invoice, payment, etc.
    reference_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=["transaction_type", "status"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return (
            f"TX {self.transaction_id[:8]}... - {self.get_transaction_type_display()}"
        )

    def calculate_hash(self):
        """Transaction hash'ini hesapla"""
        tx_string = f"{self.transaction_id}{self.from_address}{self.to_address}{self.amount}{json.dumps(self.payload, sort_keys=True)}{self.timestamp.isoformat()}"
        return hashlib.sha256(tx_string.encode()).hexdigest()


class SmartContract(models.Model):
    """Akıllı sözleşme yapısı"""

    CONTRACT_TYPES = [
        ("invoice_auto", "Otomatik Faturalama"),
        ("payment_schedule", "Ödeme Planı"),
        ("multi_signature", "Çoklu İmza"),
        ("escrow", "Emanet"),
        ("subscription", "Abonelik"),
        ("custom", "Özel"),
    ]

    contract_address = models.CharField(max_length=64, unique=True, db_index=True)
    contract_name = models.CharField(max_length=100)
    contract_type = models.CharField(max_length=30, choices=CONTRACT_TYPES)
    code = models.TextField(help_text="Sözleşme kodu (JSON/Python)")
    abi = models.JSONField(
        default=dict, blank=True, help_text="Application Binary Interface"
    )
    deployed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    deployed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    execution_count = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)
    parameters = models.JSONField(default=dict)

    class Meta:
        ordering = ["-deployed_at"]
        verbose_name = "Akıllı Sözleşme"
        verbose_name_plural = "Akıllı Sözleşmeler"

    def __str__(self):
        return f"{self.contract_name} ({self.contract_address[:8]}...)"


class DigitalAsset(models.Model):
    """Dijital varlık token'ları"""

    ASSET_TYPES = [
        ("utility", "Utility Token"),
        ("security", "Security Token"),
        ("nft", "NFT"),
        ("currency", "Currency Token"),
        ("governance", "Governance Token"),
    ]

    asset_id = models.CharField(max_length=64, unique=True, db_index=True)
    asset_name = models.CharField(max_length=100)
    asset_symbol = models.CharField(max_length=10)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    total_supply = models.DecimalField(max_digits=18, decimal_places=2)
    circulating_supply = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="owned_assets"
    )
    created_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict)
    contract = models.ForeignKey(
        SmartContract, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Dijital Varlık"
        verbose_name_plural = "Dijital Varlıklar"

    def __str__(self):
        return f"{self.asset_name} ({self.asset_symbol})"


class AssetBalance(models.Model):
    """Kullanıcıların varlık bakiyeleri"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="asset_balances"
    )
    asset = models.ForeignKey(DigitalAsset, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    locked_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "asset"]
        verbose_name = "Varlık Bakiyesi"
        verbose_name_plural = "Varlık Bakiyeleri"

    def __str__(self):
        return f"{self.user.username} - {self.asset.asset_symbol}: {self.balance}"


class AuditLog(models.Model):
    """Blockchain işlemleri için denetim log'ları"""

    ACTION_TYPES = [
        ("create", "Oluşturma"),
        ("update", "Güncelleme"),
        ("delete", "Silme"),
        ("verify", "Doğrulama"),
        ("transfer", "Transfer"),
        ("execute", "Sözleşme Çalıştırma"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="blockchain_audit_logs"
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_model = models.CharField(max_length=50)
    target_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    transaction = models.ForeignKey(
        Transaction, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Denetim Logu"
        verbose_name_plural = "Denetim Logları"

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.target_model} by {self.user}"


class ChainRecord(models.Model):
    """Legacy model - blockchain entegrasyonu için"""

    reference = models.CharField(max_length=255, db_index=True)
    hash_hex = models.CharField(max_length=64, db_index=True)
    payload_preview = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(default=timezone.now)

    # Yeni alanlar - transaction ile ilişkilendirme
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chain_records",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_chain_records",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Zincir Kaydı"
        verbose_name_plural = "Zincir Kayıtları"
        indexes = [
            models.Index(fields=["reference", "hash_hex"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.hash_hex[:8]}..."
