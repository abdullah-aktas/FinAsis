from typing import Dict, List
import random
from dataclasses import dataclass
from enum import Enum

class CurrencyType(Enum):
    COINS = "coins"
    GEMS = "gems"
    TOKENS = "tokens"

class ItemRarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Item:
    id: str
    name: str
    description: str
    rarity: ItemRarity
    value: Dict[CurrencyType, int]
    effects: Dict

class EconomySystem:
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.market_prices: Dict[str, Dict[CurrencyType, int]] = {}
        self.daily_deals: List[Item] = []
        self.seasonal_items: List[Item] = []
        
    def initialize_market(self):
        """Piyasa fiyatlarını başlatır"""
        self.update_market_prices()
        self.generate_daily_deals()
        
    def update_market_prices(self):
        """Piyasa fiyatlarını günceller"""
        # Gerçek dünya ekonomik verilerini kullanarak fiyatları güncelle
        # Rastgele dalgalanmalar ekle
        for item_id, item in self.items.items():
            base_price = item.value[CurrencyType.COINS]
            fluctuation = random.uniform(0.8, 1.2)
            self.market_prices[item_id] = {
                CurrencyType.COINS: int(base_price * fluctuation),
                CurrencyType.GEMS: int(base_price * 0.1 * fluctuation),
                CurrencyType.TOKENS: int(base_price * 0.05 * fluctuation)
            }
            
    def generate_daily_deals(self):
        """Günlük fırsatları oluşturur"""
        self.daily_deals = []
        for _ in range(5):  # Her gün 5 fırsat
            item = random.choice(list(self.items.values()))
            discount = random.uniform(0.5, 0.8)  # %20-50 indirim
            self.daily_deals.append(item)
            
    def calculate_trade_value(self, items: List[Item]) -> Dict[CurrencyType, int]:
        """Eşya takas değerini hesaplar"""
        total_value = {currency: 0 for currency in CurrencyType}
        for item in items:
            for currency, value in item.value.items():
                total_value[currency] += value
        return total_value
        
    def process_trade(self, player_items: List[Item], market_items: List[Item]) -> bool:
        """Eşya takasını işler"""
        player_value = self.calculate_trade_value(player_items)
        market_value = self.calculate_trade_value(market_items)
        
        # Takas oranlarını kontrol et
        for currency in CurrencyType:
            if player_value[currency] < market_value[currency]:
                return False
                
        return True
        
    def award_achievement_rewards(self, achievement_level: int) -> Dict[CurrencyType, int]:
        """Başarı ödüllerini hesaplar"""
        return {
            CurrencyType.COINS: 100 * achievement_level,
            CurrencyType.GEMS: 10 * achievement_level,
            CurrencyType.TOKENS: 5 * achievement_level
        }
        
    def calculate_battle_royale_rewards(self, placement: int, kills: int) -> Dict[CurrencyType, int]:
        """Battle Royale ödüllerini hesaplar"""
        placement_multiplier = (101 - placement) / 100  # 1. sıra = 1.0, 100. sıra = 0.01
        kill_bonus = kills * 10
        
        return {
            CurrencyType.COINS: int(1000 * placement_multiplier + kill_bonus),
            CurrencyType.GEMS: int(100 * placement_multiplier + kill_bonus * 0.1),
            CurrencyType.TOKENS: int(50 * placement_multiplier + kill_bonus * 0.05)
        }
        
    def generate_loot_box(self, rarity: ItemRarity) -> List[Item]:
        """Loot box içeriğini oluşturur"""
        items = []
        num_items = random.randint(1, 3)
        
        for _ in range(num_items):
            # Nadirliğe göre item seç
            available_items = [item for item in self.items.values() 
                             if item.rarity == rarity]
            if available_items:
                items.append(random.choice(available_items))
                
        return items
        
    def calculate_subscription_benefits(self, tier: str) -> Dict[CurrencyType, int]:
        """Abonelik avantajlarını hesaplar"""
        benefits = {
            "free": {
                CurrencyType.COINS: 0,
                CurrencyType.GEMS: 0,
                CurrencyType.TOKENS: 0
            },
            "premium": {
                CurrencyType.COINS: 1000,
                CurrencyType.GEMS: 100,
                CurrencyType.TOKENS: 50
            },
            "pro": {
                CurrencyType.COINS: 2500,
                CurrencyType.GEMS: 250,
                CurrencyType.TOKENS: 125
            }
        }
        return benefits.get(tier, benefits["free"]) 