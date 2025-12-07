"""
E-Spor için gerekli başlangıç verilerini oluşturur
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from games.models import Game, Season, Badge, DailyQuest, Item


class Command(BaseCommand):
    help = "E-spor için oyun verilerini oluşturur"

    def handle(self, *args, **options):
        with transaction.atomic():
            # 1. Oyunları oluştur
            games_data = [
                {
                    "name": "TradeSim",
                    "description": "Sehirler arasi ticaret yaparak kar edin",
                    "game_type": "simulation",
                    "min_players": 1,
                    "max_players": 4,
                    "duration_minutes": 20,
                    "is_esport_enabled": True,
                },
                {
                    "name": "Borsa Simulasyonu",
                    "description": "Sanal borsada hisse alim-satimi",
                    "game_type": "competitive",
                    "min_players": 1,
                    "max_players": 10,
                    "duration_minutes": 15,
                    "is_esport_enabled": True,
                },
                {
                    "name": "Butce Mucadelesi",
                    "description": "Butce yonetimi challenge",
                    "game_type": "educational",
                    "min_players": 1,
                    "max_players": 1,
                    "duration_minutes": 10,
                    "is_esport_enabled": False,
                },
                {
                    "name": "Finans Quiz",
                    "description": "Finansal bilgi yarismasi",
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
                    self.stdout.write(self.style.SUCCESS(f"[+] Oyun: {game.name}"))

            # 2. Aktif sezon oluştur
            now = timezone.now()
            season, created = Season.objects.get_or_create(
                name="Sezon 1 - 2025",
                defaults={
                    "start_date": now,
                    "end_date": now + timedelta(days=90),
                    "is_active": True,
                    "reward_pool": 500000,
                    "description": "FinAsis ilk resmi e-spor sezonu!",
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"[+] Sezon: {season.name}"))

            # 3. Rozetler oluştur
            badges_data = [
                {
                    "name": "Yeni Baslayan",
                    "icon": "🌟",
                    "rarity": "common",
                    "points": 10,
                    "xp_reward": 50,
                    "description": "Ilk oyununuzu tamamlayin",
                    "criteria": {"games_played": 1},
                },
                {
                    "name": "Kazanan",
                    "icon": "🏆",
                    "rarity": "common",
                    "points": 25,
                    "xp_reward": 100,
                    "description": "Ilk zaferiniz",
                    "criteria": {"games_won": 1},
                },
                {
                    "name": "Ticaret Ustasi",
                    "icon": "💰",
                    "rarity": "rare",
                    "points": 100,
                    "xp_reward": 500,
                    "description": "TradeSim'de 10 oyun kazanin",
                    "criteria": {"tradesim_wins": 10},
                },
                {
                    "name": "Borsa Asamasi",
                    "icon": "📈",
                    "rarity": "rare",
                    "points": 150,
                    "xp_reward": 750,
                    "description": "Borsa simülasyonunda 100k kar yapin",
                    "criteria": {"stock_profit": 100000},
                },
                {
                    "name": "Quiz Dehasi",
                    "icon": "🧠",
                    "rarity": "epic",
                    "points": 200,
                    "xp_reward": 1000,
                    "description": "Finans Quiz'de mukemmel puan",
                    "criteria": {"quiz_perfect": 1},
                },
                {
                    "name": "Haftalik Kahraman",
                    "icon": "⭐",
                    "rarity": "epic",
                    "points": 250,
                    "xp_reward": 1500,
                    "description": "7 gun ust uste oynatin",
                    "criteria": {"daily_streak": 7},
                },
                {
                    "name": "Efsane Oyuncu",
                    "icon": "👑",
                    "rarity": "legendary",
                    "points": 1000,
                    "xp_reward": 5000,
                    "description": "Challenger rankina ulasin",
                    "criteria": {"rank": "challenger"},
                },
            ]

            for badge_data in badges_data:
                badge, created = Badge.objects.update_or_create(
                    name=badge_data["name"], defaults=badge_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"[+] Rozet: {badge.name}"))

            # 4. Daily Quests oluştur
            quests_data = [
                {
                    "quest_type": "play_games",
                    "title": "3 Oyun Oyna",
                    "description": "Bugun 3 farkli oyun oynatin",
                    "target_value": 3,
                    "reward_xp": 150,
                    "reward_coins": 500,
                    "difficulty_level": 1,
                    "is_daily": True,
                },
                {
                    "quest_type": "win_games",
                    "title": "5 Oyun Kazan",
                    "description": "Bugun 5 oyun kazanin",
                    "target_value": 5,
                    "reward_xp": 300,
                    "reward_coins": 1000,
                    "reward_gems": 10,
                    "difficulty_level": 3,
                    "is_daily": True,
                },
                {
                    "quest_type": "earn_score",
                    "title": "10.000 Puan Kazan",
                    "description": "Toplam 10.000 puan kazanin",
                    "target_value": 10000,
                    "reward_xp": 500,
                    "reward_coins": 2000,
                    "reward_gems": 25,
                    "difficulty_level": 4,
                    "is_daily": False,
                    "is_weekly": True,
                },
                {
                    "quest_type": "play_games",
                    "title": "TradeSim Oyna",
                    "description": "TradeSim'de 1 oyun tamamlayin",
                    "target_value": 1,
                    "reward_xp": 100,
                    "reward_coins": 300,
                    "difficulty_level": 1,
                    "is_daily": True,
                },
            ]

            for quest_data in quests_data:
                quest, created = DailyQuest.objects.update_or_create(
                    title=quest_data["title"], defaults=quest_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"[+] Quest: {quest.title}"))

            # 5. Eşyalar (Store items)
            items_data = [
                {
                    "name": "XP Boost (1 Saat)",
                    "description": "1 saat boyunca %50 bonus XP",
                    "item_type": "boost",
                    "rarity": "common",
                    "price_coins": 1000,
                    "effect_data": {"xp_multiplier": 1.5},
                    "duration_hours": 1,
                },
                {
                    "name": "Coin Doubler (2 Saat)",
                    "description": "2 saat boyunca 2x altin kazanin",
                    "item_type": "boost",
                    "rarity": "rare",
                    "price_coins": 2500,
                    "effect_data": {"coin_multiplier": 2.0},
                    "duration_hours": 2,
                },
                {
                    "name": "VIP Rozet",
                    "description": "Isminizin yaninda VIP rozeti",
                    "item_type": "badge",
                    "rarity": "epic",
                    "price_gems": 100,
                    "effect_data": {},
                    "duration_hours": 0,  # Kalıcı
                },
                {
                    "name": "Altin Avatar Cercevesi",
                    "description": "Profilinize altin cerceve ekler",
                    "item_type": "avatar",
                    "rarity": "epic",
                    "price_gems": 150,
                    "effect_data": {},
                    "duration_hours": 0,
                },
                {
                    "name": "Zafer Efekti",
                    "description": "Kazandiginizda ozel animasyon",
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
                    self.stdout.write(self.style.SUCCESS(f"[+] Esya: {item.name}"))

        self.stdout.write(
            self.style.SUCCESS("\n[OK] E-spor verileri basariyla olusturuldu!")
        )
        self.stdout.write("\n=== OLUSTURULAN ===")
        self.stdout.write(f"Oyunlar: {Game.objects.count()}")
        self.stdout.write(f"Sezonlar: {Season.objects.count()}")
        self.stdout.write(f"Rozetler: {Badge.objects.count()}")
        self.stdout.write(f"Gunluk Gorevler: {DailyQuest.objects.count()}")
        self.stdout.write(f"Esyalar: {Item.objects.count()}")
        self.stdout.write("====================\n")
