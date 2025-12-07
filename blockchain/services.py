import hashlib
import json
from typing import Iterable, Optional, Dict, Any
from django.utils import timezone
from .models import (
    ChainRecord,
    Block,
    Transaction,
    SmartContract,
    DigitalAsset,
    AssetBalance,
)
from django.db import transaction as db_transaction


# ============================================================================
# HASH VE KRİPTOGRAFİ FONKSİYONLARI
# ============================================================================


def compute_sha256_hex(payload: str) -> str:
    """String payload'ın SHA-256 hash'ini hesapla"""
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_merkle_root(transactions: list) -> str:
    """Transaction listesinden Merkle root hesapla"""
    if not transactions:
        return compute_sha256_hex("")

    hashes = [tx.payload_hash for tx in transactions]

    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])  # Tek sayıda ise son hash'i tekrarla

        new_hashes = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i + 1]
            new_hashes.append(compute_sha256_hex(combined))
        hashes = new_hashes

    return hashes[0]


# ============================================================================
# BLOCKCHAIN YÖNETİMİ
# ============================================================================


class BlockchainManager:
    """Blockchain yönetimi için ana sınıf"""

    @staticmethod
    def get_latest_block() -> Optional[Block]:
        """Zincirdeki son bloğu getir"""
        return Block.objects.order_by("-block_number").first()

    @staticmethod
    def create_genesis_block() -> Block:
        """Genesis (ilk) bloğu oluştur"""
        genesis = Block.objects.create(
            block_number=0,
            previous_hash="0" * 64,
            block_hash="0" * 64,
            merkle_root=compute_sha256_hex("Genesis Block"),
            transactions_count=0,
            data={"message": "FinAsis Blockchain Genesis Block"},
        )
        genesis.block_hash = genesis.calculate_hash()
        genesis.save()
        return genesis

    @staticmethod
    @db_transaction.atomic
    def create_new_block(
        transactions: list = None, mined_by=None, difficulty=4
    ) -> Block:
        """Yeni blok oluştur ve mine et"""
        latest_block = BlockchainManager.get_latest_block()

        if not latest_block:
            return BlockchainManager.create_genesis_block()

        # Bekleyen transaction'ları al
        if transactions is None:
            transactions = list(
                Transaction.objects.filter(status="pending", block__isnull=True)[:100]
            )  # Blok başına max 100 transaction

        # Yeni blok oluştur
        new_block = Block.objects.create(
            block_number=latest_block.block_number + 1,
            previous_hash=latest_block.block_hash,
            block_hash="",
            merkle_root=compute_merkle_root(transactions),
            transactions_count=len(transactions),
            difficulty=difficulty,
            mined_by=mined_by,
        )

        # Transaction'ları bloğa ata
        for tx in transactions:
            tx.block = new_block
            tx.status = "confirmed"
            tx.save()

        # Bloğu mine et
        new_block.mine_block(difficulty)
        new_block.save()

        return new_block

    @staticmethod
    def verify_chain() -> tuple[bool, list]:
        """Blockchain'in bütünlüğünü doğrula"""
        blocks = Block.objects.order_by("block_number")
        errors = []

        for i, block in enumerate(blocks):
            # Hash doğrulama
            calculated_hash = block.calculate_hash()
            if block.block_hash != calculated_hash:
                errors.append(f"Block #{block.block_number}: Hash mismatch")

            # Önceki blok bağlantısı
            if i > 0:
                previous_block = blocks[i - 1]
                if block.previous_hash != previous_block.block_hash:
                    errors.append(
                        f"Block #{block.block_number}: Previous hash mismatch"
                    )

        return (len(errors) == 0, errors)


# ============================================================================
# TRANSACTION YÖNETİMİ
# ============================================================================


