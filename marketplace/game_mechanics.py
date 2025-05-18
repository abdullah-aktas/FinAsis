from typing import Dict, List
import numpy as np
import random
from datetime import datetime

class GameMechanics:
    def __init__(self):
        self.xp_multipliers = {
            "daily_streak": 1.5,
            "team_bonus": 1.2,
            "weekend_bonus": 2.0
        }
        self.prestige_levels = {
            0: "Yeni Başlayan",
            1: "Acemi Tüccar",
            2: "Tecrübeli Tüccar",
            3: "Uzman Tüccar",
            4: "Efsanevi Tüccar",
            5: "Finans Lordu"
        }
        
    def calculate_rewards(self, 
                         activity_type: str,
                         difficulty: int,
                         time_spent: int,
                         streak_days: int) -> Dict[str, float]:
        """Oyuncu ödüllerini hesapla"""
        base_reward = {
            "trading": 50,
            "learning": 30,
            "teaching": 100,
            "creating": 150
        }.get(activity_type, 20)
        
        # Temel XP hesaplama
        xp = base_reward * difficulty * (time_spent / 60)
        
        # Çarpanları uygula
        if streak_days > 0:
            xp *= self.xp_multipliers["daily_streak"]
        
        if datetime.now().weekday() in [5, 6]:  # Hafta sonu
            xp *= self.xp_multipliers["weekend_bonus"]
            
        # FinCoin hesaplama
        fincoin = xp / 10
        
        return {
            "xp": round(xp),
            "fincoin": round(fincoin),
            "skill_points": round(xp / 100)
        }
        
    def generate_daily_challenges(self) -> List[Dict]:
        """Günlük görevler oluştur"""
        challenges = [
            {
                "title": "Borsa Ustası",
                "description": "Bir günde 10 başarılı trade yap",
                "reward": {"fincoin": 500, "xp": 1000}
            },
            {
                "title": "Öğretmen Ruhu",
                "description": "3 kişiye mentorluk yap",
                "reward": {"fincoin": 300, "xp": 800}
            },
            {
                "title": "İçerik Üreticisi",
                "description": "Yeni bir eğitim içeriği yayınla",
                "reward": {"fincoin": 1000, "xp": 2000}
            }
        ]
        return random.sample(challenges, 3)  # Günde 3 rastgele görev

    def calculate_trade_power(self, player_stats: Dict) -> float:
        """Ticaret gücünü hesapla"""
        base_power = 1.0
        
        # Başarılar bonus verir
        achievement_bonus = len(player_stats.get('achievements', [])) * 0.05
        
        # Win streak bonus
        streak_bonus = min(player_stats.get('win_streak', 0) * 0.02, 0.5)
        
        # Prestij seviyesi bonus
        prestige_bonus = player_stats.get('prestige_level', 0) * 0.1
        
        return base_power + achievement_bonus + streak_bonus + prestige_bonus
        
    def generate_daily_challenge(self) -> Dict:
        """Günlük görev oluştur"""
        challenges = [
            {
                "type": "TRADING",
                "title": "Borsa Kralı",
                "target": random.randint(5, 15),
                "reward": {
                    "xp": 1000,
                    "fincoin": 500,
                    "trading_power_boost": 0.1
                }
            },
            {
                "type": "MENTOR",
                "title": "Bilge Tüccar",
                "target": random.randint(2, 5),
                "reward": {
                    "xp": 800,
                    "fincoin": 400,
                    "mentor_rating_boost": 0.1
                }
            }
        ]
        return random.choice(challenges)
        
    def calculate_tournament_rewards(self, 
                                   position: int, 
                                   participants: int,
                                   prize_pool: float) -> Dict:
        """Turnuva ödüllerini hesapla"""
        if position == 1:
            share = 0.5  # %50
        elif position == 2:
            share = 0.3  # %30
        elif position == 3:
            share = 0.15  # %15
        else:
            share = 0.05  # %5
            
        return {
            "prize_money": prize_pool * share,
            "ranking_points": (participants - position + 1) * 10,
            "prestige_points": (4 - position) if position <= 3 else 0
        }
