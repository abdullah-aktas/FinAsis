from web3 import Web3
from eth_account import Account
from django.conf import settings
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EthereumIntegration:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_NODE_URL))
        self.account = Account.from_key(settings.ETHEREUM_PRIVATE_KEY)
        self.contract_address = settings.ETHEREUM_CONTRACT_ADDRESS
        self.contract_abi = settings.ETHEREUM_CONTRACT_ABI
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
    def create_smart_contract(self, data):
        """
        Akıllı sözleşme oluştur
        """
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            transaction = self.contract.functions.createContract(
                data['title'],
                data['description'],
                data['amount'],
                data['parties']
            ).build_transaction({
                'chainId': settings.ETHEREUM_CHAIN_ID,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=settings.ETHEREUM_PRIVATE_KEY
            )
            
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'transaction_hash': tx_hash.hex(),
                'contract_address': receipt.contractAddress,
                'status': receipt.status
            }
        except Exception as e:
            logger.error(f"Akıllı sözleşme oluşturma hatası: {str(e)}")
            raise
            
    def execute_contract(self, contract_address, function_name, *args):
        """
        Akıllı sözleşme fonksiyonunu çalıştır
        """
        try:
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.contract_abi
            )
            
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            transaction = getattr(contract.functions, function_name)(*args).build_transaction({
                'chainId': settings.ETHEREUM_CHAIN_ID,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=settings.ETHEREUM_PRIVATE_KEY
            )
            
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'transaction_hash': tx_hash.hex(),
                'status': receipt.status
            }
        except Exception as e:
            logger.error(f"Akıllı sözleşme çalıştırma hatası: {str(e)}")
            raise
            
    def get_contract_state(self, contract_address):
        """
        Akıllı sözleşme durumunu sorgula
        """
        try:
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=self.contract_abi
            )
            
            state = {
                'title': contract.functions.title().call(),
                'description': contract.functions.description().call(),
                'amount': contract.functions.amount().call(),
                'parties': contract.functions.parties().call(),
                'status': contract.functions.status().call(),
                'created_at': contract.functions.createdAt().call()
            }
            
            return state
        except Exception as e:
            logger.error(f"Akıllı sözleşme durumu sorgulama hatası: {str(e)}")
            raise 