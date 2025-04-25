from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class Friend:
    id: str
    username: str
    status: str
    last_online: datetime
    mutual_friends: int

@dataclass
class Clan:
    id: str
    name: str
    tag: str
    leader_id: str
    members: List[str]
    level: int
    achievements: List[str]
    description: str
    created_at: datetime

@dataclass
class ChatMessage:
    id: str
    sender_id: str
    content: str
    timestamp: datetime
    type: str  # 'global', 'clan', 'private', 'team'

class SocialSystem:
    def __init__(self):
        self.friends: Dict[str, List[Friend]] = {}
        self.clans: Dict[str, Clan] = {}
        self.chat_messages: List[ChatMessage] = []
        self.reports: Dict[str, List[Dict]] = {}
        
    def add_friend(self, player_id: str, friend_id: str) -> bool:
        """Oyuncuya arkadaş ekler"""
        if player_id not in self.friends:
            self.friends[player_id] = []
            
        if friend_id not in [f.id for f in self.friends[player_id]]:
            friend = Friend(
                id=friend_id,
                username="",  # Kullanıcı adı veritabanından alınacak
                status="offline",
                last_online=datetime.now(),
                mutual_friends=0
            )
            self.friends[player_id].append(friend)
            return True
        return False
        
    def remove_friend(self, player_id: str, friend_id: str) -> bool:
        """Oyuncudan arkadaş siler"""
        if player_id in self.friends:
            self.friends[player_id] = [
                f for f in self.friends[player_id] if f.id != friend_id
            ]
            return True
        return False
        
    def create_clan(self, leader_id: str, name: str, tag: str, description: str) -> Optional[Clan]:
        """Yeni bir klan oluşturur"""
        if not self._is_clan_name_available(name):
            return None
            
        clan = Clan(
            id=str(uuid.uuid4()),
            name=name,
            tag=tag,
            leader_id=leader_id,
            members=[leader_id],
            level=1,
            achievements=[],
            description=description,
            created_at=datetime.now()
        )
        
        self.clans[clan.id] = clan
        return clan
        
    def join_clan(self, player_id: str, clan_id: str) -> bool:
        """Oyuncuyu klana ekler"""
        if clan_id in self.clans and player_id not in self.clans[clan_id].members:
            self.clans[clan_id].members.append(player_id)
            return True
        return False
        
    def leave_clan(self, player_id: str, clan_id: str) -> bool:
        """Oyuncuyu klandan çıkarır"""
        if clan_id in self.clans and player_id in self.clans[clan_id].members:
            self.clans[clan_id].members.remove(player_id)
            return True
        return False
        
    def send_chat_message(self, sender_id: str, content: str, 
                         message_type: str, recipient_id: Optional[str] = None) -> ChatMessage:
        """Sohbet mesajı gönderir"""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            content=content,
            timestamp=datetime.now(),
            type=message_type
        )
        
        self.chat_messages.append(message)
        return message
        
    def get_clan_chat(self, clan_id: str, limit: int = 50) -> List[ChatMessage]:
        """Klan sohbetini getirir"""
        return [
            msg for msg in self.chat_messages
            if msg.type == 'clan' and msg.sender_id in self.clans[clan_id].members
        ][-limit:]
        
    def report_player(self, reporter_id: str, reported_id: str, reason: str) -> bool:
        """Oyuncu şikayetini kaydeder"""
        if reported_id not in self.reports:
            self.reports[reported_id] = []
            
        report = {
            "id": str(uuid.uuid4()),
            "reporter_id": reporter_id,
            "reason": reason,
            "timestamp": datetime.now()
        }
        
        self.reports[reported_id].append(report)
        return True
        
    def get_player_reputation(self, player_id: str) -> float:
        """Oyuncu itibarını hesaplar"""
        if player_id not in self.reports:
            return 1.0
            
        reports = self.reports[player_id]
        if not reports:
            return 1.0
            
        # Son 30 gündeki raporları say
        recent_reports = [
            r for r in reports
            if (datetime.now() - r["timestamp"]).days <= 30
        ]
        
        # İtibar puanını hesapla (1.0 = mükemmel, 0.0 = çok kötü)
        reputation = 1.0 - (len(recent_reports) * 0.1)
        return max(0.0, min(1.0, reputation))
        
    def _is_clan_name_available(self, name: str) -> bool:
        """Klan adının müsait olup olmadığını kontrol eder"""
        return not any(c.name.lower() == name.lower() for c in self.clans.values())
        
    def get_clan_leaderboard(self, limit: int = 10) -> List[Clan]:
        """Klan liderlik tablosunu getirir"""
        return sorted(
            self.clans.values(),
            key=lambda c: c.level,
            reverse=True
        )[:limit]
        
    def update_clan_level(self, clan_id: str, experience: int) -> bool:
        """Klan seviyesini günceller"""
        if clan_id in self.clans:
            clan = self.clans[clan_id]
            # Seviye atlama formülü
            new_level = int((experience / 1000) ** 0.5) + 1
            if new_level > clan.level:
                clan.level = new_level
                return True
        return False 