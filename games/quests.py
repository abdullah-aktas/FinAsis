# -*- coding: utf-8 -*-
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

class QuestType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SEASONAL = "seasonal"
    SPECIAL = "special"

class QuestStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class Quest:
    id: str
    title: str
    description: str
    type: QuestType
    requirements: Dict
    rewards: Dict
    start_time: datetime
    end_time: datetime
    status: QuestStatus
    progress: Dict

@dataclass
class Event:
    id: str
    name: str
    description: str
    start_time: datetime
    end_time: datetime
    rewards: Dict
    special_rules: Dict
    participants: List[str]

class QuestSystem:
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.events: Dict[str, Event] = {}
        self.player_quests: Dict[str, List[Quest]] = {}
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0)
        
    def initialize_quests(self):
        """Görev sistemini başlatır"""
        self._generate_daily_quests()
        self._generate_weekly_quests()
        self._load_seasonal_quests()
        
    def _generate_daily_quests(self):
        """Günlük görevleri oluşturur"""
        daily_quests = [
            {
                "id": "daily_trade_1",
                "title": "Günlük Ticaret",
                "description": "5 başarılı ticaret yap",
                "type": QuestType.DAILY,
                "requirements": {"trades": 5},
                "rewards": {"coins": 100, "experience": 50},
                "start_time": self.daily_reset_time,
                "end_time": self.daily_reset_time + timedelta(days=1),
                "status": QuestStatus.ACTIVE,
                "progress": {"trades": 0}
            },
            {
                "id": "daily_profit_1",
                "title": "Günlük Kar",
                "description": "1000 coin kar elde et",
                "type": QuestType.DAILY,
                "requirements": {"profit": 1000},
                "rewards": {"coins": 200, "experience": 100},
                "start_time": self.daily_reset_time,
                "end_time": self.daily_reset_time + timedelta(days=1),
                "status": QuestStatus.ACTIVE,
                "progress": {"profit": 0}
            }
        ]
        
        for quest in daily_quests:
            self.quests[quest["id"]] = Quest(**quest)
            
    def _generate_weekly_quests(self):
        """Haftalık görevleri oluşturur"""
        weekly_quests = [
            {
                "id": "weekly_trade_1",
                "title": "Haftalık Ticaret",
                "description": "25 başarılı ticaret yap",
                "type": QuestType.WEEKLY,
                "requirements": {"trades": 25},
                "rewards": {"coins": 500, "experience": 250, "weekly_points": 100},
                "start_time": self.daily_reset_time,
                "end_time": self.daily_reset_time + timedelta(days=7),
                "status": QuestStatus.ACTIVE,
                "progress": {"trades": 0}
            }
        ]
        
        for quest in weekly_quests:
            self.quests[quest["id"]] = Quest(**quest)
            
    def _load_seasonal_quests(self):
        """Sezonluk görevleri yükler"""
        current_season = self._get_current_season()
        seasonal_quests = [
            {
                "id": f"seasonal_{current_season}_master",
                "title": f"Sezon {current_season} Ustası",
                "description": f"Sezon {current_season}'da 100 başarılı ticaret yap",
                "type": QuestType.SEASONAL,
                "requirements": {"trades": 100},
                "rewards": {"coins": 1000, "experience": 500, "season_points": 200},
                "start_time": self._get_season_start(),
                "end_time": self._get_season_end(),
                "status": QuestStatus.ACTIVE,
                "progress": {"trades": 0}
            }
        ]
        
        for quest in seasonal_quests:
            self.quests[quest["id"]] = Quest(**quest)
            
    def update_quest_progress(self, player_id: str, quest_id: str, progress: Dict):
        """Görev ilerlemesini günceller"""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            
            # İlerlemeyi güncelle
            for key, value in progress.items():
                if key in quest.progress:
                    quest.progress[key] += value
                    
            # Görev tamamlandı mı kontrol et
            if self._is_quest_completed(quest):
                self._complete_quest(player_id, quest)
                
    def _is_quest_completed(self, quest: Quest) -> bool:
        """Görevin tamamlanıp tamamlanmadığını kontrol eder"""
        for requirement, target in quest.requirements.items():
            if quest.progress.get(requirement, 0) < target:
                return False
        return True
        
    def _complete_quest(self, player_id: str, quest: Quest):
        """Görevi tamamlar ve ödülleri dağıtır"""
        quest.status = QuestStatus.COMPLETED
        self._distribute_rewards(player_id, quest.rewards)
        
    def _distribute_rewards(self, player_id: str, rewards: Dict):
        """Görev ödüllerini dağıtır"""
        # Ödül dağıtım mantığı
        pass
        
    def create_event(self, name: str, description: str, duration: int,
                    rewards: Dict, special_rules: Dict) -> Event:
        """Yeni bir etkinlik oluşturur"""
        event = Event(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=duration),
            rewards=rewards,
            special_rules=special_rules,
            participants=[]
        )
        
        self.events[event.id] = event
        return event
        
    def join_event(self, player_id: str, event_id: str) -> bool:
        """Oyuncuyu etkinliğe ekler"""
        if event_id in self.events:
            event = self.events[event_id]
            if player_id not in event.participants:
                event.participants.append(player_id)
                return True
        return False
        
    def _get_current_season(self) -> int:
        """Mevcut sezonu hesaplar"""
        now = datetime.now()
        year = now.year
        month = now.month
        return (year - 2023) * 12 + month
        
    def _get_season_start(self) -> datetime:
        """Sezon başlangıç zamanını hesaplar"""
        now = datetime.now()
        return now.replace(day=1, hour=0, minute=0, second=0)
        
    def _get_season_end(self) -> datetime:
        """Sezon bitiş zamanını hesaplar"""
        start = self._get_season_start()
        if start.month == 12:
            return start.replace(year=start.year + 1, month=1)
        return start.replace(month=start.month + 1) 