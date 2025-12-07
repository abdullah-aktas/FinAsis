"""
TradeSim Zorluk Sistemi - E-Spor Seviyesi
Her seviyede farklı meydan okumalar ve AI davranışları
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional


class DifficultyLevel(Enum):
    """Zorluk seviyeleri"""

    BEGINNER = 1  # Yeni başlayanlar - Öğretici mod
    EASY = 2  # Kolay - Rahat oyun
    NORMAL = 3  # Normal - Dengeli
    HARD = 4  # Zor - Meydan okuyucu
    EXPERT = 5  # Uzman - Profesyoneller için
    MASTER = 6  # Usta - E-spor seviyesi
    GRANDMASTER = 7  # Büyük Usta - Aşırı zor
    CHALLENGER = 8  # Meydan Okuyan - İmkansız gibi


@dataclass
class DifficultyConfig:
    """Her zorluk seviyesi için yapılandırma"""

    level: DifficultyLevel
    name: str
    description: str

    # AI Rakip Özellikleri
    ai_count: int  # AI rakip sayısı
    ai_intelligence: float  # 0.0 - 1.0 (karar verme kalitesi)
    ai_reaction_time: float  # saniye (pazar değişimlerine tepki süresi)
    ai_starting_capital: int  # AI başlangıç sermayesi

    # Pazar Dinamikleri
    price_volatility: float  # 0.0 - 1.0 (fiyat dalgalanması)
    demand_fluctuation: float  # 0.0 - 1.0 (talep değişim hızı)
    supply_scarcity: float  # 0.0 - 1.0 (ürün kıtlığı olasılığı)

    # Random Eventler
    event_frequency: float  # 0.0 - 1.0 (kriz, fırsat olasılığı)
    event_severity: float  # 0.0 - 1.0 (event'lerin etkisi)

    # Oyun Mekanikleri
    transport_cost_multiplier: float  # Taşıma maliyeti çarpanı
    tax_rate: float  # Vergi oranı
    inflation_rate: float  # Enflasyon oranı (aylık)
    interest_rate: float  # Kredi faiz oranı

    # Zaman ve Hedefler
    time_limit_minutes: int  # Oyun süresi
    victory_condition_multiplier: float  # Hedef sermaye çarpanı

    # Ödüller
    xp_multiplier: float  # XP çarpanı
    coin_multiplier: float  # Altın çarpanı
    elo_gain_multiplier: float  # ELO kazancı çarpanı


# Zorluk yapılandırmaları
DIFFICULTY_CONFIGS = {
    DifficultyLevel.BEGINNER: DifficultyConfig(
        level=DifficultyLevel.BEGINNER,
        name="Acemi",
        description="Öğretici modda ticaretin temellerini öğren. Yardımcılar ve ipuçları aktif.",
        ai_count=1,
        ai_intelligence=0.2,
        ai_reaction_time=10.0,
        ai_starting_capital=5000,
        price_volatility=0.1,
        demand_fluctuation=0.1,
        supply_scarcity=0.05,
        event_frequency=0.05,
        event_severity=0.2,
        transport_cost_multiplier=0.5,
        tax_rate=0.05,
        inflation_rate=0.01,
        interest_rate=0.05,
        time_limit_minutes=30,
        victory_condition_multiplier=1.5,
        xp_multiplier=1.0,
        coin_multiplier=1.0,
        elo_gain_multiplier=0.5,
    ),
    DifficultyLevel.EASY: DifficultyConfig(
        level=DifficultyLevel.EASY,
        name="Kolay",
        description="Rahat tempo, düşük rekabet. Günlük oyun için ideal.",
        ai_count=2,
        ai_intelligence=0.35,
        ai_reaction_time=7.0,
        ai_starting_capital=8000,
        price_volatility=0.15,
        demand_fluctuation=0.15,
        supply_scarcity=0.1,
        event_frequency=0.1,
        event_severity=0.3,
        transport_cost_multiplier=0.75,
        tax_rate=0.08,
        inflation_rate=0.02,
        interest_rate=0.08,
        time_limit_minutes=25,
        victory_condition_multiplier=2.0,
        xp_multiplier=1.2,
        coin_multiplier=1.1,
        elo_gain_multiplier=0.75,
    ),
    DifficultyLevel.NORMAL: DifficultyConfig(
        level=DifficultyLevel.NORMAL,
        name="Normal",
        description="Dengeli oyun deneyimi. Orta seviye strateji gerektirir.",
        ai_count=3,
        ai_intelligence=0.5,
        ai_reaction_time=5.0,
        ai_starting_capital=10000,
        price_volatility=0.25,
        demand_fluctuation=0.25,
        supply_scarcity=0.15,
        event_frequency=0.2,
        event_severity=0.5,
        transport_cost_multiplier=1.0,
        tax_rate=0.10,
        inflation_rate=0.03,
        interest_rate=0.10,
        time_limit_minutes=20,
        victory_condition_multiplier=2.5,
        xp_multiplier=1.5,
        coin_multiplier=1.3,
        elo_gain_multiplier=1.0,
    ),
    DifficultyLevel.HARD: DifficultyConfig(
        level=DifficultyLevel.HARD,
        name="Zor",
        description="Agresif AI rakipler ve belirsiz pazar koşulları. İyi strateji şart.",
        ai_count=4,
        ai_intelligence=0.65,
        ai_reaction_time=3.0,
        ai_starting_capital=12000,
        price_volatility=0.35,
        demand_fluctuation=0.35,
        supply_scarcity=0.25,
        event_frequency=0.3,
        event_severity=0.7,
        transport_cost_multiplier=1.25,
        tax_rate=0.15,
        inflation_rate=0.05,
        interest_rate=0.15,
        time_limit_minutes=18,
        victory_condition_multiplier=3.0,
        xp_multiplier=2.0,
        coin_multiplier=1.6,
        elo_gain_multiplier=1.5,
    ),
    DifficultyLevel.EXPERT: DifficultyConfig(
        level=DifficultyLevel.EXPERT,
        name="Uzman",
        description="Çok agresif AI, sık krizler, yüksek vergi. Uzmanlar için.",
        ai_count=5,
        ai_intelligence=0.75,
        ai_reaction_time=2.0,
        ai_starting_capital=15000,
        price_volatility=0.45,
        demand_fluctuation=0.45,
        supply_scarcity=0.35,
        event_frequency=0.4,
        event_severity=0.85,
        transport_cost_multiplier=1.5,
        tax_rate=0.18,
        inflation_rate=0.07,
        interest_rate=0.18,
        time_limit_minutes=15,
        victory_condition_multiplier=3.5,
        xp_multiplier=2.5,
        coin_multiplier=2.0,
        elo_gain_multiplier=2.0,
    ),
    DifficultyLevel.MASTER: DifficultyConfig(
        level=DifficultyLevel.MASTER,
        name="Usta",
        description="E-spor seviyesi. Neredeyse mükemmel AI, ekonomik krizler, çok yüksek vergi.",
        ai_count=6,
        ai_intelligence=0.85,
        ai_reaction_time=1.0,
        ai_starting_capital=18000,
        price_volatility=0.55,
        demand_fluctuation=0.55,
        supply_scarcity=0.45,
        event_frequency=0.5,
        event_severity=1.0,
        transport_cost_multiplier=1.75,
        tax_rate=0.22,
        inflation_rate=0.10,
        interest_rate=0.22,
        time_limit_minutes=12,
        victory_condition_multiplier=4.0,
        xp_multiplier=3.0,
        coin_multiplier=2.5,
        elo_gain_multiplier=2.5,
    ),
    DifficultyLevel.GRANDMASTER: DifficultyConfig(
        level=DifficultyLevel.GRANDMASTER,
        name="Büyük Usta",
        description="Aşırı zor! Kusursuz AI, sürekli krizler, manipülasyonlar. Profesyoneller için.",
        ai_count=7,
        ai_intelligence=0.92,
        ai_reaction_time=0.5,
        ai_starting_capital=20000,
        price_volatility=0.65,
        demand_fluctuation=0.65,
        supply_scarcity=0.55,
        event_frequency=0.6,
        event_severity=1.2,
        transport_cost_multiplier=2.0,
        tax_rate=0.25,
        inflation_rate=0.12,
        interest_rate=0.25,
        time_limit_minutes=10,
        victory_condition_multiplier=5.0,
        xp_multiplier=4.0,
        coin_multiplier=3.0,
        elo_gain_multiplier=3.0,
    ),
    DifficultyLevel.CHALLENGER: DifficultyConfig(
        level=DifficultyLevel.CHALLENGER,
        name="Efsane Meydan Okuyucu",
        description="İMKANSIZ! Hiper-akıllı AI, kaos seviyesi ekonomi, sürekli krizler. Sadece şampiyonlar için.",
        ai_count=9,
        ai_intelligence=0.98,
        ai_reaction_time=0.3,
        ai_starting_capital=25000,
        price_volatility=0.80,
        demand_fluctuation=0.80,
        supply_scarcity=0.70,
        event_frequency=0.8,
        event_severity=1.5,
        transport_cost_multiplier=2.5,
        tax_rate=0.30,
        inflation_rate=0.15,
        interest_rate=0.30,
        time_limit_minutes=8,
        victory_condition_multiplier=6.0,
        xp_multiplier=5.0,
        coin_multiplier=4.0,
        elo_gain_multiplier=4.0,
    ),
}


class RandomEventSystem:
    """Random event sistemi - zorluk artırıcı"""

    @staticmethod
    def generate_event(difficulty_config: DifficultyConfig) -> Optional[Dict]:
        """Zorluk seviyesine göre random event oluştur"""
        if random.random() > difficulty_config.event_frequency:
            return None

        severity = difficulty_config.event_severity

        events = [
            # Ekonomik Krizler
            {
                "type": "economic_crisis",
                "name": "Ekonomik Kriz",
                "description": "Tüm şehirlerde talep %{amount} düştü!",
                "effect": {"demand_multiplier": max(0.3, 1.0 - (0.4 * severity))},
                "duration_turns": int(3 + (3 * severity)),
                "severity": severity,
            },
            {
                "type": "inflation_spike",
                "name": "Hiper Enflasyon",
                "description": "Tüm fiyatlar %{amount} arttı!",
                "effect": {"price_multiplier": 1.0 + (0.5 * severity)},
                "duration_turns": int(5 + (5 * severity)),
                "severity": severity,
            },
            {
                "type": "supply_shortage",
                "name": "Arz Krizi",
                "description": "{product} ürününde ciddi kıtlık!",
                "effect": {"supply_multiplier": max(0.2, 1.0 - (0.6 * severity))},
                "duration_turns": int(4 + (4 * severity)),
                "severity": severity,
            },
            # Doğal Afetler
            {
                "type": "natural_disaster",
                "name": "Doğal Afet",
                "description": "{city} şehrinde deprem! Ticaret {duration} tur durdu.",
                "effect": {"city_trade_blocked": True},
                "duration_turns": int(2 + (2 * severity)),
                "severity": severity,
            },
            {
                "type": "pandemic",
                "name": "Salgın Hastalık",
                "description": "Salgın! Tüm şehirler arası ticaret maliyeti 2x.",
                "effect": {"transport_cost_multiplier": 2.0 + severity},
                "duration_turns": int(6 + (4 * severity)),
                "severity": severity,
            },
            # Fırsatlar (nadir, yüksek zorlukta az görülür)
            {
                "type": "gold_rush",
                "name": "Altın Madeni Bulundu",
                "description": "{city} şehrinde altın bulundu! Fiyatlar uçtu!",
                "effect": {"specific_product_price_multiplier": 3.0},
                "duration_turns": int(3),
                "severity": -0.5,  # Pozitif etki
            },
            # Pazar Manipülasyonları (yüksek zorlukta)
            {
                "type": "market_manipulation",
                "name": "Pazar Manipülasyonu",
                "description": "AI karteli fiyatları manipüle ediyor!",
                "effect": {"ai_collusion": True, "price_fixing": True},
                "duration_turns": int(8 * severity),
                "severity": severity,
            },
            # Devlet Müdahaleleri
            {
                "type": "government_regulation",
                "name": "Yeni Düzenleme",
                "description": "Hükümet yeni vergiler koydu! Vergi oranı %{amount} arttı.",
                "effect": {"tax_increase": 0.05 * severity},
                "duration_turns": int(10 + (10 * severity)),
                "severity": severity,
            },
            # Teknolojik İnovasyonlar
            {
                "type": "tech_breakthrough",
                "name": "Teknolojik İlerleme",
                "description": "Yeni taşıma teknolojisi! Maliyetler %20 düştü.",
                "effect": {"transport_cost_multiplier": 0.8},
                "duration_turns": int(5),
                "severity": -0.3,
            },
            # Ticaret Savaşları
            {
                "type": "trade_war",
                "name": "Ticaret Savaşı",
                "description": "{city1} ve {city2} arasında ticaret savaşı! Gümrük vergileri 3x.",
                "effect": {"tariff_multiplier": 3.0},
                "duration_turns": int(7 + (7 * severity)),
                "severity": severity,
            },
        ]

        # Zorluk seviyesine göre event seç
        if severity < 0.5:
            # Düşük zorlukta pozitif eventler daha olası
            event = random.choice(events[:6] + [events[5]] * 2)  # Fırsat 2x daha olası
        else:
            # Yüksek zorlukta negatif eventler daha olası
            event = random.choice(events)

        return event


class AIPlayerBehavior:
    """AI rakip davranış sistemi"""

    def __init__(self, difficulty_config: DifficultyConfig, player_id: str):
        self.config = difficulty_config
        self.player_id = player_id
        self.capital = difficulty_config.ai_starting_capital
        self.inventory = {}
        self.memory = []  # Geçmiş kararları hatırla
        self.strategy = self._determine_strategy()

    def _determine_strategy(self) -> str:
        """AI strateji tipi seç"""
        intelligence = self.config.ai_intelligence

        if intelligence > 0.9:
            return random.choice(
                [
                    "adaptive_learning",  # Oyuncunun stratejisini öğrenir ve karşı hamle yapar
                    "market_manipulation",  # Piyasayı manipüle etmeye çalışır
                    "perfect_timing",  # Mükemmel alım-satım zamanlaması
                ]
            )
        elif intelligence > 0.7:
            return random.choice(
                [
                    "aggressive",  # Agresif ticaret
                    "monopoly_seeker",  # Tekel oluşturmaya çalışır
                    "arbitrage_master",  # Şehirler arası fark avcısı
                ]
            )
        elif intelligence > 0.5:
            return random.choice(
                [
                    "balanced",  # Dengeli oyun
                    "defensive",  # Muhafazakar
                    "opportunist",  # Fırsat avcısı
                ]
            )
        else:
            return "basic"  # Basit alım-satım

    def make_decision(self, game_state: Dict) -> Dict:
        """AI kararı ver"""
        # Strateji bazlı karar
        if self.strategy == "adaptive_learning":
            return self._adaptive_strategy(game_state)
        elif self.strategy == "market_manipulation":
            return self._manipulation_strategy(game_state)
        elif self.strategy == "perfect_timing":
            return self._perfect_timing_strategy(game_state)
        elif self.strategy == "aggressive":
            return self._aggressive_strategy(game_state)
        elif self.strategy == "monopoly_seeker":
            return self._monopoly_strategy(game_state)
        elif self.strategy == "arbitrage_master":
            return self._arbitrage_strategy(game_state)
        else:
            return self._basic_strategy(game_state)

    def _adaptive_learning_strategy(self, game_state: Dict) -> Dict:
        """Öğrenen AI - oyuncunun hareketlerini analiz eder"""
        # Oyuncunun en çok hangi ürünü alıp sattığını öğren
        # Oyuncudan önce al, fiyatı yükselt
        # Oyuncunun satış yapacağı şehirlerde rekabet et
        return {
            "action": "buy",
            "product": self._predict_player_target_product(game_state),
            "amount": self._calculate_aggressive_amount(game_state),
            "strategy_notes": "Adaptive learning active",
        }

    def _market_manipulation_strategy(self, game_state: Dict) -> Dict:
        """Piyasa manipülasyonu - fiyatları etkilemeye çalış"""
        # Bir üründe tekel oluştur
        # Fiyatı yapay olarak yükselt
        # Diğer AI'larla işbirliği (yüksek zorlukta)
        return {
            "action": "monopolize",
            "product": self._find_monopoly_opportunity(game_state),
            "amount": "maximum",
            "strategy_notes": "Market manipulation detected",
        }

    def _perfect_timing_strategy(self, game_state: Dict) -> Dict:
        """Mükemmel zamanlama - en iyi alım-satım anlarını yakalar"""
        # Teknik analiz benzeri hesaplamalar
        # Fiyat trendlerini öngörür
        # En düşük fiyatta al, en yüksek fiyatta sat
        return {
            "action": "time_market",
            "timing_quality": self.config.ai_intelligence,
            "strategy_notes": "Perfect timing engaged",
        }

    def _aggressive_strategy(self, game_state: Dict) -> Dict:
        """Agresif strateji - hızlı ve riskli"""
        return {
            "action": "aggressive_trade",
            "risk_level": "high",
        }

    def _monopoly_strategy(self, game_state: Dict) -> Dict:
        """Tekel stratejisi"""
        return {"action": "monopoly_attempt"}

    def _arbitrage_strategy(self, game_state: Dict) -> Dict:
        """Arbitraj stratejisi - şehirler arası fark"""
        return {"action": "arbitrage"}

    def _basic_strategy(self, game_state: Dict) -> Dict:
        """Basit alım-satım"""
        return {"action": "simple_trade"}

    def _predict_player_target_product(self, game_state: Dict) -> str:
        """Oyuncunun hedef ürününü tahmin et"""
        # Memory'den en çok alınan ürünü bul
        return "default_product"

    def _calculate_aggressive_amount(self, game_state: Dict) -> int:
        """Agresif miktar hesapla"""
        return int(self.capital * 0.7)  # Sermayenin %70'i

    def _find_monopoly_opportunity(self, game_state: Dict) -> str:
        """Tekel fırsatı bul"""
        return "high_demand_product"


class DifficultyManager:
    """Zorluk yöneticisi - oyun sırasında dinamik ayarlamalar"""

    def __init__(self, difficulty_level: DifficultyLevel):
        self.difficulty = difficulty_level
        self.config = DIFFICULTY_CONFIGS[difficulty_level]
        self.active_events = []
        self.ai_players = []
        self._initialize_ai_players()

    def _initialize_ai_players(self):
        """AI rakipleri oluştur"""
        for i in range(self.config.ai_count):
            ai_player = AIPlayerBehavior(self.config, f"AI_{i+1}")
            self.ai_players.append(ai_player)

    def calculate_market_price(
        self, base_price: float, product: str, city: str
    ) -> float:
        """Zorluk bazlı pazar fiyatı hesapla"""
        price = base_price

        # Volatilite ekle
        volatility = random.uniform(
            -self.config.price_volatility, self.config.price_volatility
        )
        price *= 1.0 + volatility

        # Aktif eventlerin etkisi
        for event in self.active_events:
            if event["type"] == "inflation_spike":
                price *= event["effect"].get("price_multiplier", 1.0)
            elif event["type"] == "supply_shortage" and event.get("product") == product:
                price *= (
                    event["effect"].get("supply_multiplier", 1.0) * 2.0
                )  # Kıtlıkta fiyat artar

        return max(1, int(price))

    def calculate_transport_cost(self, distance: float, amount: int) -> int:
        """Taşıma maliyeti hesapla"""
        base_cost = distance * amount * 0.1
        adjusted_cost = base_cost * self.config.transport_cost_multiplier

        # Aktif eventlerin etkisi
        for event in self.active_events:
            if event["type"] == "pandemic":
                adjusted_cost *= event["effect"].get("transport_cost_multiplier", 1.0)

        return max(1, int(adjusted_cost))

    def calculate_tax(self, profit: int) -> int:
        """Vergi hesapla"""
        tax = profit * self.config.tax_rate

        # Event bonusları
        for event in self.active_events:
            if event["type"] == "government_regulation":
                tax += profit * event["effect"].get("tax_increase", 0.0)

        return max(0, int(tax))

    def process_turn(self) -> List[Dict]:
        """Her tur zorluk sistemi güncelleme"""
        new_events = []

        # Event oluştur
        event = RandomEventSystem.generate_event(self.config)
        if event:
            self.active_events.append(event)
            new_events.append(event)

        # Eski eventleri temizle
        self.active_events = [
            e for e in self.active_events if e.get("duration_turns", 0) > 0
        ]

        # Event sürelerini azalt
        for event in self.active_events:
            event["duration_turns"] = event.get("duration_turns", 0) - 1

        # AI kararları
        ai_actions = []
        for ai in self.ai_players:
            if random.random() < self.config.ai_intelligence:
                action = ai.make_decision({"events": self.active_events})
                ai_actions.append(
                    {
                        "ai_id": ai.player_id,
                        "action": action,
                    }
                )

        return new_events, ai_actions

    def get_victory_requirement(self, starting_capital: int) -> int:
        """Zafer için gerekli sermaye"""
        return int(starting_capital * self.config.victory_condition_multiplier)

    def get_rewards(self, score: int, victory: bool) -> Dict:
        """Ödülleri hesapla"""
        base_xp = score * 0.1
        base_coins = score * 0.05

        xp = int(base_xp * self.config.xp_multiplier)
        coins = int(base_coins * self.config.coin_multiplier)

        if victory:
            xp = int(xp * 1.5)
            coins = int(coins * 1.5)

        return {
            "xp": xp,
            "coins": coins,
            "elo_change": self._calculate_elo_change(victory),
        }

    def _calculate_elo_change(self, victory: bool) -> int:
        """ELO değişimi hesapla"""
        base_change = 32 if victory else -20
        return int(base_change * self.config.elo_gain_multiplier)


# Zorluk kilit açma sistemi
DIFFICULTY_UNLOCK_REQUIREMENTS = {
    DifficultyLevel.BEGINNER: {"min_level": 1, "min_elo": 0},
    DifficultyLevel.EASY: {"min_level": 1, "min_elo": 0},
    DifficultyLevel.NORMAL: {"min_level": 3, "min_elo": 1000},
    DifficultyLevel.HARD: {"min_level": 5, "min_elo": 1200},
    DifficultyLevel.EXPERT: {"min_level": 10, "min_elo": 1500},
    DifficultyLevel.MASTER: {"min_level": 15, "min_elo": 1800},
    DifficultyLevel.GRANDMASTER: {"min_level": 25, "min_elo": 2200},
    DifficultyLevel.CHALLENGER: {"min_level": 40, "min_elo": 2400},
}


def get_available_difficulties(
    player_level: int, player_elo: int
) -> List[DifficultyLevel]:
    """Oyuncunun erişebileceği zorluk seviyelerini döndür"""
    available = []
    for level, requirements in DIFFICULTY_UNLOCK_REQUIREMENTS.items():
        if (
            player_level >= requirements["min_level"]
            and player_elo >= requirements["min_elo"]
        ):
            available.append(level)
    return available


def get_recommended_difficulty(
    player_level: int, player_elo: int, win_rate: float
) -> DifficultyLevel:
    """Oyuncuya önerilen zorluk seviyesi"""
    available = get_available_difficulties(player_level, player_elo)

    if not available:
        return DifficultyLevel.BEGINNER

    # Win rate'e göre öneri
    if win_rate > 0.7:
        # Çok kolay, zorluk artır
        current_index = list(DifficultyLevel).index(available[-1])
        if current_index < len(DifficultyLevel) - 1:
            next_level = list(DifficultyLevel)[current_index + 1]
            if next_level in get_available_difficulties(player_level, player_elo):
                return next_level
    elif win_rate < 0.3:
        # Çok zor, zorluk azalt
        current_index = list(DifficultyLevel).index(available[-1])
        if current_index > 0:
            return list(DifficultyLevel)[current_index - 1]

    return available[-1]
