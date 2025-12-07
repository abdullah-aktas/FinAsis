from django.contrib import admin
from .models import (
    Block,
    Transaction,
    SmartContract,
    DigitalAsset,
    AssetBalance,
    AuditLog,
    ChainRecord,
)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = [
        "block_number",
        "block_hash_short",
        "transactions_count",
        "mined_by",
        "timestamp",
        "is_valid",
    ]
    list_filter = ["is_valid", "difficulty"]
    search_fields = ["block_hash", "previous_hash"]
    readonly_fields = ["block_hash", "merkle_root", "timestamp"]

    def block_hash_short(self, obj):
        return f"{obj.block_hash[:16]}..."

    block_hash_short.short_description = "Block Hash"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_id_short",
        "transaction_type",
        "amount",
        "status",
        "block",
        "timestamp",
    ]
    list_filter = ["transaction_type", "status", "timestamp"]
    search_fields = ["transaction_id", "from_address", "to_address"]
    readonly_fields = ["transaction_id", "payload_hash", "timestamp"]

    def transaction_id_short(self, obj):
        return f"{obj.transaction_id[:12]}..."

    transaction_id_short.short_description = "TX ID"


@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = [
        "contract_name",
        "contract_type",
        "deployed_by",
        "execution_count",
        "is_active",
        "deployed_at",
    ]
    list_filter = ["contract_type", "is_active"]
    search_fields = ["contract_name", "contract_address"]
    readonly_fields = ["contract_address", "deployed_at", "last_executed"]


@admin.register(DigitalAsset)
class DigitalAssetAdmin(admin.ModelAdmin):
    list_display = [
        "asset_name",
        "asset_symbol",
        "asset_type",
        "total_supply",
        "owner",
        "created_at",
    ]
    list_filter = ["asset_type"]
    search_fields = ["asset_name", "asset_symbol", "asset_id"]
    readonly_fields = ["asset_id", "created_at"]


@admin.register(AssetBalance)
class AssetBalanceAdmin(admin.ModelAdmin):
    list_display = ["user", "asset", "balance", "locked_balance", "last_updated"]
    list_filter = ["asset"]
    search_fields = ["user__username", "asset__asset_symbol"]
    readonly_fields = ["last_updated"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action_type", "target_model", "user", "timestamp"]
    list_filter = ["action_type", "target_model", "timestamp"]
    search_fields = ["description", "user__username"]
    readonly_fields = ["timestamp"]


@admin.register(ChainRecord)
class ChainRecordAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "hash_hex_short",
        "status",
        "transaction",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = ["reference", "hash_hex"]
    readonly_fields = ["created_at", "verified_at"]

    def hash_hex_short(self, obj):
        return f"{obj.hash_hex[:16]}..."

    hash_hex_short.short_description = "Hash"
