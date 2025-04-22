from celery import shared_task
from django.core.cache import cache
from .models import Transaction, Wallet
from web3 import Web3
import logging
from decimal import Decimal

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