"""
Blockchain-Based Audit Trail Module
Blockchain Tabanlı Değiştirilemez Denetim İzi Sistemi
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from django.utils import timezone


class AuditBlock:
    """Tek bir audit bloğu"""

    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Bloğun SHA-256 hash'ini hesapla"""
        block_string = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "data": self.data,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )

        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int = 4):
        """
        Proof of Work - Bloğu belirli zorluk seviyesinde madenciliği yap
        difficulty: Kaç tane 0 ile başlamalı (örn: 4 = '0000...')
        """
        target = "0" * difficulty

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict:
        """Bloğu dictionary'e dönüştür"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
        }


class AuditBlockchain:
    """
    Audit Trail için Blockchain İmplementasyonu
    - Değiştirilemez kayıt
    - Zincir doğrulama
    - Merkezi olmayan denetim izi
    """

    def __init__(self, difficulty: int = 4):
        self.chain: List[AuditBlock] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Dict] = []

        # Genesis block oluştur
        self.create_genesis_block()

    def create_genesis_block(self):
        """İlk bloğu (Genesis) oluştur"""
        genesis_block = AuditBlock(
            index=0,
            timestamp=timezone.now().isoformat(),
            data={
                "type": "genesis",
                "message": "FinAsis Audit Blockchain Initialized",
                "version": "1.0.0",
            },
            previous_hash="0",
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self) -> AuditBlock:
        """Zincirdeki son bloğu getir"""
        return self.chain[-1]

    def add_audit_event(self, event_data: Dict) -> AuditBlock:
        """
        Yeni audit event'i blockchain'e ekle

        Args:
            event_data: Audit event bilgileri

        Returns:
            Created AuditBlock
        """
        # Yeni blok oluştur
        new_block = AuditBlock(
            index=len(self.chain),
            timestamp=timezone.now().isoformat(),
            data=event_data,
            previous_hash=self.get_latest_block().hash,
        )

        # Bloğu madenciliği yap (Proof of Work)
        new_block.mine_block(self.difficulty)

        # Zincire ekle
        self.chain.append(new_block)

        return new_block

    def add_batch_events(self, events: List[Dict]) -> List[AuditBlock]:
        """Toplu audit event ekleme"""
        added_blocks = []

        for event in events:
            block = self.add_audit_event(event)
            added_blocks.append(block)

        return added_blocks

    def is_chain_valid(self) -> Tuple[bool, Optional[str]]:
        """
        Blockchain zincirinin bütünlüğünü doğrula

        Returns:
            (is_valid, error_message)
        """
        # Genesis bloğunu atla
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # 1. Mevcut bloğun hash'i doğru mu?
            if current_block.hash != current_block.calculate_hash():
                return False, f"Blok {i} hash'i geçersiz! Veri değiştirilmiş olabilir."

            # 2. Önceki blok hash referansı doğru mu?
            if current_block.previous_hash != previous_block.hash:
                return (
                    False,
                    f"Blok {i} zincir bağlantısı kopuk! Önceki hash uyuşmuyor.",
                )

            # 3. Proof of Work geçerli mi?
            if not current_block.hash.startswith("0" * self.difficulty):
                return False, f"Blok {i} Proof of Work geçersiz!"

        return True, None

    def get_block_by_index(self, index: int) -> Optional[AuditBlock]:
        """Index ile blok getir"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    def get_blocks_by_user(self, username: str) -> List[AuditBlock]:
        """Belirli kullanıcının tüm bloklarını getir"""
        user_blocks = []

        for block in self.chain[1:]:  # Genesis'i atla
            if block.data.get("actor_username") == username:
                user_blocks.append(block)

        return user_blocks

    def get_blocks_by_action(self, action: str) -> List[AuditBlock]:
        """Belirli aksiyon tipinin tüm bloklarını getir"""
        action_blocks = []

        for block in self.chain[1:]:
            if block.data.get("action") == action:
                action_blocks.append(block)

        return action_blocks

    def get_blocks_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[AuditBlock]:
        """Tarih aralığındaki blokları getir"""
        filtered_blocks = []

        for block in self.chain[1:]:
            block_date = datetime.fromisoformat(block.timestamp)
            if start_date <= block_date <= end_date:
                filtered_blocks.append(block)

        return filtered_blocks

    def search_blockchain(self, query: str) -> List[AuditBlock]:
        """Blockchain içinde metin arama"""
        results = []
        query_lower = query.lower()

        for block in self.chain[1:]:
            block_str = json.dumps(block.data).lower()
            if query_lower in block_str:
                results.append(block)

        return results

    def get_chain_statistics(self) -> Dict:
        """Blockchain istatistikleri"""
        if len(self.chain) <= 1:
            return {"total_blocks": 1, "total_events": 0, "chain_valid": True}

        is_valid, error = self.is_chain_valid()

        # Aksiyon tipleri
        actions = {}
        users = set()
        severities = {}

        for block in self.chain[1:]:
            data = block.data

            # Aksiyon sayıları
            action = data.get("action", "unknown")
            actions[action] = actions.get(action, 0) + 1

            # Kullanıcılar
            if data.get("actor_username"):
                users.add(data["actor_username"])

            # Ciddiyet
            severity = data.get("severity", "info")
            severities[severity] = severities.get(severity, 0) + 1

        return {
            "total_blocks": len(self.chain),
            "total_events": len(self.chain) - 1,  # Genesis hariç
            "chain_valid": is_valid,
            "validation_error": error,
            "unique_users": len(users),
            "actions": actions,
            "severities": severities,
            "difficulty": self.difficulty,
            "latest_block_hash": self.get_latest_block().hash,
        }

    def export_chain(self) -> List[Dict]:
        """Tüm zinciri export et"""
        return [block.to_dict() for block in self.chain]

    def import_chain(self, chain_data: List[Dict]) -> bool:
        """
        Zinciri import et ve doğrula

        Returns:
            Success status
        """
        try:
            # Yeni zincir oluştur
            new_chain = []

            for block_data in chain_data:
                block = AuditBlock(
                    index=block_data["index"],
                    timestamp=block_data["timestamp"],
                    data=block_data["data"],
                    previous_hash=block_data["previous_hash"],
                )
                block.hash = block_data["hash"]
                block.nonce = block_data["nonce"]
                new_chain.append(block)

            # Geçici olarak değiştir ve doğrula
            original_chain = self.chain
            self.chain = new_chain

            is_valid, error = self.is_chain_valid()

            if not is_valid:
                # Doğrulama başarısız, eski zinciri geri yükle
                self.chain = original_chain
                return False

            return True

        except Exception:
            return False

    def verify_event_integrity(self, event_id: str) -> Dict:
        """
        Belirli bir event'in bütünlüğünü doğrula

        Returns:
            Verification result with details
        """
        # Event'i bul
        target_block = None
        for block in self.chain:
            if block.data.get("id") == event_id:
                target_block = block
                break

        if not target_block:
            return {
                "verified": False,
                "reason": "Event bulunamadı",
                "event_id": event_id,
            }

        # Hash doğrulama
        calculated_hash = target_block.calculate_hash()
        hash_valid = calculated_hash == target_block.hash

        # Zincir doğrulama
        chain_valid, error = self.is_chain_valid()

        return {
            "verified": hash_valid and chain_valid,
            "event_id": event_id,
            "block_index": target_block.index,
            "hash_valid": hash_valid,
            "chain_valid": chain_valid,
            "block_hash": target_block.hash,
            "calculated_hash": calculated_hash,
            "timestamp": target_block.timestamp,
            "validation_error": error if not chain_valid else None,
            "tamper_proof": hash_valid and chain_valid,
        }


