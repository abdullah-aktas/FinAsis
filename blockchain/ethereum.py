# -*- coding: utf-8 -*-
from web3 import Web3
from eth_account import Account
from django.conf import settings
import logging
from datetime import datetime
import json
import os
from eth_typing import Address
from typing import Dict, Any
from decimal import Decimal

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

# Ethereum ağına bağlan
w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_RPC_URL')))

# Token sözleşmesi ABI'si
TOKEN_ABI = json.loads('''
[
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "name",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "symbol",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "totalSupply",
                "type": "uint256"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": true,
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "indexed": true,
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "internalType": "uint8",
                "name": "",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "recipient",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "sender",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "recipient",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
''')

def deploy_contract(token_name: str, token_symbol: str, total_supply: Decimal) -> str:
    """
    Yeni token sözleşmesi oluştur
    """
    try:
        # Sözleşme bytecode'unu yükle
        with open('blockchain/contracts/Token.sol', 'r') as f:
            contract_source = f.read()
        
        # Sözleşmeyi derle
        compiled_contract = w3.eth.contract(
            abi=TOKEN_ABI,
            bytecode=contract_source
        )
        
        # Sözleşmeyi deploy et
        tx_hash = compiled_contract.constructor(
            token_name,
            token_symbol,
            int(total_supply * 10**18)
        ).transact({
            'from': w3.eth.accounts[0],
            'gas': 2000000
        })
        
        # İşlemi bekle
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        
        return tx_receipt.contractAddress
        
    except Exception as e:
        raise Exception(f"Sözleşme oluşturma hatası: {str(e)}")

def mint_token(contract_address: str, amount: Decimal) -> str:
    """
    Yeni token oluştur
    """
    try:
        # Sözleşmeyi yükle
        contract = w3.eth.contract(
            address=contract_address,
            abi=TOKEN_ABI
        )
        
        # Token oluştur
        tx_hash = contract.functions.mint(
            w3.eth.accounts[0],
            int(amount * 10**18)
        ).transact({
            'from': w3.eth.accounts[0],
            'gas': 200000
        })
        
        return tx_hash.hex()
        
    except Exception as e:
        raise Exception(f"Token oluşturma hatası: {str(e)}")

def transfer_token(contract_address: str, from_address: str, to_address: str, amount: Decimal) -> str:
    """
    Token transferi yap
    """
    try:
        # Sözleşmeyi yükle
        contract = w3.eth.contract(
            address=contract_address,
            abi=TOKEN_ABI
        )
        
        # Transfer yap
        tx_hash = contract.functions.transfer(
            to_address,
            int(amount * 10**18)
        ).transact({
            'from': from_address,
            'gas': 200000
        })
        
        return tx_hash.hex()
        
    except Exception as e:
        raise Exception(f"Token transfer hatası: {str(e)}") 