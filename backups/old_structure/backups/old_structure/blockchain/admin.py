# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import BlockchainTransaction, BlockchainLog

@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('title', 'reference_id', 'notes')
    readonly_fields = ('data_hash', 'blockchain_hash')
    ordering = ('-created_at',)

@admin.register(BlockchainLog)
class BlockchainLogAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction__title', 'message', 'error')
    readonly_fields = ('transaction', 'status', 'message', 'error')
    ordering = ('-created_at',)
