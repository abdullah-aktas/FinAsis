# -*- coding: utf-8 -*-
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import datetime

class AchievementType(Enum):
    GAME_PLAY = "game_play"
    TRADING = "trading"
    SOCIAL = "social"
    COLLECTION = "collection"
    SPECIAL = "special"

class AchievementTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    type: AchievementType
    tier: AchievementTier
    progress: int
    max_progress: int
    rewards: Dict
    hidden: bool
    created_at: datetime.datetime

@dataclass
class Badge:
    id: str
    name: str
    description: str
    icon: str
    rarity: AchievementTier
    requirements: List[str]
    effects: Dict

class AchievementSystem:
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.badges: Dict[str, Badge] = {}
        self.player_progress: Dict[str, Dict[str, int]] = {}
        self.seasonal_achievements: List[Achievement] = []
        
    def initialize_achievements(self):
        """Başarı sistemini başlatır"""
        self._load_base_achievements()
        self._load_seasonal_achievements()
        self._initialize_badges()
        
    def _load_base_achievements(self):
        """Temel başarıları yükler"""
        base_achievements = [
            {
                "id": "first_trade",
                "name": "İlk Ticaret",
                "description": "İlk ticaret işlemini gerçekleştir",
                "type": AchievementType.TRADING,
                "tier": AchievementTier.BRONZE,
                "max_progress": 1,
                "rewards": {"coins": 100, "experience": 50},
                "hidden": False
            },
            {
                "id": "market_master",
                "name": "Piyasa Ustası",
                "description": "100 başarılı ticaret yap",
                "type": AchievementType.TRADING,
                "tier": AchievementTier.GOLD,
                "max_progress": 100,
                "rewards": {"coins": 1000, "experience": 500, "badge": "market_master"},
                "hidden": False
            },
            # Diğer başarılar...
        ]
        
        for achievement in base_achievements:
            self.achievements[achievement["id"]] = Achievement(
                **achievement,
                progress=0,
                created_at=datetime.datetime.now()
            )
            
    def _load_seasonal_achievements(self):
        """Sezonluk başarıları yükler"""
        current_season = self._get_current_season()
        seasonal_achievements = [
            {
                "id": f"season_{current_season}_trader",
                "name": f"Sezon {current_season} Tüccarı",
                "description": f"Sezon {current_season}'da 50 başarılı ticaret yap",
                "type": AchievementType.SPECIAL,
                "tier": AchievementTier.SILVER,
                "max_progress": 50,
                "rewards": {"coins": 500, "experience": 250, "season_points": 100},
                "hidden": False
            }
            # Diğer sezonluk başarılar...
        ]
        
        self.seasonal_achievements = [
            Achievement(**achievement, progress=0, created_at=datetime.datetime.now())
            for achievement in seasonal_achievements
        ]
        
    def _initialize_badges(self):
        """Rozetleri başlatır"""
        badges = [
            {
                "id": "market_master",
                "name": "Piyasa Ustası",
                "description": "100 başarılı ticaret yaparak kazanıldı",
                "icon": "badges/market_master.png",
                "rarity": AchievementTier.GOLD,
                "requirements": ["market_master_achievement"],
                "effects": {"trade_bonus": 0.05}  # %5 ticaret bonusu
            },
            # Diğer rozetler...
        ]
        
        for badge in badges:
            self.badges[badge["id"]] = Badge(**badge)
            
    def update_progress(self, player_id: str, achievement_id: str, progress: int = 1):
        """Başarı ilerlemesini günceller"""
        if player_id not in self.player_progress:
            self.player_progress[player_id] = {}
            
        current_progress = self.player_progress[player_id].get(achievement_id, 0)
        new_progress = min(current_progress + progress, 
                         self.achievements[achievement_id].max_progress)
        
        self.player_progress[player_id][achievement_id] = new_progress
        
        if new_progress >= self.achievements[achievement_id].max_progress:
            self._award_achievement(player_id, achievement_id)
            
    def _award_achievement(self, player_id: str, achievement_id: str):
        """Başarı ödüllerini dağıtır"""
        achievement = self.achievements[achievement_id]
        rewards = achievement.rewards
        
        # Ödülleri dağıt
        self._distribute_rewards(player_id, rewards)
        
        # Rozet kontrolü
        if "badge" in rewards:
            self._award_badge(player_id, rewards["badge"])
            
    def _distribute_rewards(self, player_id: str, rewards: Dict):
        """Ödülleri oyuncuya dağıtır"""
        # Ödül dağıtım mantığı
        pass
        
    def _award_badge(self, player_id: str, badge_id: str):
        """Rozeti oyuncuya verir"""
        badge = self.badges[badge_id]
        # Rozet verme mantığı
        pass
        
    def get_player_achievements(self, player_id: str) -> List[Achievement]:
        """Oyuncunun başarılarını getirir"""
        player_progress = self.player_progress.get(player_id, {})
        achievements = []
        
        for achievement_id, progress in player_progress.items():
            if achievement_id in self.achievements:
                achievement = self.achievements[achievement_id]
                achievement.progress = progress
                achievements.append(achievement)
                
        return achievements
        
    def get_player_badges(self, player_id: str) -> List[Badge]:
        """Oyuncunun rozetlerini getirir"""
        # Rozet getirme mantığı
        pass
        
    def _get_current_season(self) -> int:
        """Mevcut sezonu hesaplar"""
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        return (year - 2023) * 12 + month 