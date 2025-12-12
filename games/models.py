# -*- coding: utf-8 -*-
"""
FinAsis Games - E-Spor Seviyesinde Oyun Modelleri
Turnuva, Sezon, Quest, Progression ve Multiplayer özellikleri
"""

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta


class Game(models.Model):
    """Oyun tanımları"""

    GAME_TYPES = [
        ("competitive", "Rekabetçi"),
        ("casual", "Günlük"),
        ("educational", "Eğitsel"),
        ("simulation", "Simülasyon"),
    ]

    name = models.CharField(max_length=100, verbose_name="Oyun Adı")
    description = models.TextField(verbose_name="Açıklama")
    game_type = models.CharField(max_length=20, choices=GAME_TYPES, default="casual")
    min_players = models.IntegerField(default=1)
    max_players = models.IntegerField(default=1)
    duration_minutes = models.IntegerField(
        default=15, help_text="Ortalama oyun süresi (dakika)"
    )
    is_esport_enabled = models.BooleanField(default=False, verbose_name="E-Spor Modu")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Oluşturulma Tarihi"
    )

    class Meta:
        verbose_name = "Oyun"
        verbose_name_plural = "Oyunlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Season(models.Model):
    """E-Spor sezonları"""

    name = models.CharField(max_length=100, verbose_name="Sezon Adı")
    start_date = models.DateTimeField(verbose_name="Başlangıç Tarihi")
    end_date = models.DateTimeField(verbose_name="Bitiş Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    reward_pool = models.IntegerField(default=100000, verbose_name="Ödül Havuzu (Puan)")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Sezon"
        verbose_name_plural = "Sezonlar"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({'Aktif' if self.is_active else 'Bitti'})"

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.is_active


class Badge(models.Model):
    """Rozet modeli: oyunculara verilen başarım rozetleri."""

    RARITY_CHOICES = [
        ("common", "Yaygın"),
        ("rare", "Nadir"),
        ("epic", "Epik"),
        ("legendary", "Efsanevi"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Rozet Adı")
    description = models.TextField(verbose_name="Açıklama")
    icon = models.CharField(max_length=50, default="🏆", verbose_name="İkon")
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default="common")
    criteria = models.JSONField(
        default=dict, blank=True, verbose_name="Kazanma Kriteri"
    )
    points = models.PositiveIntegerField(default=10, verbose_name="Puan")
    xp_reward = models.PositiveIntegerField(default=100, verbose_name="XP Ödülü")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Oyun Rozeti"
        verbose_name_plural = "Oyun Rozetleri"
        ordering = ["-points", "name"]

    def __str__(self):
        return f"{self.icon} {self.name} ({self.rarity})"


class PlayerProfile(models.Model):
    """Oyuncu profili - Gelişmiş progression sistemi"""

    DIFFICULTY_CHOICES = [
        ("easy", "Kolay"),
        ("medium", "Orta"),
        ("hard", "Zor"),
        ("expert", "Uzman"),
        ("adaptive", "Uyarlanır"),
    ]

    RANK_CHOICES = [
        ("bronze", "Bronz"),
        ("silver", "Gümüş"),
        ("gold", "Altın"),
        ("platinum", "Platin"),
        ("diamond", "Elmas"),
        ("master", "Usta"),
        ("grandmaster", "Büyük Usta"),
        ("challenger", "Meydan Okuyan"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="player_profile",
    )
    difficulty = models.CharField(
        max_length=16,
        choices=DIFFICULTY_CHOICES,
        default="adaptive",
        verbose_name="Zorluk",
    )

    # XP ve Level Sistemi
    level = models.PositiveIntegerField(default=1, verbose_name="Seviye")
    xp = models.PositiveIntegerField(default=0, verbose_name="Deneyim Puanı")
    xp_to_next_level = models.PositiveIntegerField(
        default=1000, verbose_name="Sonraki Seviyeye Kalan XP"
    )

    # Beceri metrikleri (0-100)
    skill_trade = models.PositiveIntegerField(default=50)
    skill_invest = models.PositiveIntegerField(default=50)
    skill_budget = models.PositiveIntegerField(default=50)
    skill_education = models.PositiveIntegerField(default=50)
    skill_accounting = models.PositiveIntegerField(default=50)

    # Rekabet metrikleri
    rank = models.CharField(
        max_length=20, choices=RANK_CHOICES, default="bronze", verbose_name="Rank"
    )
    mmr = models.IntegerField(default=1000, verbose_name="Matchmaking Rating")
    elo_rating = models.IntegerField(default=1200, verbose_name="ELO Rating")

    # Oyun istatistikleri
    games_played = models.PositiveIntegerField(default=0)
    games_won = models.PositiveIntegerField(default=0)
    games_lost = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0, verbose_name="Toplam Skor")
    highest_score = models.PositiveIntegerField(
        default=0, verbose_name="En Yüksek Skor"
    )

    # Ekonomi
    coins = models.PositiveIntegerField(default=1000, verbose_name="Altın")
    gems = models.PositiveIntegerField(default=0, verbose_name="Elmas (Premium)")

    # İlişkiler
    badges = models.ManyToManyField(
        Badge, blank=True, related_name="players", verbose_name="Rozetler"
    )
    current_season = models.ForeignKey(
        Season, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Streak sistemi (bağımlılık yaratma)
    daily_streak = models.PositiveIntegerField(default=0, verbose_name="Günlük Seri")
    last_played_date = models.DateField(null=True, blank=True)

    # Meta data
    stats = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    last_recommended = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Oyuncu Profili"
        verbose_name_plural = "Oyuncu Profilleri"
        ordering = ["-elo_rating", "-total_score"]

    def __str__(self):
        return f"{self.user.username} (Lvl {self.level}, {self.rank.upper()})"

    def award_badge(self, badge: "Badge"):
        """Oyuncuya rozet ver, XP ve puan ekle"""
        if badge not in self.badges.all():
            self.badges.add(badge)
            self.add_xp(badge.xp_reward)
            self.total_score += badge.points
            self.save(update_fields=["total_score"])

    def add_xp(self, amount):
        """XP ekle ve level'ı güncelle"""
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(
                1000 * (1.5 ** (self.level - 1))
            )  # Exponential growth
            self.coins += 500 * self.level  # Level başına bonus
        self.save(update_fields=["xp", "level", "xp_to_next_level", "coins"])

    def update_rank(self):
        """ELO'ya göre rank güncelle"""
        if self.elo_rating >= 2400:
            self.rank = "challenger"
        elif self.elo_rating >= 2200:
            self.rank = "grandmaster"
        elif self.elo_rating >= 2000:
            self.rank = "master"
        elif self.elo_rating >= 1800:
            self.rank = "diamond"
        elif self.elo_rating >= 1600:
            self.rank = "platinum"
        elif self.elo_rating >= 1400:
            self.rank = "gold"
        elif self.elo_rating >= 1200:
            self.rank = "silver"
        else:
            self.rank = "bronze"
        self.save(update_fields=["rank"])

    def check_daily_streak(self):
        """Günlük seri kontrolü - bağımlılık yaratma"""
        today = timezone.now().date()
        if self.last_played_date:
            if self.last_played_date == today:
                return  # Bugün zaten oynandı
            elif self.last_played_date == today - timedelta(days=1):
                self.daily_streak += 1
                # Streak bonusu
                if self.daily_streak % 7 == 0:  # Her 7 gün
                    self.coins += 1000
                    self.add_xp(500)
            else:
                self.daily_streak = 1  # Seri kırıldı
        else:
            self.daily_streak = 1

        self.last_played_date = today
        self.save(update_fields=["daily_streak", "last_played_date"])

    def record_event(self, category: str, correct: bool):
        """Oyun olayını kaydet ve becerileri güncelle"""
        stats = self.stats or {}
        c = stats.get(category, {"correct": 0, "total": 0})
        c["total"] += 1
        if correct:
            c["correct"] += 1
        stats[category] = c
        self.stats = stats

        # Beceri güncellemesi
        delta = 2 if correct else -1
        if category.lower() in ("ticaret", "trade"):
            self.skill_trade = max(0, min(100, self.skill_trade + delta))
        elif category.lower() in ("yatırım", "investment"):
            self.skill_invest = max(0, min(100, self.skill_invest + delta))
        elif category.lower() in ("bütçe", "budget"):
            self.skill_budget = max(0, min(100, self.skill_budget + delta))
        elif category.lower() in ("muhasebe", "accounting"):
            self.skill_accounting = max(0, min(100, self.skill_accounting + delta))
        else:
            self.skill_education = max(0, min(100, self.skill_education + delta))

        self.games_played += 1
        self.updated_at = timezone.now()
        self.save(
            update_fields=[
                "stats",
                "skill_trade",
                "skill_invest",
                "skill_budget",
                "skill_education",
                "skill_accounting",
                "games_played",
                "updated_at",
            ]
        )


class Tournament(models.Model):
    """E-Spor turnuvaları"""

    TOURNAMENT_TYPES = [
        ("ranked", "Dereceli"),
        ("casual", "Günlük"),
        ("championship", "Şampiyonluk"),
        ("special", "Özel Etkinlik"),
    ]

    STATUS_CHOICES = [
        ("upcoming", "Yaklaşan"),
        ("registration", "Kayıt Açık"),
        ("ongoing", "Devam Ediyor"),
        ("finished", "Bitti"),
        ("cancelled", "İptal"),
    ]

    name = models.CharField(max_length=200, verbose_name="Turnuva Adı")
    description = models.TextField(blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="tournaments")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True)

    tournament_type = models.CharField(
        max_length=20, choices=TOURNAMENT_TYPES, default="casual"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")

    # Tarihler
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Katılım
    max_participants = models.IntegerField(
        default=128, validators=[MinValueValidator(2)]
    )
    entry_fee_coins = models.IntegerField(
        default=0, verbose_name="Katılım Ücreti (Altın)"
    )
    entry_fee_gems = models.IntegerField(
        default=0, verbose_name="Katılım Ücreti (Elmas)"
    )

    # Ödüller
    prize_pool_coins = models.IntegerField(default=10000)
    prize_pool_gems = models.IntegerField(default=0)
    prize_distribution = models.JSONField(
        default=dict, help_text="1st: 50%, 2nd: 30%, 3rd: 20%"
    )

    # Kurallar
    rules = models.TextField(blank=True)
    bracket_type = models.CharField(
        max_length=20,
        default="single_elimination",
        choices=[
            ("single_elimination", "Eleme"),
            ("double_elimination", "Çift Eleme"),
            ("round_robin", "Herkes Herkesle"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tournaments",
    )

    class Meta:
        verbose_name = "E-Spor Turnuvası"
        verbose_name_plural = "E-Spor Turnuvaları"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class TournamentParticipant(models.Model):
    """Turnuva katılımcıları"""

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="participants"
    )
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tournament_participations",
    )

    registered_at = models.DateTimeField(auto_now_add=True)
    seed = models.IntegerField(null=True, blank=True, help_text="Turnuva kura numarası")
    final_rank = models.IntegerField(null=True, blank=True)
    total_score = models.IntegerField(default=0)
    prizes_won = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Turnuva Katılımcısı"
        verbose_name_plural = "Turnuva Katılımcıları"
        unique_together = ["tournament", "player"]
        ordering = ["tournament", "seed"]

    def __str__(self):
        return f"{self.player.username} - {self.tournament.name}"


class Match(models.Model):
    """Turnuva maçları"""

    STATUS_CHOICES = [
        ("scheduled", "Planlandı"),
        ("live", "Canlı"),
        ("finished", "Bitti"),
        ("forfeit", "Hükmen"),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="matches",
        null=True,
        blank=True,
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    player1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_player1",
    )
    player2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_player2",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    scheduled_time = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Sonuçlar
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_matches",
    )

    # Replay ve detaylar
    replay_data = models.JSONField(default=dict, blank=True)
    match_stats = models.JSONField(default=dict, blank=True)

    # Elo değişimi
    elo_change_player1 = models.IntegerField(default=0)
    elo_change_player2 = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Maç"
        verbose_name_plural = "Maçlar"
        ordering = ["-scheduled_time"]

    def __str__(self):
        p2_name = self.player2.username if self.player2 else "BOT"
        return f"{self.player1.username} vs {p2_name} ({self.get_status_display()})"


class DailyQuest(models.Model):
    """Günlük görevler - bağımlılık yaratma"""

    QUEST_TYPES = [
        ("play_games", "Oyun Oyna"),
        ("win_games", "Oyun Kazan"),
        ("earn_score", "Puan Kazan"),
        ("complete_tutorial", "Eğitim Tamamla"),
        ("trade_items", "Takas Yap"),
    ]

    quest_type = models.CharField(max_length=30, choices=QUEST_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_value = models.IntegerField(default=1, verbose_name="Hedef Değer")

    # Ödüller
    reward_xp = models.IntegerField(default=100)
    reward_coins = models.IntegerField(default=500)
    reward_gems = models.IntegerField(default=0)

    # Sıklık
    is_daily = models.BooleanField(default=True)
    is_weekly = models.BooleanField(default=False)
    difficulty_level = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Günlük Görev"
        verbose_name_plural = "Günlük Görevler"
        ordering = ["difficulty_level", "title"]

    def __str__(self):
        return f"{self.title} ({self.get_quest_type_display()})"


class PlayerQuest(models.Model):
    """Oyuncunun quest ilerleme kaydı"""

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quests"
    )
    quest = models.ForeignKey(DailyQuest, on_delete=models.CASCADE)

    current_value = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Oyuncu Görevi"
        verbose_name_plural = "Oyuncu Görevleri"
        unique_together = ["player", "quest", "assigned_at"]
        ordering = ["-assigned_at"]

    def __str__(self):
        status = (
            "✓"
            if self.is_completed
            else f"{self.current_value}/{self.quest.target_value}"
        )
        return f"{self.player.username} - {self.quest.title} ({status})"

    def check_completion(self):
        """Quest tamamlandı mı kontrol et"""
        if not self.is_completed and self.current_value >= self.quest.target_value:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()

            # Ödülleri ver
            profile = self.player.player_profile
            profile.add_xp(self.quest.reward_xp)
            profile.coins += self.quest.reward_coins
            profile.gems += self.quest.reward_gems
            profile.save(update_fields=["coins", "gems"])

            return True
        return False


class Item(models.Model):
    """Oyun içi eşyalar"""

    ITEM_TYPES = [
        ("skin", "Görünüm"),
        ("boost", "Güçlendirici"),
        ("badge", "Rozet"),
        ("avatar", "Avatar"),
        ("effect", "Efekt"),
    ]

    RARITY_CHOICES = [
        ("common", "Yaygın"),
        ("rare", "Nadir"),
        ("epic", "Epik"),
        ("legendary", "Efsanevi"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default="common")

    price_coins = models.IntegerField(default=0)
    price_gems = models.IntegerField(default=0)

    # Etki
    effect_data = models.JSONField(
        default=dict, help_text="XP boost, coin multiplier vb."
    )
    duration_hours = models.IntegerField(default=0, help_text="0 = kalıcı")

    is_tradeable = models.BooleanField(default=True)
    is_purchasable = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Eşya"
        verbose_name_plural = "Eşyalar"
        ordering = ["rarity", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class PlayerInventory(models.Model):
    """Oyuncu envanteri"""

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventory"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    acquired_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_equipped = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Oyuncu Envanteri"
        verbose_name_plural = "Oyuncu Envanterleri"
        unique_together = ["player", "item"]

    def __str__(self):
        return f"{self.player.username} - {self.item.name} (x{self.quantity})"


class GameSession(models.Model):
    """Oyun oturumu - match history"""

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="game_sessions"
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)

    score = models.IntegerField(default=0)
    is_victory = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)
    coins_earned = models.IntegerField(default=0)

    # Detaylar
    session_data = models.JSONField(
        default=dict, blank=True, help_text="Oyun içi events, actions vb."
    )

    class Meta:
        verbose_name = "Oyun Oturumu"
        verbose_name_plural = "Oyun Oturumları"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.player.username} - {self.game.name} ({self.score} puan)"


class Leaderboard(models.Model):
    """Sıralama tabloları (cached)"""

    LEADERBOARD_TYPES = [
        ("global", "Global"),
        ("season", "Sezonluk"),
        ("weekly", "Haftalık"),
        ("daily", "Günlük"),
        ("game_specific", "Oyuna Özel"),
    ]

    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True)

    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()
    score = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sıralama"
        verbose_name_plural = "Sıralamalar"
        unique_together = ["leaderboard_type", "game", "season", "player"]
        ordering = ["rank"]
        indexes = [
            models.Index(fields=["leaderboard_type", "rank"]),
            models.Index(fields=["season", "rank"]),
        ]

    def __str__(self):
        return f"#{self.rank} {self.player.username} ({self.score})"


