# -*- coding: utf-8 -*-
"""
Mali Müşavir Blockchain Anlaşma Servisi
Platform ile mali müşavir arasındaki anlaşmaların blockchain'e kaydedilmesi
"""
from django.utils import timezone
from decimal import Decimal
import json

try:
    from blockchain.services import TransactionManager, SmartContractManager
    from blockchain.models import SmartContract, Transaction
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    TransactionManager = None  # type: ignore
    SmartContractManager = None  # type: ignore
    SmartContract = None  # type: ignore
    Transaction = None  # type: ignore
    print("WARNING: Blockchain modülü bulunamadı. Blockchain özellikleri devre dışı.")


class ConsultantBlockchainService:
    """
    Mali Müşavir Blockchain Anlaşma Servisi
    
    Platform ile mali müşavir arasında:
    - Komisyon oranı
    - Hizmet şartları
    - Ödeme koşulları
    - Süre ve fesih şartları
    blockchain üzerine kaydedilir ve değiştirilemez hale gelir.
    """
    
    DEFAULT_CONTRACT_TERMS = {
        'platform': 'FinAsis Mali Müşavir Marketplace',
        'contract_type': 'consultant_platform_agreement',
        'version': '1.0',
    }
    
    @staticmethod
    def create_consultant_agreement(consultant_profile, admin_user=None):
        """
        Mali müşavir için platform anlaşması oluştur ve blockchain'e kaydet
        
        Args:
            consultant_profile: ConsultantProfile instance
            admin_user: Onaylayan admin kullanıcısı
        
        Returns:
            dict: Blockchain transaction ve contract bilgileri
        """
        if not BLOCKCHAIN_AVAILABLE:
            raise Exception("Blockchain modülü aktif değil")
        
        # Anlaşma şartlarını hazırla
        contract_terms = {
            **ConsultantBlockchainService.DEFAULT_CONTRACT_TERMS,
            'consultant_id': consultant_profile.id,
            'consultant_name': consultant_profile.display_name,
            'advisor_chamber_no': consultant_profile.advisor.chamber_no,
            'consultant_type': consultant_profile.advisor.type,
            'commission_rate': float(consultant_profile.commission_rate),
            'hourly_rate': float(consultant_profile.hourly_rate),
            'city': consultant_profile.city,
            'specializations': consultant_profile.specializations,
            'agreement_date': timezone.now().isoformat(),
            'approved_by': admin_user.username if admin_user else 'system',
            'terms': {
                'commission': {
                    'rate': float(consultant_profile.commission_rate),
                    'description': f'FinAsis platformu her randevudan %{consultant_profile.commission_rate} komisyon alır.',
                    'calculation': 'Müşteri ödemesinden otomatik kesilir'
                },
                'payment': {
                    'frequency': 'monthly',
                    'description': 'Ödemeler aylık dönemler halinde mali müşavire aktarılır',
                    'minimum_payout': 500.00,
                    'currency': 'TRY'
                },
                'services': {
                    'can_offer_services': True,
                    'can_set_prices': True,
                    'instant_booking_allowed': consultant_profile.instant_booking,
                    'accepts_new_clients': consultant_profile.accepts_new_clients
                },
                'platform_rules': {
                    'must_maintain_rating': 3.0,
                    'response_time_hours': 24,
                    'cancellation_policy': 'En az 24 saat önceden bildirim',
                    'professional_conduct': True
                },
                'termination': {
                    'notice_period_days': 30,
                    'can_terminate_by_consultant': True,
                    'can_terminate_by_platform': True,
                    'breach_conditions': [
                        'Profesyonel davranış ihlali',
                        'Sahte belge',
                        'Müşteri şikayetleri (3+ ciddi)',
                        'Yasa ihlali'
                    ]
                },
                'intellectual_property': {
                    'consultant_owns_content': True,
                    'platform_can_display': True,
                    'platform_can_promote': True
                },
                'data_privacy': {
                    'gdpr_compliant': True,
                    'data_retention_years': 7,
                    'client_data_access': 'Limited to active engagements'
                }
            },
            'documents_verified': {
                'diploma': consultant_profile.diploma_verified,
                'graduation': consultant_profile.graduation_verified,
                'verified_at': consultant_profile.documents_verified_at.isoformat() if consultant_profile.documents_verified_at else None,
                'verified_by': consultant_profile.documents_verified_by.username if consultant_profile.documents_verified_by else None
            }
        }
        
        # Smart Contract oluştur
        contract = SmartContractManager.deploy_contract(
            contract_name=f'Consultant_{consultant_profile.id}',
            contract_type='consultant_agreement',
            code=json.dumps(contract_terms, indent=2),
            deployed_by=admin_user,
            parameters=contract_terms
        )
        
        # Transaction oluştur
        transaction = TransactionManager.create_transaction(
            transaction_type='contract',
            from_address='finasis_platform',
            to_address=f'consultant_{consultant_profile.id}',
            amount=0,  # Ücret yok, anlaşma kaydı
            payload={
                'action': 'create_agreement',
                'contract_address': contract.contract_address,
                'consultant_id': consultant_profile.id,
                'consultant_name': consultant_profile.display_name,
                'agreement_type': 'platform_consultant',
            },
            created_by=admin_user,
            reference_model='advisors.ConsultantProfile',
            reference_id=consultant_profile.id
        )
        
        # ConsultantProfile'ı güncelle
        consultant_profile.blockchain_contract_address = contract.contract_address
        consultant_profile.blockchain_transaction_hash = transaction.transaction_id
        consultant_profile.blockchain_contract_created_at = timezone.now()
        consultant_profile.blockchain_contract_terms = contract_terms
        consultant_profile.save(update_fields=[
            'blockchain_contract_address',
            'blockchain_transaction_hash',
            'blockchain_contract_created_at',
            'blockchain_contract_terms'
        ])
        
        return {
            'contract': contract,
            'transaction': transaction,
            'contract_address': contract.contract_address,
            'transaction_hash': transaction.transaction_id,
            'terms': contract_terms
        }
    
    @staticmethod
    def verify_consultant_agreement(consultant_profile):
        """
        Mali müşavir anlaşmasını blockchain'den doğrula
        
        Args:
            consultant_profile: ConsultantProfile instance
        
        Returns:
            dict: Doğrulama sonucu ve detaylar
        """
        if not BLOCKCHAIN_AVAILABLE:
            return {'valid': False, 'error': 'Blockchain modülü aktif değil'}
        
        if not consultant_profile.blockchain_contract_address:
            return {'valid': False, 'error': 'Blockchain anlaşması bulunamadı'}
        
        try:
            # Smart Contract'ı getir
            contract = SmartContract.objects.get(
                contract_address=consultant_profile.blockchain_contract_address
            )
            
            # Transaction'ı getir
            transaction = Transaction.objects.get(
                transaction_id=consultant_profile.blockchain_transaction_hash
            )
            
            # Doğrulama
            is_valid = (
                contract.is_active and
                transaction.status == 'confirmed'
            )
            
            return {
                'valid': is_valid,
                'contract': contract,
                'transaction': transaction,
                'contract_data': contract.parameters,
                'created_at': contract.deployed_at,
                'last_updated': contract.last_executed,
                'block_number': transaction.block.block_number if transaction.block else None
            }
        
        except (SmartContract.DoesNotExist, Transaction.DoesNotExist) as e:
            return {
                'valid': False,
                'error': f'Blockchain kaydı bulunamadı: {str(e)}'
            }
    
    @staticmethod
    def update_commission_rate(consultant_profile, new_rate, admin_user):
        """
        Komisyon oranını güncelle (yeni blockchain transaction oluşturur)
        
        Args:
            consultant_profile: ConsultantProfile instance
            new_rate: Yeni komisyon oranı (Decimal)
            admin_user: İşlemi yapan admin
        
        Returns:
            dict: Yeni transaction bilgileri
        """
        if not BLOCKCHAIN_AVAILABLE:
            raise Exception("Blockchain modülü aktif değil")
        
        old_rate = consultant_profile.commission_rate
        
        # Değişiklik transaction'ı oluştur
        transaction = TransactionManager.create_transaction(
            transaction_type='contract',
            from_address='finasis_platform',
            to_address=f'consultant_{consultant_profile.id}',
            amount=0,
            payload={
                'action': 'update_commission',
                'consultant_id': consultant_profile.id,
                'old_rate': float(old_rate),
                'new_rate': float(new_rate),
                'updated_by': admin_user.username,
                'reason': 'Commission rate adjustment',
                'effective_date': timezone.now().isoformat()
            },
            created_by=admin_user,
            reference_model='advisors.ConsultantProfile',
            reference_id=consultant_profile.id
        )
        
        # Contract güncelle
        contract = SmartContract.objects.get(
            contract_address=consultant_profile.blockchain_contract_address
        )
        
        updated_data = contract.parameters.copy()
        updated_data['commission_rate'] = float(new_rate)
        updated_data['terms']['commission']['rate'] = float(new_rate)
        updated_data['commission_history'] = updated_data.get('commission_history', [])
        updated_data['commission_history'].append({
            'date': timezone.now().isoformat(),
            'old_rate': float(old_rate),
            'new_rate': float(new_rate),
            'updated_by': admin_user.username
        })
        
        # Blockchain execution (mock - gerçek blockchain için customize edilmeli)
        SmartContractManager.execute_contract(
            contract_address=contract.contract_address,
            execution_params={
                'function_name': 'update_terms',
                'parameters': {'new_data': updated_data},
                'executed_by': admin_user.username if admin_user else 'system'
            }
        )
        
        return {
            'transaction': transaction,
            'transaction_hash': transaction.transaction_id,
            'old_rate': old_rate,
            'new_rate': new_rate
        }
    
    @staticmethod
    def terminate_agreement(consultant_profile, reason, terminated_by):
        """
        Anlaşmayı feshet (blockchain'e kaydet)
        
        Args:
            consultant_profile: ConsultantProfile instance
            reason: Fesih nedeni
            terminated_by: Feshi yapan (user instance)
        
        Returns:
            dict: Fesih transaction bilgileri
        """
        if not BLOCKCHAIN_AVAILABLE:
            raise Exception("Blockchain modülü aktif değil")
        
        # Fesih transaction'ı
        transaction = TransactionManager.create_transaction(
            transaction_type='contract',
            from_address='finasis_platform',
            to_address=f'consultant_{consultant_profile.id}',
            amount=0,
            payload={
                'action': 'terminate_agreement',
                'consultant_id': consultant_profile.id,
                'consultant_name': consultant_profile.display_name,
                'reason': reason,
                'terminated_by': terminated_by.username,
                'termination_date': timezone.now().isoformat(),
                'contract_address': consultant_profile.blockchain_contract_address
            },
            created_by=terminated_by,
            reference_model='advisors.ConsultantProfile',
            reference_id=consultant_profile.id
        )
        
        # Smart Contract'ı deaktive et
        contract = SmartContract.objects.get(
            contract_address=consultant_profile.blockchain_contract_address
        )
        contract.is_active = False
        contract.save()
        
        # Mali müşavir durumunu güncelle
        consultant_profile.approval_status = 'suspended'
        consultant_profile.save(update_fields=['approval_status'])
        
        return {
            'transaction': transaction,
            'transaction_hash': transaction.transaction_id,
            'termination_date': timezone.now()
        }
    
    @staticmethod
    def get_agreement_history(consultant_profile):
        """
        Mali müşavir anlaşma geçmişini blockchain'den getir
        
        Args:
            consultant_profile: ConsultantProfile instance
        
        Returns:
            list: Transaction geçmişi
        """
        if not BLOCKCHAIN_AVAILABLE:
            return []
        
        transactions = Transaction.objects.filter(
            reference_model='advisors.ConsultantProfile',
            reference_id=consultant_profile.id
        ).order_by('-timestamp')
        
        history = []
        for tx in transactions:
            history.append({
                'transaction_hash': tx.transaction_id,
                'type': tx.transaction_type,
                'payload': tx.payload,
                'created_at': tx.timestamp,
                'status': tx.status,
                'block_number': tx.block.block_number if tx.block else None
            })
        
        return history


# Helper fonksiyonlar
def create_agreement_on_approval(consultant_profile, admin_user):
    """
    Mali müşavir onaylandığında otomatik olarak blockchain anlaşması oluştur
    
    Usage:
        # Onay verildikten sonra
        if consultant.approval_status == 'approved':
            result = create_agreement_on_approval(consultant, request.user)
    """
    return ConsultantBlockchainService.create_consultant_agreement(
        consultant_profile,
        admin_user
    )


def verify_agreement(consultant_profile):
    """Anlaşmayı doğrula (kolaylık fonksiyonu)"""
    return ConsultantBlockchainService.verify_consultant_agreement(consultant_profile)
