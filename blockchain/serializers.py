# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import BlockchainNetwork, SmartContract, Transaction, Wallet, Token
from django.core.validators import MinValueValidator
from decimal import Decimal

class BlockchainNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainNetwork
        fields = ['id', 'name', 'network_id', 'chain_id', 'currency_symbol', 'block_explorer_url']
        read_only_fields = ['id']

class SmartContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartContract
        fields = ['id', 'network', 'name', 'address', 'contract_type', 'version', 'is_verified']
        read_only_fields = ['id', 'is_verified']

    def validate_address(self, value):
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid contract address format")
        return value

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'network', 'contract', 'from_address', 'to_address',
            'value', 'gas_price', 'gas_used', 'transaction_hash',
            'block_number', 'status'
        ]
        read_only_fields = ['id', 'status']

    def validate(self, data):
        if data['from_address'] == data['to_address']:
            raise serializers.ValidationError("From and to addresses cannot be the same")
        return data

    def validate_value(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError("Value cannot be negative")
        return value

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'network', 'address', 'balance', 'is_active']
        read_only_fields = ['id', 'user', 'address', 'balance']

    def validate_address(self, value):
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid wallet address format")
        return value

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = [
            'id', 'contract', 'token_id', 'name', 'symbol',
            'decimals', 'total_supply', 'owner', 'metadata'
        ]
        read_only_fields = ['id', 'contract', 'token_id', 'name', 'symbol', 'decimals']

    def validate_total_supply(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError("Total supply cannot be negative")
        return value 