class Friend(models.Model):
    """Arkadaşlık sistemi"""

    STATUS_CHOICES = [
        ("pending", "Bekliyor"),
        ("accepted", "Kabul Edildi"),
        ("blocked", "Engellendi"),
    ]

    from_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )
    to_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Arkadaşlık"
        verbose_name_plural = "Arkadaşlıklar"
        unique_together = ["from_player", "to_player"]

    def __str__(self):
        return f"{self.from_player.username} → {self.to_player.username} ({self.get_status_display()})"


class Team(models.Model):
    """Takım sistemi (team-based games için)"""

    name = models.CharField(max_length=100, unique=True)
    tag = models.CharField(
        max_length=10, unique=True, help_text="Kısa takım etiketi (örn: FIN)"
    )
    description = models.TextField(blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_teams"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="teams", through="TeamMembership"
    )

    team_rank = models.CharField(max_length=20, default="bronze")
    team_elo = models.IntegerField(default=1000)

    logo_icon = models.CharField(max_length=50, default="🛡️")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Takım"
        verbose_name_plural = "Takımlar"
        ordering = ["-team_elo"]

    def __str__(self):
        return f"[{self.tag}] {self.name}"


class TeamMembership(models.Model):
    """Takım üyeliği"""

    ROLE_CHOICES = [
        ("owner", "Kurucu"),
        ("captain", "Kaptan"),
        ("member", "Üye"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Takım Üyeliği"
        verbose_name_plural = "Takım Üyelikleri"
        unique_together = ["team", "player"]

    def __str__(self):
        return f"{self.player.username} @ {self.team.name} ({self.get_role_display()})"


# Signals
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_profile(sender, instance, created, **kwargs):
    """Kullanıcı oluşturulduğunda PlayerProfile otomatik oluştur"""
    if created:
        PlayerProfile.objects.get_or_create(user=instance)