class TransactionManager:
    """Transaction yönetimi"""

    @staticmethod
    def create_transaction(
        transaction_type: str,
        from_address: str,
        to_address: str,
        amount: float = 0,
        payload: dict = None,
        created_by=None,
        reference_model: str = "",
        reference_id: int = None,
    ) -> Transaction:
        """Yeni transaction oluştur"""
        if payload is None:
            payload = {}

        # Transaction ID oluştur (timestamp + hash)
        tx_id = compute_sha256_hex(
            f"{timezone.now().isoformat()}{from_address}{to_address}{amount}"
        )

        # Payload hash
        payload_hash = compute_sha256_hex(json.dumps(payload, sort_keys=True))

        tx = Transaction.objects.create(
            transaction_id=tx_id,
            transaction_type=transaction_type,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            payload=payload,
            payload_hash=payload_hash,
            created_by=created_by,
            reference_model=reference_model,
            reference_id=reference_id,
        )

        return tx

    @staticmethod
    def verify_transaction(transaction_id: str) -> tuple[bool, str]:
        """Transaction'ı doğrula"""
        try:
            tx = Transaction.objects.get(transaction_id=transaction_id)

            # Payload hash kontrolü
            calculated_hash = compute_sha256_hex(json.dumps(tx.payload, sort_keys=True))
            if tx.payload_hash != calculated_hash:
                return (False, "Payload hash mismatch")

            # Blok kontrolü
            if tx.block and tx.status == "confirmed":
                return (True, "Transaction verified in block")

            return (False, "Transaction not confirmed yet")

        except Transaction.DoesNotExist:
            return (False, "Transaction not found")


# ============================================================================
# AKILLI SÖZLEŞME YÖNETİMİ
# ============================================================================


class SmartContractManager:
    """Akıllı sözleşme yönetimi"""

    @staticmethod
    def deploy_contract(
        contract_name: str,
        contract_type: str,
        code: str,
        deployed_by,
        parameters: dict = None,
    ) -> SmartContract:
        """Yeni akıllı sözleşme deploy et"""
        if parameters is None:
            parameters = {}

        # Contract address oluştur
        contract_address = compute_sha256_hex(
            f"{contract_name}{timezone.now().isoformat()}{deployed_by.id}"
        )

        contract = SmartContract.objects.create(
            contract_address=contract_address,
            contract_name=contract_name,
            contract_type=contract_type,
            code=code,
            deployed_by=deployed_by,
            parameters=parameters,
        )

        return contract

    @staticmethod
    def execute_contract(
        contract_address: str, execution_params: dict
    ) -> Dict[str, Any]:
        """Akıllı sözleşme çalıştır"""
        try:
            contract = SmartContract.objects.get(
                contract_address=contract_address, is_active=True
            )

            # Execution count artır
            contract.execution_count += 1
            contract.last_executed = timezone.now()
            contract.save()

            # Basit sözleşme tiplerine göre işlem yap
            result = {
                "success": True,
                "contract": contract.contract_name,
                "executed_at": timezone.now().isoformat(),
                "result": {},
            }

            if contract.contract_type == "invoice_auto":
                result["result"] = {"message": "Otomatik fatura oluşturuldu"}

            elif contract.contract_type == "payment_schedule":
                result["result"] = {"message": "Ödeme planı başlatıldı"}

            return result

        except SmartContract.DoesNotExist:
            return {"success": False, "error": "Contract not found"}


# ============================================================================
# DİJİTAL VARLIK YÖNETİMİ
# ============================================================================


