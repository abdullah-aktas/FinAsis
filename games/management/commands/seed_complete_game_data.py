# -*- coding: utf-8 -*-
"""
Eksiksiz Oyun Verileri Seed Komutu
TradeSim, FinQuest ve Ticaretin İzinde için tüm verileri oluşturur
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from games.models import Game, Season, Badge, DailyQuest, Item, Tournament
from games.trade_sim.models import City, Product, CityMarket, Quest
from django.contrib.auth import get_user_model
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Tüm oyunlar için eksiksiz veri oluşturur: şehirler, ürünler, turnuvalar, rozetler, ödüller"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Mevcut verileri sil ve yeniden oluştur",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write(
                self.style.SUCCESS("🎮 Eksiksiz Oyun Verileri Oluşturuluyor...\n")
            )

            # 1. Oyunları oluştur
            self._create_games()

            # 2. TradeSim verileri
            self._create_tradesim_data()

            # 3. Rozetler
            self._create_badges()

            # 4. Sezonlar
            self._create_seasons()

            # 5. Turnuvalar
            self._create_tournaments()

            # 6. Günlük görevler
            self._create_daily_quests()

            # 7. Mağaza eşyaları
            self._create_store_items()

            # 8. Örnek karakterler ve quest'ler
            self._create_sample_quests()

            self.stdout.write(
                self.style.SUCCESS("\n✅ Tüm oyun verileri başarıyla oluşturuldu!")
            )

    def _create_games(self):
        """Oyun tanımlarını oluştur"""
        self.stdout.write("📦 Oyunlar oluşturuluyor...")

        games_data = [
            {
                "name": "TradeSim",
                "description": "Şehirler arası ticaret simülasyonu - En popüler oyunumuz",
                "game_type": "simulation",
                "min_players": 1,
                "max_players": 4,
                "duration_minutes": 20,
                "is_esport_enabled": True,
            },
            {
                "name": "FinQuest",
                "description": "Finansal macera oyunu - Hikaye tabanlı öğrenme",
                "game_type": "educational",
                "min_players": 1,
                "max_players": 1,
                "duration_minutes": 30,
                "is_esport_enabled": False,
            },
            {
                "name": "Ticaretin İzinde",
                "description": "3D işletme simülasyonu - Gerçekçi ticaret deneyimi",
                "game_type": "simulation",
                "min_players": 1,
                "max_players": 8,
                "duration_minutes": 45,
                "is_esport_enabled": True,
            },
            {
                "name": "Borsa Simülasyonu",
                "description": "Sanal borsada hisse alım-satımı",
                "game_type": "competitive",
                "min_players": 1,
                "max_players": 10,
                "duration_minutes": 15,
                "is_esport_enabled": True,
            },
            {
                "name": "Finans Quiz",
                "description": "Finansal bilgi yarışması",
                "game_type": "competitive",
                "min_players": 1,
                "max_players": 50,
                "duration_minutes": 5,
                "is_esport_enabled": True,
            },
        ]

        for game_data in games_data:
            game, created = Game.objects.update_or_create(
                name=game_data["name"], defaults=game_data
            )
            if created:
                self.stdout.write(f"  ✓ {game.name}")

    def _create_tradesim_data(self):
        """TradeSim için şehirler, ürünler ve piyasa verileri"""
        self.stdout.write("\n🏙️ TradeSim verileri oluşturuluyor...")

        # Şehirler
        cities_data = [
            {
                "name": "İstanbul",
                "description": "Finans ve ticaret merkezi - En büyük pazar",
                "sectors": ["finans", "teknoloji", "turizm", "sanayi"],
                "coordinates": {"x": 10, "y": 5},
                "market_size": 5000,
                "sector_markets": {
                    "finans": {"price": 150, "demand": 200},
                    "teknoloji": {"price": 200, "demand": 180},
                    "turizm": {"price": 120, "demand": 150},
                    "sanayi": {"price": 100, "demand": 100},
                },
            },
            {
                "name": "Ankara",
                "description": "Başkent - Bürokrasi ve hizmet sektörü",
                "sectors": ["finans", "sanayi", "tarım"],
                "coordinates": {"x": 70, "y": 80},
                "market_size": 3000,
                "sector_markets": {
                    "finans": {"price": 130, "demand": 150},
                    "sanayi": {"price": 90, "demand": 120},
                    "tarım": {"price": 80, "demand": 100},
                },
            },
            {
                "name": "İzmir",
                "description": "Ege'nin incisi - Tarım ve turizm",
                "sectors": ["tarım", "turizm", "sanayi"],
                "coordinates": {"x": 50, "y": 60},
                "market_size": 2500,
                "sector_markets": {
                    "tarım": {"price": 70, "demand": 200},
                    "turizm": {"price": 110, "demand": 180},
                    "sanayi": {"price": 95, "demand": 110},
                },
            },
            {
                "name": "Bursa",
                "description": "Sanayi şehri - Otomotiv ve tekstil",
                "sectors": ["sanayi", "teknoloji"],
                "coordinates": {"x": 30, "y": 40},
                "market_size": 2000,
                "sector_markets": {
                    "sanayi": {"price": 85, "demand": 180},
                    "teknoloji": {"price": 180, "demand": 120},
                },
            },
            {
                "name": "Antalya",
                "description": "Turizm başkenti - Yüksek talep",
                "sectors": ["turizm", "tarım"],
                "coordinates": {"x": 60, "y": 100},
                "market_size": 1800,
                "sector_markets": {
                    "turizm": {"price": 140, "demand": 250},
                    "tarım": {"price": 75, "demand": 150},
                },
            },
            {
                "name": "Gaziantep",
                "description": "Güneydoğu'nun ticaret merkezi",
                "sectors": ["tarım", "sanayi", "finans"],
                "coordinates": {"x": 120, "y": 140},
                "market_size": 1500,
                "sector_markets": {
                    "tarım": {"price": 60, "demand": 180},
                    "sanayi": {"price": 80, "demand": 100},
                    "finans": {"price": 110, "demand": 90},
                },
            },
            {
                "name": "Konya",
                "description": "Tarım merkezi - Düşük fiyat, yüksek arz",
                "sectors": ["tarım", "sanayi"],
                "coordinates": {"x": 80, "y": 120},
                "market_size": 1200,
                "sector_markets": {
                    "tarım": {"price": 50, "demand": 200},
                    "sanayi": {"price": 70, "demand": 80},
                },
            },
            {
                "name": "Trabzon",
                "description": "Karadeniz liman şehri - Balık ve tarım",
                "sectors": ["tarım", "turizm"],
                "coordinates": {"x": 150, "y": 30},
                "market_size": 1000,
                "sector_markets": {
                    "tarım": {"price": 65, "demand": 120},
                    "turizm": {"price": 100, "demand": 100},
                },
            },
        ]

        city_objects = {}
        for city_data in cities_data:
            city, created = City.objects.update_or_create(
                name=city_data["name"],
                defaults={
                    "description": city_data["description"],
                    "sectors": city_data["sectors"],
                    "coordinates": city_data["coordinates"],
                    "market_size": city_data["market_size"],
                    "sector_markets": city_data["sector_markets"],
                    "weather": random.choice(["gunesli", "yagmurlu", "sisli"]),
                    "time_of_day": random.choice(["sabah", "oglen", "aksam"]),
                },
            )
            city_objects[city.name] = city
            if created:
                self.stdout.write(f"  ✓ Şehir: {city.name}")

        # Komşuluklar
        neighbors_map = {
            "İstanbul": ["Bursa", "Ankara"],
            "Ankara": ["İstanbul", "Konya", "Bursa"],
            "İzmir": ["Bursa", "Antalya"],
            "Bursa": ["İstanbul", "Ankara", "İzmir"],
            "Antalya": ["İzmir", "Konya"],
            "Gaziantep": ["Konya"],
            "Konya": ["Ankara", "Antalya", "Gaziantep"],
            "Trabzon": [],
        }

        for city_name, neighbor_names in neighbors_map.items():
            if city_name in city_objects:
                city = city_objects[city_name]
                for neighbor_name in neighbor_names:
                    if neighbor_name in city_objects:
                        city.neighbors.add(city_objects[neighbor_name])

        # Ürünler
        products_data = [
            ("Buğday", "Temel tarım ürünü", 100, "kg", "tarım"),
            ("Mısır", "Yem ve gıda ürünü", 120, "kg", "tarım"),
            ("Pamuk", "Tekstil hammaddesi", 300, "kg", "tarım"),
            ("Bakır", "Sanayi hammaddesi", 500, "kg", "madencilik"),
            ("Demir", "İnşaat ve sanayi", 400, "kg", "madencilik"),
            ("Altın", "Değerli maden", 5000, "gram", "madencilik"),
            ("Petrol", "Enerji kaynağı", 800, "varil", "enerji"),
            ("Tekstil", "Hazır giyim", 200, "adet", "sanayi"),
            ("Elektronik", "Teknoloji ürünü", 1500, "adet", "teknoloji"),
            ("Gıda", "İşlenmiş gıda", 150, "kg", "gıda"),
            ("İlaç", "Sağlık ürünü", 2000, "kutu", "sağlık"),
            ("Turizm Paketi", "Seyahat paketi", 5000, "paket", "turizm"),
        ]

        product_objects = {}
        for name, desc, base_price, unit, category in products_data:
            product, created = Product.objects.update_or_create(
                name=name,
                defaults={
                    "description": desc,
                    "base_price": base_price,
                    "unit": unit,
                    "category": category,
                },
            )
            product_objects[name] = product
            if created:
                self.stdout.write(f"  ✓ Ürün: {name}")

        # Şehir-Ürün piyasaları (her şehirde her ürün için farklı fiyat)
        for city in city_objects.values():
            for product in product_objects.values():
                # Şehir sektörüne göre fiyat varyasyonu
                base_multiplier = 1.0
                if product.category in city.sectors:
                    base_multiplier = 0.8  # Şehirde üretiliyorsa daha ucuz
                else:
                    base_multiplier = 1.2  # Şehirde üretilmiyorsa daha pahalı

                price = int(
                    product.base_price * base_multiplier * random.uniform(0.9, 1.1)
                )
                supply = random.randint(50, 200)
                demand = random.randint(50, 200)

                CityMarket.objects.update_or_create(
                    city=city,
                    product=product,
                    defaults={
                        "price": price,
                        "supply": supply,
                        "demand": demand,
                    },
                )

        self.stdout.write(f"  ✓ {CityMarket.objects.count()} piyasa oluşturuldu")

    def _create_badges(self):
        """Rozetler oluştur"""
        self.stdout.write("\n🏆 Rozetler oluşturuluyor...")

        badges_data = [
            # Başlangıç rozetleri
            {
                "name": "İlk Adım",
                "icon": "🌟",
                "rarity": "common",
                "points": 10,
                "xp_reward": 50,
                "description": "İlk oyununuzu tamamlayın",
                "criteria": {"games_played": 1},
            },
            {
                "name": "İlk Zafer",
                "icon": "🏆",
                "rarity": "common",
                "points": 25,
                "xp_reward": 100,
                "description": "İlk oyunu kazanın",
                "criteria": {"games_won": 1},
            },
            # TradeSim rozetleri
            {
                "name": "Ticaret Ustası",
                "icon": "💰",
                "rarity": "rare",
                "points": 100,
                "xp_reward": 500,
                "description": "TradeSim'de 10 oyun kazanın",
                "criteria": {"tradesim_wins": 10},
            },
            {
                "name": "Şehir Gezgini",
                "icon": "🗺️",
                "rarity": "rare",
                "points": 150,
                "xp_reward": 750,
                "description": "Tüm şehirleri ziyaret edin",
                "criteria": {"cities_visited": 8},
            },
            {
                "name": "Milyoner Trader",
                "icon": "💎",
                "rarity": "epic",
                "points": 300,
                "xp_reward": 1500,
                "description": "TradeSim'de 1 milyon kar yapın",
                "criteria": {"total_profit": 1000000},
            },
            # FinQuest rozetleri
            {
                "name": "Finans Maceracısı",
                "icon": "⚔️",
                "rarity": "rare",
                "points": 200,
                "xp_reward": 1000,
                "description": "FinQuest'te 5 bölüm tamamlayın",
                "criteria": {"finquest_chapters": 5},
            },
            {
                "name": "Bilge Finansçı",
                "icon": "📚",
                "rarity": "epic",
                "points": 400,
                "xp_reward": 2000,
                "description": "FinQuest'te tüm görevleri tamamlayın",
                "criteria": {"finquest_all_quests": True},
            },
            # Genel rozetler
            {
                "name": "Haftalık Kahraman",
                "icon": "⭐",
                "rarity": "epic",
                "points": 250,
                "xp_reward": 1500,
                "description": "7 gün üst üste oynayın",
                "criteria": {"daily_streak": 7},
            },
            {
                "name": "Aylık Şampiyon",
                "icon": "👑",
                "rarity": "legendary",
                "points": 500,
                "xp_reward": 3000,
                "description": "30 gün üst üste oynayın",
                "criteria": {"daily_streak": 30},
            },
            {
                "name": "Efsane Oyuncu",
                "icon": "💫",
                "rarity": "legendary",
                "points": 1000,
                "xp_reward": 5000,
                "description": "Challenger rankına ulaşın",
                "criteria": {"rank": "challenger"},
            },
            {
                "name": "Turnuva Şampiyonu",
                "icon": "🏅",
                "rarity": "legendary",
                "points": 800,
                "xp_reward": 4000,
                "description": "Bir turnuvada 1. olun",
                "criteria": {"tournament_first": 1},
            },
            {
                "name": "Top 10",
                "icon": "🎯",
                "rarity": "epic",
                "points": 300,
                "xp_reward": 1500,
                "description": "Liderlik tablosunda ilk 10'a girin",
                "criteria": {"leaderboard_top10": True},
            },
        ]

        for badge_data in badges_data:
            badge, created = Badge.objects.update_or_create(
                name=badge_data["name"], defaults=badge_data
            )
            if created:
                self.stdout.write(f"  ✓ {badge.icon} {badge.name}")

    def _create_seasons(self):
        """Sezonlar oluştur"""
        self.stdout.write("\n📅 Sezonlar oluşturuluyor...")

        now = timezone.now()
        seasons_data = [
            {
                "name": "Sezon 1 - 2025 Beta",
                "start_date": now,
                "end_date": now + timedelta(days=90),
                "is_active": True,
                "reward_pool": 1000000,
                "description": "FinAsis ilk resmi e-spor sezonu - Beta dönemi özel ödüller!",
            },
            {
                "name": "Sezon 2 - 2025 Yaz",
                "start_date": now + timedelta(days=91),
                "end_date": now + timedelta(days=180),
                "is_active": False,
                "reward_pool": 2000000,
                "description": "Yaz sezonu - Daha büyük ödül havuzu",
            },
        ]

        for season_data in seasons_data:
            season, created = Season.objects.update_or_create(
                name=season_data["name"], defaults=season_data
            )
            if created:
                self.stdout.write(f"  ✓ {season.name}")

    def _create_tournaments(self):
        """Turnuvalar oluştur"""
        self.stdout.write("\n🎯 Turnuvalar oluşturuluyor...")

        try:
            tradesim_game = Game.objects.get(name="TradeSim")
        except Game.DoesNotExist:
            self.stdout.write(self.style.WARNING("  ⚠ TradeSim oyunu bulunamadı"))
            return

        try:
            current_season = Season.objects.filter(is_active=True).first()
        except Season.DoesNotExist:
            current_season = None

        now = timezone.now()

        # TradeSim turnuvaları
        tournaments_data = [
            {
                "name": "Haftalık TradeSim Yarışması",
                "description": "Her hafta düzenlenen hızlı yarışma - Tüm seviyeler",
                "game": tradesim_game,
                "season": current_season,
                "tournament_type": "casual",
                "status": "registration",
                "registration_start": now - timedelta(days=1),
                "registration_end": now + timedelta(days=6),
                "start_date": now + timedelta(days=7),
                "end_date": now + timedelta(days=7, hours=24),
                "max_participants": 100,
                "entry_fee_coins": 100,
                "prize_pool_coins": 50000,
                "prize_distribution": {"1": 0.5, "2": 0.3, "3": 0.2},
            },
            {
                "name": "TradeSim Şampiyonası",
                "description": "Aylık büyük turnuva - Sadece Gold+ rank",
                "game": tradesim_game,
                "season": current_season,
                "tournament_type": "championship",
                "status": "upcoming",
                "registration_start": now + timedelta(days=20),
                "registration_end": now + timedelta(days=27),
                "start_date": now + timedelta(days=28),
                "end_date": now + timedelta(days=30),
                "max_participants": 64,
                "entry_fee_coins": 1000,
                "prize_pool_coins": 500000,
                "prize_pool_gems": 100,
                "prize_distribution": {
                    "1": 0.4,
                    "2": 0.25,
                    "3": 0.15,
                    "4-8": 0.1,
                    "9-16": 0.1,
                },
            },
            {
                "name": "Beta Özel Turnuva",
                "description": "Beta kullanıcılarına özel - Ücretsiz katılım!",
                "game": tradesim_game,
                "season": current_season,
                "tournament_type": "special",
                "status": "registration",
                "registration_start": now,
                "registration_end": now + timedelta(days=14),
                "start_date": now + timedelta(days=15),
                "end_date": now + timedelta(days=16),
                "max_participants": 200,
                "entry_fee_coins": 0,
                "prize_pool_coins": 200000,
                "prize_pool_gems": 50,
                "prize_distribution": {"1": 0.3, "2": 0.2, "3": 0.15, "4-10": 0.35},
            },
        ]

        for tour_data in tournaments_data:
            tournament, created = Tournament.objects.update_or_create(
                name=tour_data["name"],
                defaults=tour_data,
            )
            if created:
                self.stdout.write(f"  ✓ {tournament.name}")

    def _create_daily_quests(self):
        """Günlük görevler oluştur"""
        self.stdout.write("\n📋 Günlük görevler oluşturuluyor...")

        quests_data = [
            {
                "quest_type": "play_games",
                "title": "3 Oyun Oyna",
                "description": "Bugün 3 farklı oyun oynayın",
                "target_value": 3,
                "reward_xp": 150,
                "reward_coins": 500,
                "difficulty_level": 1,
                "is_daily": True,
            },
            {
                "quest_type": "win_games",
                "title": "5 Oyun Kazan",
                "description": "Bugün 5 oyun kazanın",
                "target_value": 5,
                "reward_xp": 300,
                "reward_coins": 1000,
                "reward_gems": 10,
                "difficulty_level": 3,
                "is_daily": True,
            },
            {
                "quest_type": "tradesim_trade",
                "title": "TradeSim'de 10 Ticaret Yap",
                "description": "TradeSim'de 10 başarılı ticaret yapın",
                "target_value": 10,
                "reward_xp": 200,
                "reward_coins": 800,
                "difficulty_level": 2,
                "is_daily": True,
            },
            {
                "quest_type": "earn_score",
                "title": "10.000 Puan Kazan",
                "description": "Toplam 10.000 puan kazanın",
                "target_value": 10000,
                "reward_xp": 500,
                "reward_coins": 2000,
                "reward_gems": 25,
                "difficulty_level": 4,
                "is_daily": False,
                "is_weekly": True,
            },
            {
                "quest_type": "visit_cities",
                "title": "5 Şehir Ziyaret Et",
                "description": "TradeSim'de 5 farklı şehir ziyaret edin",
                "target_value": 5,
                "reward_xp": 250,
                "reward_coins": 1200,
                "difficulty_level": 2,
                "is_daily": True,
            },
        ]

        for quest_data in quests_data:
            quest, created = DailyQuest.objects.update_or_create(
                title=quest_data["title"], defaults=quest_data
            )
            if created:
                self.stdout.write(f"  ✓ {quest.title}")

    def _create_store_items(self):
        """Mağaza eşyaları oluştur"""
        self.stdout.write("\n🛒 Mağaza eşyaları oluşturuluyor...")

        items_data = [
            {
                "name": "XP Boost (1 Saat)",
                "description": "1 saat boyunca %50 bonus XP kazanın",
                "item_type": "boost",
                "rarity": "common",
                "price_coins": 1000,
                "effect_data": {"xp_multiplier": 1.5},
                "duration_hours": 1,
            },
            {
                "name": "XP Boost (24 Saat)",
                "description": "24 saat boyunca %50 bonus XP",
                "item_type": "boost",
                "rarity": "rare",
                "price_coins": 15000,
                "price_gems": 50,
                "effect_data": {"xp_multiplier": 1.5},
                "duration_hours": 24,
            },
            {
                "name": "Coin Doubler (2 Saat)",
                "description": "2 saat boyunca 2x altın kazanın",
                "item_type": "boost",
                "rarity": "rare",
                "price_coins": 2500,
                "effect_data": {"coin_multiplier": 2.0},
                "duration_hours": 2,
            },
            {
                "name": "Lucky Charm",
                "description": "Bir sonraki oyunda %20 daha fazla ödül",
                "item_type": "boost",
                "rarity": "epic",
                "price_gems": 100,
                "effect_data": {"reward_multiplier": 1.2},
                "duration_hours": 0,  # Tek kullanımlık
            },
            {
                "name": "VIP Rozet",
                "description": "İsminizin yanında VIP rozeti görünür",
                "item_type": "badge",
                "rarity": "epic",
                "price_gems": 200,
                "effect_data": {},
                "duration_hours": 0,  # Kalıcı
            },
            {
                "name": "Altın Avatar Çerçevesi",
                "description": "Profilinize altın çerçeve ekler",
                "item_type": "avatar",
                "rarity": "epic",
                "price_gems": 150,
                "effect_data": {},
                "duration_hours": 0,
            },
            {
                "name": "Zafer Efekti",
                "description": "Kazandığınızda özel animasyon",
                "item_type": "effect",
                "rarity": "legendary",
                "price_gems": 500,
                "effect_data": {},
                "duration_hours": 0,
            },
        ]

        for item_data in items_data:
            item, created = Item.objects.update_or_create(
                name=item_data["name"], defaults=item_data
            )
            if created:
                self.stdout.write(f"  ✓ {item.name}")

    def _create_sample_quests(self):
        """TradeSim için örnek quest'ler"""
        self.stdout.write("\n📜 TradeSim quest'leri oluşturuluyor...")

        quests_data = [
            {
                "name": "İlk Ticaret",
                "description": "İlk şehir ticaretini tamamla ve 100 altın kazan",
                "quest_type": "main",
                "requirements": {"trade_count": 1},
                "rewards": {"coins": 100, "xp": 10},
            },
            {
                "name": "Şehir Gezgini",
                "description": "3 farklı şehir ziyaret et",
                "quest_type": "side",
                "requirements": {"cities_visited": 3},
                "rewards": {"coins": 300, "xp": 50},
            },
            {
                "name": "Kar Ustası",
                "description": "Tek bir ticarette 1000 altın kar yap",
                "quest_type": "side",
                "requirements": {"single_trade_profit": 1000},
                "rewards": {"coins": 500, "xp": 100},
            },
            {
                "name": "Ticaret Zinciri",
                "description": "5 şehir arasında ticaret yap",
                "quest_type": "main",
                "requirements": {"cities_traded": 5},
                "rewards": {"coins": 1000, "xp": 200},
            },
        ]

        for quest_data in quests_data:
            quest, created = Quest.objects.update_or_create(
                name=quest_data["name"], defaults=quest_data
            )
            if created:
                self.stdout.write(f"  ✓ {quest.name}")

        self.stdout.write(self.style.SUCCESS("\n✅ Tüm veriler başarıyla oluşturuldu!"))
        self.stdout.write("\n📊 ÖZET:")
        self.stdout.write(f"  • Oyunlar: {Game.objects.count()}")
        self.stdout.write(f"  • Şehirler: {City.objects.count()}")
        self.stdout.write(f"  • Ürünler: {Product.objects.count()}")
        self.stdout.write(f"  • Piyasalar: {CityMarket.objects.count()}")
        self.stdout.write(f"  • Rozetler: {Badge.objects.count()}")
        self.stdout.write(f"  • Sezonlar: {Season.objects.count()}")
        self.stdout.write(f"  • Turnuvalar: {Tournament.objects.count()}")
        self.stdout.write(f"  • Görevler: {DailyQuest.objects.count()}")
        self.stdout.write(f"  • Eşyalar: {Item.objects.count()}")
        self.stdout.write(f"  • Quest'ler: {Quest.objects.count()}")
