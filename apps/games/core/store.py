from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid
from enum import Enum

class ItemCategory(Enum):
    COSMETIC = "cosmetic"
    BOOST = "boost"
    CURRENCY = "currency"
    BUNDLE = "bundle"
    SUBSCRIPTION = "subscription"

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    GOOGLE_PAY = "google_pay"
    APPLE_PAY = "apple_pay"
    IN_GAME_CURRENCY = "in_game_currency"

@dataclass
class StoreItem:
    id: str
    name: str
    description: str
    category: ItemCategory
    price: Dict[str, float]  # Para birimi -> fiyat
    stock: Optional[int]
    start_date: datetime
    end_date: Optional[datetime]
    requirements: Dict
    effects: Dict

@dataclass
class Transaction:
    id: str
    player_id: str
    item_id: str
    payment_method: PaymentMethod
    amount: float
    currency: str
    status: str
    timestamp: datetime
    receipt: Dict

class StoreSystem:
    def __init__(self):
        self.items: Dict[str, StoreItem] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.featured_items: List[StoreItem] = []
        self.daily_deals: List[StoreItem] = []
        
    def initialize_store(self):
        """Mağaza sistemini başlatır"""
        self._load_store_items()
        self._update_featured_items()
        self._generate_daily_deals()
        
    def _load_store_items(self):
        """Mağaza ürünlerini yükler"""
        store_items = [
            {
                "id": "premium_subscription",
                "name": "Premium Abonelik",
                "description": "30 günlük premium abonelik",
                "category": ItemCategory.SUBSCRIPTION,
                "price": {"USD": 9.99, "EUR": 8.99, "TRY": 199.99},
                "stock": None,
                "start_date": datetime.now(),
                "end_date": None,
                "requirements": {},
                "effects": {"subscription_tier": "premium"}
            },
            {
                "id": "pro_subscription",
                "name": "Pro Abonelik",
                "description": "30 günlük pro abonelik",
                "category": ItemCategory.SUBSCRIPTION,
                "price": {"USD": 19.99, "EUR": 17.99, "TRY": 399.99},
                "stock": None,
                "start_date": datetime.now(),
                "end_date": None,
                "requirements": {},
                "effects": {"subscription_tier": "pro"}
            },
            {
                "id": "coin_pack_1",
                "name": "Coin Paketi (1000)",
                "description": "1000 coin",
                "category": ItemCategory.CURRENCY,
                "price": {"USD": 4.99, "EUR": 4.49, "TRY": 99.99},
                "stock": None,
                "start_date": datetime.now(),
                "end_date": None,
                "requirements": {},
                "effects": {"coins": 1000}
            }
        ]
        
        for item in store_items:
            self.items[item["id"]] = StoreItem(**item)
            
    def _update_featured_items(self):
        """Öne çıkan ürünleri günceller"""
        self.featured_items = [
            item for item in self.items.values()
            if item.category != ItemCategory.SUBSCRIPTION
        ][:5]  # İlk 5 ürün
        
    def _generate_daily_deals(self):
        """Günlük fırsatları oluşturur"""
        available_items = [
            item for item in self.items.values()
            if item.category != ItemCategory.SUBSCRIPTION
        ]
        
        self.daily_deals = random.sample(available_items, min(3, len(available_items)))
        
    def process_purchase(self, player_id: str, item_id: str,
                        payment_method: PaymentMethod) -> Optional[Transaction]:
        """Satın alma işlemini gerçekleştirir"""
        if item_id not in self.items:
            return None
            
        item = self.items[item_id]
        
        # Stok kontrolü
        if item.stock is not None and item.stock <= 0:
            return None
            
        # Gereksinimleri kontrol et
        if not self._check_requirements(player_id, item.requirements):
            return None
            
        # Ödeme işlemini gerçekleştir
        transaction = self._process_payment(player_id, item, payment_method)
        
        if transaction and transaction.status == "completed":
            # Stok güncelle
            if item.stock is not None:
                item.stock -= 1
                
            # Öğe efektlerini uygula
            self._apply_item_effects(player_id, item.effects)
            
        return transaction
        
    def _check_requirements(self, player_id: str, requirements: Dict) -> bool:
        """Gereksinimleri kontrol eder"""
        # Gereksinim kontrol mantığı
        return True
        
    def _process_payment(self, player_id: str, item: StoreItem,
                        payment_method: PaymentMethod) -> Transaction:
        """Ödeme işlemini gerçekleştirir"""
        # Ödeme işlemi mantığı
        transaction = Transaction(
            id=str(uuid.uuid4()),
            player_id=player_id,
            item_id=item.id,
            payment_method=payment_method,
            amount=item.price["USD"],  # Varsayılan para birimi
            currency="USD",
            status="completed",
            timestamp=datetime.now(),
            receipt={}
        )
        
        self.transactions[transaction.id] = transaction
        return transaction
        
    def _apply_item_effects(self, player_id: str, effects: Dict):
        """Öğe efektlerini uygular"""
        # Efekt uygulama mantığı
        pass
        
    def get_player_transactions(self, player_id: str) -> List[Transaction]:
        """Oyuncunun işlem geçmişini getirir"""
        return [
            transaction for transaction in self.transactions.values()
            if transaction.player_id == player_id
        ]
        
    def refund_transaction(self, transaction_id: str) -> bool:
        """İşlem iadesini gerçekleştirir"""
        if transaction_id in self.transactions:
            transaction = self.transactions[transaction_id]
            
            # İade işlemi mantığı
            transaction.status = "refunded"
            return True
            
        return False 