class AssetManager:
    """Dijital varlık yönetimi"""

    @staticmethod
    @db_transaction.atomic
    def create_asset(
        asset_name: str,
        asset_symbol: str,
        asset_type: str,
        total_supply: float,
        owner,
        metadata: dict = None,
    ) -> DigitalAsset:
        """Yeni dijital varlık oluştur"""
        if metadata is None:
            metadata = {}

        asset_id = compute_sha256_hex(
            f"{asset_name}{asset_symbol}{timezone.now().isoformat()}"
        )

        asset = DigitalAsset.objects.create(
            asset_id=asset_id,
            asset_name=asset_name,
            asset_symbol=asset_symbol,
            asset_type=asset_type,
            total_supply=total_supply,
            circulating_supply=total_supply,
            owner=owner,
            metadata=metadata,
        )

        # Owner'a bakiye oluştur
        AssetBalance.objects.create(user=owner, asset=asset, balance=total_supply)

        return asset

    @staticmethod
    @db_transaction.atomic
    def transfer_asset(
        asset: DigitalAsset, from_user, to_user, amount: float, created_by=None
    ) -> tuple[bool, str]:
        """Varlık transferi yap"""
        try:
            # From balance kontrol
            from_balance, _ = AssetBalance.objects.get_or_create(
                user=from_user, asset=asset, defaults={"balance": 0}
            )

            if from_balance.balance < amount:
                return (False, "Insufficient balance")

            # To balance
            to_balance, _ = AssetBalance.objects.get_or_create(
                user=to_user, asset=asset, defaults={"balance": 0}
            )

            # Transfer yap
            from_balance.balance -= amount
            from_balance.save()

            to_balance.balance += amount
            to_balance.save()

            # Transaction oluştur
            TransactionManager.create_transaction(
                transaction_type="asset_transfer",
                from_address=f"user:{from_user.id}",
                to_address=f"user:{to_user.id}",
                amount=amount,
                payload={
                    "asset_id": asset.asset_id,
                    "asset_symbol": asset.asset_symbol,
                    "from_balance_after": float(from_balance.balance),
                    "to_balance_after": float(to_balance.balance),
                },
                created_by=created_by,
            )

            return (True, "Transfer successful")

        except Exception as e:
            return (False, str(e))


# ============================================================================
# LEGACY FONKSİYONLAR (Geriye Uyumluluk)
# ============================================================================


def ensure_record(reference: str, payload: str, status: str = "pending") -> ChainRecord:
    """ChainRecord oluştur (legacy)"""
    hash_hex = compute_sha256_hex(payload)
    record, _ = ChainRecord.objects.get_or_create(
        reference=reference,
        hash_hex=hash_hex,
        defaults={
            "payload_preview": payload[:500],
            "status": status,
        },
    )
    return record


# Payload helpers (eski sistemle uyumluluk)
def payload_for_invoice(invoice) -> str:
    return (
        f"INVOICE|{invoice.id}|{invoice.invoice_number}|{invoice.issue_date}|"
        f"{invoice.total_amount}|{invoice.customer_id}|{getattr(invoice, 'company_id', '')}|"
        f"{getattr(invoice, 'gib_uuid', '')}|{getattr(invoice, 'gib_status', '')}"
    )


def payload_for_voucher(voucher, lines: Iterable) -> str:
    line_parts = []
    for ln in lines:
        line_parts.append(
            f"{ln.line_no}:{ln.account_id}:{ln.debit_amount}:{ln.credit_amount}:{ln.description or ''}"
        )
    lines_str = ";".join(sorted(line_parts))
    return (
        f"VOUCHER|{voucher.id}|{voucher.number}|{voucher.date}|{voucher.company_id}|{voucher.type_id}|"
        f"{voucher.state}|{lines_str}"
    )


def payload_for_payment(payment) -> str:
    return (
        f"PAYMENT|{payment.id}|{payment.company_id}|{payment.customer_id}|{payment.amount}|"
        f"{payment.payment_method}|{payment.payment_date}|{payment.related_invoice_id or ''}"
    )


def payload_for_expense(expense) -> str:
    return f"EXPENSE|{expense.id}|{expense.company_id}|{expense.category}|{expense.amount}|{expense.expense_date}|{int(expense.paid)}"


def payload_for_banktxn(txn) -> str:
    return f"BANKTXN|{txn.id}|{txn.account_id}|{txn.amount}|{txn.transaction_type}|{txn.date}"


def payload_for_edefter(edefter) -> str:
    return f"EDEFTER|{edefter.id}|{edefter.year}-{edefter.month}|{edefter.type}|{edefter.xml_file.name}|{edefter.berat_file.name}|{edefter.status}"
