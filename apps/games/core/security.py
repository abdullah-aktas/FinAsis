from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import base64
import json
from enum import Enum

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CheatType(Enum):
    SPEED_HACK = "speed_hack"
    WALL_HACK = "wall_hack"
    AIMBOT = "aimbot"
    INVENTORY_HACK = "inventory_hack"
    CURRENCY_HACK = "currency_hack"

@dataclass
class SecurityEvent:
    id: str
    type: CheatType
    player_id: str
    timestamp: datetime
    severity: SecurityLevel
    details: Dict
    action_taken: str

@dataclass
class PlayerSecurityProfile:
    player_id: str
    risk_score: float
    last_scan: datetime
    violations: List[SecurityEvent]
    whitelisted: bool

class SecuritySystem:
    def __init__(self):
        self.security_events: List[SecurityEvent] = []
        self.player_profiles: Dict[str, PlayerSecurityProfile] = {}
        self.whitelist: List[str] = []
        self.blacklist: List[str] = []
        self.encryption_key: bytes = self._generate_encryption_key()
        
    def _generate_encryption_key(self) -> bytes:
        """Şifreleme anahtarı oluştur"""
        return hashlib.sha256(b"game_security_key").digest()
        
    def initialize_player_security(self, player_id: str):
        """Oyuncu güvenlik profilini başlat"""
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = PlayerSecurityProfile(
                player_id=player_id,
                risk_score=0.0,
                last_scan=datetime.now(),
                violations=[],
                whitelisted=player_id in self.whitelist
            )
            
    def scan_player(self, player_id: str, game_data: Dict) -> bool:
        """Oyuncuyu tarar ve hile kontrolü yapar"""
        if player_id not in self.player_profiles:
            return False
            
        profile = self.player_profiles[player_id]
        
        # Hile tespiti
        cheat_detected = self._detect_cheats(player_id, game_data)
        
        if cheat_detected:
            self._handle_cheat_detection(player_id, cheat_detected)
            return False
            
        # Risk skoru güncelle
        self._update_risk_score(player_id)
        
        return True
        
    def _detect_cheats(self, player_id: str, game_data: Dict) -> Optional[CheatType]:
        """Hile tespiti yapar"""
        # Hız hilesi kontrolü
        if self._check_speed_hack(game_data):
            return CheatType.SPEED_HACK
            
        # Duvar hilesi kontrolü
        if self._check_wall_hack(game_data):
            return CheatType.WALL_HACK
            
        # Aimbot kontrolü
        if self._check_aimbot(game_data):
            return CheatType.AIMBOT
            
        # Envanter hilesi kontrolü
        if self._check_inventory_hack(game_data):
            return CheatType.INVENTORY_HACK
            
        # Para hilesi kontrolü
        if self._check_currency_hack(game_data):
            return CheatType.CURRENCY_HACK
            
        return None
        
    def _check_speed_hack(self, game_data: Dict) -> bool:
        """Hız hilesi kontrolü"""
        # Hız limiti kontrolü
        max_speed = 10.0  # Örnek hız limiti
        current_speed = game_data.get("speed", 0.0)
        return current_speed > max_speed
        
    def _check_wall_hack(self, game_data: Dict) -> bool:
        """Duvar hilesi kontrolü"""
        # Görünmezlik ve duvar geçme kontrolü
        return game_data.get("wall_collision", True) is False
        
    def _check_aimbot(self, game_data: Dict) -> bool:
        """Aimbot kontrolü"""
        # Hedef vuruş oranı kontrolü
        hit_rate = game_data.get("hit_rate", 0.0)
        return hit_rate > 0.95  # %95'ten yüksek isabet oranı
        
    def _check_inventory_hack(self, game_data: Dict) -> bool:
        """Envanter hilesi kontrolü"""
        # Envanter limiti kontrolü
        max_items = 100  # Örnek limit
        current_items = len(game_data.get("inventory", []))
        return current_items > max_items
        
    def _check_currency_hack(self, game_data: Dict) -> bool:
        """Para hilesi kontrolü"""
        # Para değişim hızı kontrolü
        currency_change = game_data.get("currency_change", 0)
        return currency_change > 10000  # Örnek limit
        
    def _handle_cheat_detection(self, player_id: str, cheat_type: CheatType):
        """Hile tespiti durumunda işlem yapar"""
        severity = self._get_cheat_severity(cheat_type)
        
        event = SecurityEvent(
            id=str(uuid.uuid4()),
            type=cheat_type,
            player_id=player_id,
            timestamp=datetime.now(),
            severity=severity,
            details={"detected_cheat": cheat_type.value},
            action_taken=self._determine_action(severity)
        )
        
        self.security_events.append(event)
        
        # Oyuncu profilini güncelle
        if player_id in self.player_profiles:
            profile = self.player_profiles[player_id]
            profile.violations.append(event)
            profile.risk_score = min(1.0, profile.risk_score + 0.2)
            
    def _get_cheat_severity(self, cheat_type: CheatType) -> SecurityLevel:
        """Hile tipine göre önem seviyesi belirler"""
        severity_map = {
            CheatType.SPEED_HACK: SecurityLevel.MEDIUM,
            CheatType.WALL_HACK: SecurityLevel.HIGH,
            CheatType.AIMBOT: SecurityLevel.HIGH,
            CheatType.INVENTORY_HACK: SecurityLevel.CRITICAL,
            CheatType.CURRENCY_HACK: SecurityLevel.CRITICAL
        }
        return severity_map.get(cheat_type, SecurityLevel.MEDIUM)
        
    def _determine_action(self, severity: SecurityLevel) -> str:
        """Önem seviyesine göre aksiyon belirler"""
        action_map = {
            SecurityLevel.LOW: "warning",
            SecurityLevel.MEDIUM: "temp_ban_1d",
            SecurityLevel.HIGH: "temp_ban_7d",
            SecurityLevel.CRITICAL: "permanent_ban"
        }
        return action_map.get(severity, "warning")
        
    def _update_risk_score(self, player_id: str):
        """Risk skorunu günceller"""
        if player_id in self.player_profiles:
            profile = self.player_profiles[player_id]
            
            # Zamanla risk skorunu azalt
            time_diff = (datetime.now() - profile.last_scan).days
            decay_factor = 0.1 * time_diff
            profile.risk_score = max(0.0, profile.risk_score - decay_factor)
            
            profile.last_scan = datetime.now()
            
    def encrypt_data(self, data: Dict) -> str:
        """Veriyi şifreler"""
        json_data = json.dumps(data)
        hmac_obj = hmac.new(self.encryption_key, json_data.encode(), hashlib.sha256)
        signature = hmac_obj.digest()
        return base64.b64encode(signature + json_data.encode()).decode()
        
    def decrypt_data(self, encrypted_data: str) -> Optional[Dict]:
        """Şifrelenmiş veriyi çözer"""
        try:
            decoded_data = base64.b64decode(encrypted_data)
            signature = decoded_data[:32]
            json_data = decoded_data[32:]
            
            hmac_obj = hmac.new(self.encryption_key, json_data, hashlib.sha256)
            if hmac.compare_digest(hmac_obj.digest(), signature):
                return json.loads(json_data.decode())
        except:
            pass
        return None
        
    def get_player_security_report(self, player_id: str) -> Dict:
        """Oyuncu güvenlik raporunu getirir"""
        if player_id in self.player_profiles:
            profile = self.player_profiles[player_id]
            return {
                "player_id": player_id,
                "risk_score": profile.risk_score,
                "violations": len(profile.violations),
                "last_scan": profile.last_scan,
                "whitelisted": profile.whitelisted
            }
        return {} 