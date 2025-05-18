# -*- coding: utf-8 -*-
from celery import shared_task
from django.core.cache import cache
from .models import Transaction, Wallet, TokenContract, TokenBalance, TokenTransaction
from web3 import Web3
import logging
from decimal import Decimal
from django.contrib.auth import get_user_model
from .ethereum import deploy_contract, mint_token, transfer_token

logger = logging.getLogger(__name__)

@shared_task
def sync_transaction_status(transaction_id):
    """
    İşlem durumunu senkronize eder.
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        network = transaction.network
        
        web3 = Web3(Web3.HTTPProvider(network.rpc_url))
        if not web3.is_connected():
            logger.error(f"Network connection failed for transaction {transaction_id}")
            return

        receipt = web3.eth.get_transaction_receipt(transaction.transaction_hash)
        if receipt is None:
            logger.info(f"Transaction {transaction_id} is still pending")
            return

        if receipt.status == 1:
            transaction.status = 'completed'
        else:
            transaction.status = 'reverted'

        transaction.gas_used = Decimal(str(receipt.gasUsed))
        transaction.save()

        logger.info(f"Transaction {transaction_id} status updated to {transaction.status}")

    except Exception as e:
        logger.error(f"Error syncing transaction {transaction_id}: {str(e)}")
        raise

@shared_task
def sync_wallet_balance(wallet_id):
    """
    Cüzdan bakiyesini senkronize eder.
    """
    try:
        wallet = Wallet.objects.get(id=wallet_id)
        network = wallet.network
        
        web3 = Web3(Web3.HTTPProvider(network.rpc_url))
        if not web3.is_connected():
            logger.error(f"Network connection failed for wallet {wallet_id}")
            return

        balance = web3.eth.get_balance(wallet.address)
        wallet.balance = Decimal(str(web3.from_wei(balance, 'ether')))
        wallet.save()

        logger.info(f"Wallet {wallet_id} balance updated to {wallet.balance}")

    except Exception as e:
        logger.error(f"Error syncing wallet {wallet_id}: {str(e)}")
        raise

@shared_task
def sync_contract_events(contract_id):
    """
    Akıllı kontrat olaylarını senkronize eder.
    """
    try:
        # Contract event synchronization logic here
        pass
    except Exception as e:
        logger.error(f"Error syncing contract events {contract_id}: {str(e)}")
        raise

@shared_task
def cleanup_old_transactions():
    """
    Eski işlemleri temizler.
    """
    try:
        # Cleanup logic here
        pass
    except Exception as e:
        logger.error(f"Error cleaning up old transactions: {str(e)}")
        raise

@shared_task
def create_token_contract(user_id, token_name, token_symbol, total_supply):
    """
    Yeni token sözleşmesi oluştur
    """
    try:
        user = get_user_model().objects.get(id=user_id)
        
        # Sözleşmeyi blockchain'e deploy et
        contract_address = deploy_contract(
            token_name=token_name,
            token_symbol=token_symbol,
            total_supply=total_supply
        )
        
        # Veritabanında sözleşmeyi oluştur
        contract = TokenContract.objects.create(
            user=user,
            contract_address=contract_address,
            token_name=token_name,
            token_symbol=token_symbol,
            total_supply=total_supply,
            status='active'
        )
        
        # Kullanıcı için başlangıç bakiyesi oluştur
        TokenBalance.objects.create(
            contract=contract,
            user=user,
            balance=total_supply
        )
        
        return {
            'status': 'success',
            'contract_id': contract.id,
            'contract_address': contract_address
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@shared_task
def mint_tokens(contract_id, amount):
    """
    Yeni token oluştur
    """
    try:
        contract = TokenContract.objects.get(id=contract_id)
        
        # Blockchain'de token oluştur
        transaction_hash = mint_token(
            contract_address=contract.contract_address,
            amount=amount
        )
        
        # Veritabanında işlemi kaydet
        TokenTransaction.objects.create(
            contract=contract,
            from_user=contract.user,
            to_user=contract.user,
            amount=amount,
            transaction_type='mint',
            transaction_hash=transaction_hash
        )
        
        # Bakiyeyi güncelle
        balance = TokenBalance.objects.get(
            contract=contract,
            user=contract.user
        )
        balance.balance += amount
        balance.save()
        
        return {
            'status': 'success',
            'transaction_hash': transaction_hash
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@shared_task
def transfer_tokens(contract_id, from_user_id, to_user_id, amount):
    """
    Token transferi yap
    """
    try:
        contract = TokenContract.objects.get(id=contract_id)
        from_user = get_user_model().objects.get(id=from_user_id)
        to_user = get_user_model().objects.get(id=to_user_id)
        
        # Blockchain'de transfer yap
        transaction_hash = transfer_token(
            contract_address=contract.contract_address,
            from_address=from_user.wallets.first().address,
            to_address=to_user.wallets.first().address,
            amount=amount
        )
        
        # Veritabanında işlemi kaydet
        TokenTransaction.objects.create(
            contract=contract,
            from_user=from_user,
            to_user=to_user,
            amount=amount,
            transaction_type='transfer',
            transaction_hash=transaction_hash
        )
        
        # Bakiyeleri güncelle
        from_balance = TokenBalance.objects.get(
            contract=contract,
            user=from_user
        )
        from_balance.balance -= amount
        from_balance.save()
        
        to_balance, _ = TokenBalance.objects.get_or_create(
            contract=contract,
            user=to_user,
            defaults={'balance': Decimal('0')}
        )
        to_balance.balance += amount
        to_balance.save()
        
        return {
            'status': 'success',
            'transaction_hash': transaction_hash
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 