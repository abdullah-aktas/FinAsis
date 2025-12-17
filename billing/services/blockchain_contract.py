# -*- coding: utf-8 -*-
"""
Billing Blockchain Contract Service
Abonelik ve beta üyelik için blockchain sözleşme oluşturma
"""
import json
import logging
from decimal import Decimal
from django.utils import timezone
from django.conf import settings

from blockchain.services import SmartContractManager, TransactionManager
from blockchain.models import SmartContract
from billing.models import SubscriptionProfile, Plan, Invoice, Transaction as BillingTransaction

logger = logging.getLogger(__name__)


class SubscriptionBlockchainService:
    """Abonelik blockchain sözleşme servisi"""
    
    BLOCKCHAIN_THRESHOLD = Decimal('10000.00')  # 10.000₺ eşiği
    
    @staticmethod
    def should_create_contract(subscription_profile):
        """Sözleşme oluşturulmalı mı kontrol et"""
        if not subscription_profile.plan:
            return False
        
        # Beta plan kontrolü
        if subscription_profile.plan.is_beta_plan:
            return True
        
        # 10.000₺ üzeri abonelik kontrolü
        try:
            # Aylık fiyat kontrolü
            monthly_price = subscription_profile.plan.prices.filter(
                period='month',
                is_active=True
            ).first()
            
            if monthly_price and monthly_price.amount >= SubscriptionBlockchainService.BLOCKCHAIN_THRESHOLD:
                return True
            
            # Yıllık fiyat kontrolü
            yearly_price = subscription_profile.plan.prices.filter(
                period='year',
                is_active=True
            ).first()
            
            if yearly_price and yearly_price.amount >= SubscriptionBlockchainService.BLOCKCHAIN_THRESHOLD:
                return True
        except Exception as e:
            logger.error(f"Fiyat kontrolü hatası: {e}")
        
        return False
    
    @staticmethod
    def create_subscription_contract(subscription_profile, transaction=None):
        """Abonelik için blockchain sözleşmesi oluştur"""
        if not SubscriptionBlockchainService.should_create_contract(subscription_profile):
            return None
        
        try:
            user = subscription_profile.user
            plan = subscription_profile.plan
            
            # Sözleşme terimleri
            contract_terms = {
                "subscription_id": str(subscription_profile.id),
                "user_id": user.id,
                "user_email": user.email,
                "user_username": user.username,
                "plan_code": plan.code,
                "plan_name": plan.name,
                "subscription_status": subscription_profile.status,
                "start_date": subscription_profile.created_at.isoformat(),
                "end_date": (
                    subscription_profile.current_period_end.isoformat()
                    if subscription_profile.current_period_end
                    else None
                ),
                "terms": {
                    "billing_period": "monthly" if subscription_profile.current_period_end else "yearly",
                    "auto_renew": True,
                    "cancellation_policy": "30 days notice required",
                    "refund_policy": "Pro-rated refund for unused period",
                },
                "pricing": {
                    "base_amount": str(plan.prices.filter(is_active=True).first().amount if plan.prices.filter(is_active=True).exists() else 0),
                    "currency": "TRY",
                    "beta_discount": str(plan.beta_discount_percent) if plan.is_beta_plan else "0",
                },
                "beta_membership": {
                    "is_beta": plan.is_beta_plan,
                    "beta_benefits": [
                        "Early access to new features",
                        "Priority support",
                        "Beta discount",
                        "Partnership opportunities",
                    ] if plan.is_beta_plan else [],
                },
                "partnership": {
                    "is_partner": plan.is_beta_plan,  # Beta üyeler ortak sayılır
                    "partnership_terms": {
                        "revenue_share": "Available for enterprise plans",
                        "referral_bonus": "10% commission on referrals",
                        "co_marketing": "Joint marketing opportunities",
                    } if plan.is_beta_plan else {},
                },
                "legal": {
                    "governing_law": "Turkish Law",
                    "jurisdiction": "Istanbul, Turkey",
                    "dispute_resolution": "Arbitration",
                },
            }
            
            # Transaction bilgisi varsa ekle
            if transaction:
                contract_terms["transaction"] = {
                    "transaction_id": str(transaction.id),
                    "amount": str(transaction.amount),
                    "currency": transaction.currency,
                    "method": transaction.method,
                    "status": transaction.status,
                }
            
            # Smart Contract oluştur
            contract = SmartContractManager.deploy_contract(
                contract_name=f"Subscription_{subscription_profile.id}_{user.username}",
                contract_type="subscription",
                code=json.dumps(contract_terms, indent=2, ensure_ascii=False),
                deployed_by=user,
                parameters=contract_terms,
            )
            
            # Blockchain transaction oluştur
            blockchain_tx = TransactionManager.create_transaction(
                transaction_type="subscription_contract",
                from_address="finasis_platform",
                to_address=f"user_{user.id}",
                amount=0,  # Sözleşme kaydı, ücret yok
                payload={
                    "action": "create_subscription_contract",
                    "contract_address": contract.contract_address,
                    "subscription_id": str(subscription_profile.id),
                    "plan_name": plan.name,
                    "is_beta": plan.is_beta_plan,
                    "amount_threshold": str(SubscriptionBlockchainService.BLOCKCHAIN_THRESHOLD),
                },
                created_by=user,
                reference_model="billing.SubscriptionProfile",
                reference_id=subscription_profile.id,
            )
            
            logger.info(
                f"Blockchain sözleşmesi oluşturuldu: {contract.contract_address} "
                f"for subscription {subscription_profile.id} (User: {user.username})"
            )
            
            return {
                "contract": contract,
                "transaction": blockchain_tx,
                "contract_address": contract.contract_address,
            }
            
        except Exception as e:
            logger.error(
                f"Blockchain sözleşme oluşturma hatası: {e}",
                exc_info=True
            )
            return None
    
    @staticmethod
    def get_user_contracts(user):
        """Kullanıcının blockchain sözleşmelerini getir"""
        contracts = SmartContract.objects.filter(
            deployed_by=user,
            contract_type="subscription",
            is_active=True
        ).order_by('-deployed_at')
        
        return contracts
    
    @staticmethod
    def verify_contract(subscription_profile):
        """Sözleşme doğrula"""
        contracts = SmartContract.objects.filter(
            deployed_by=subscription_profile.user,
            contract_type="subscription",
            is_active=True,
            parameters__subscription_id=str(subscription_profile.id)
        )
        
        return contracts.exists()