class BlockchainAuditManager:
    """
    Blockchain Audit Manager - Django modelleri ile entegrasyon
    """

    def __init__(self):
        self.blockchain = AuditBlockchain(difficulty=4)
        self._load_from_storage()

    def _load_from_storage(self):
        """
        Depodan blockchain'i yükle (cache veya database)
        Bu implementasyonda basitlik için memory'de tutuyoruz
        Production'da Redis/Database kullanılmalı
        """
        # TODO: Implement persistent storage
        pass

    def _save_to_storage(self):
        """Blockchain'i depoya kaydet"""
        # TODO: Implement persistent storage
        pass

    def add_audit_event_to_chain(self, audit_event) -> AuditBlock:
        """
        Django AuditEvent modelini blockchain'e ekle

        Args:
            audit_event: AuditEvent model instance

        Returns:
            Created AuditBlock
        """
        event_data = {
            "id": str(audit_event.id),
            "action": audit_event.action,
            "object_repr": audit_event.object_repr,
            "actor_username": audit_event.actor_username,
            "ip": audit_event.ip,
            "severity": audit_event.severity,
            "category": audit_event.category,
            "description": audit_event.description,
            "created_at": audit_event.created_at.isoformat(),
            "financial_impact": (
                float(audit_event.financial_impact)
                if audit_event.financial_impact
                else None
            ),
        }

        block = self.blockchain.add_audit_event(event_data)
        self._save_to_storage()

        return block

    def verify_audit_trail(self) -> Dict:
        """Tüm audit trail'in bütünlüğünü doğrula"""
        is_valid, error = self.blockchain.is_chain_valid()
        stats = self.blockchain.get_chain_statistics()

        return {
            "valid": is_valid,
            "error": error,
            "statistics": stats,
            "verification_timestamp": timezone.now().isoformat(),
            "trust_score": 100 if is_valid else 0,
        }

    def generate_audit_certificate(
        self, company_name: str, start_date: datetime, end_date: datetime
    ) -> Dict:
        """
        Belirli dönem için blockchain destekli audit sertifikası oluştur
        """
        blocks = self.blockchain.get_blocks_by_date_range(start_date, end_date)
        is_valid, error = self.blockchain.is_chain_valid()

        certificate = {
            "company_name": company_name,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "audit_events_count": len(blocks),
            "blockchain_verified": is_valid,
            "certificate_hash": hashlib.sha256(
                f"{company_name}{start_date}{end_date}{len(blocks)}".encode()
            ).hexdigest(),
            "issued_at": timezone.now().isoformat(),
            "verification_error": error,
            "blockchain_integrity": "VERIFIED" if is_valid else "COMPROMISED",
            "certificate_type": "BLOCKCHAIN_AUDIT_TRAIL",
            "version": "1.0",
        }

        return certificate
