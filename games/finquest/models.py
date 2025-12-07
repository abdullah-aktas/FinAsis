"""
FinQuest 3D - Modern 3D Finansal Macera Oyunu Modelleri
"""
from django.db import models
from django.conf import settings


class FinQuestCharacter(models.Model):
    """FinQuest oyuncu karakteri"""

    DIFFICULTY_CHOICES = [
        (1, "Acemi"),
        (2, "Normal"),
        (3, "Zor"),
        (4, "Uzman"),
        (5, "Efsane"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="finquest_characters",
    )
    name = models.CharField(max_length=100, default="Maceraperest")

    # Lokasyon
    current_city = models.CharField(max_length=50, default="Mardin")
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=1.0)
    position_z = models.FloatField(default=0.0)

    # İstatistikler
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)
    health = models.IntegerField(default=100)
    energy = models.IntegerField(default=100)
    money = models.IntegerField(default=10000)

    # Beceriler (0-100)
    skill_trading = models.IntegerField(default=10)
    skill_negotiation = models.IntegerField(default=10)
    skill_accounting = models.IntegerField(default=10)
    skill_investing = models.IntegerField(default=10)
    skill_management = models.IntegerField(default=10)

    # Progression
    quests_completed = models.IntegerField(default=0)
    cities_explored = models.JSONField(default=list)
    achievements_unlocked = models.JSONField(default=list)

    # Oyun durumu
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=2)
    is_active = models.BooleanField(default=True)
    last_played = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FinQuest Karakter"
        verbose_name_plural = "FinQuest Karakterler"
        ordering = ["-level", "-xp"]

    def __str__(self):
        return f"{self.name} (Lvl {self.level}, {self.user.username})"


class FinQuestItem(models.Model):
    """FinQuest oyun içi eşyalar"""

    ITEM_TYPES = [
        ("equipment", "Ekipman"),
        ("consumable", "Sarf Malzeme"),
        ("quest", "Görev Eşyası"),
        ("cosmetic", "Kozmetik"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)

    # Değer
    buy_price = models.IntegerField(default=100)
    sell_price = models.IntegerField(default=50)

    # Efektler
    health_bonus = models.IntegerField(default=0)
    energy_bonus = models.IntegerField(default=0)
    skill_bonuses = models.JSONField(default=dict)

    # Model ve görsel
    model_path = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=50, default="📦")

    is_tradeable = models.BooleanField(default=True)
    is_stackable = models.BooleanField(default=True)
    max_stack = models.IntegerField(default=99)

    class Meta:
        verbose_name = "FinQuest Eşya"
        verbose_name_plural = "FinQuest Eşyalar"

    def __str__(self):
        return f"{self.icon} {self.name}"


class FinQuestInventory(models.Model):
    """Karakter envanteri"""

    character = models.ForeignKey(
        FinQuestCharacter, on_delete=models.CASCADE, related_name="inventory"
    )
    item = models.ForeignKey(FinQuestItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_equipped = models.BooleanField(default=False)

    class Meta:
        unique_together = ["character", "item"]
        verbose_name = "Envanter"
        verbose_name_plural = "Envanter"

    def __str__(self):
        return f"{self.character.name} - {self.item.name} (x{self.quantity})"


class FinQuestQuest(models.Model):
    """FinQuest görevleri"""

    QUEST_TYPES = [
        ("tutorial", "Öğretici"),
        ("main", "Ana Hikaye"),
        ("side", "Yan Görev"),
        ("daily", "Günlük"),
        ("challenge", "Meydan Okuma"),
    ]

    quest_type = models.CharField(max_length=20, choices=QUEST_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()

    # Gereksinimler
    required_level = models.IntegerField(default=1)
    required_city = models.CharField(max_length=50, blank=True)
    prerequisites = models.JSONField(default=list)

    # Hedefler
    objectives = models.JSONField(default=list)

    # Ödüller
    reward_xp = models.IntegerField(default=100)
    reward_money = models.IntegerField(default=500)
    reward_items = models.JSONField(default=list)

    # Zorluk
    difficulty_level = models.IntegerField(default=1)
    time_limit_minutes = models.IntegerField(default=0, help_text="0 = sınırsız")

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "FinQuest Görev"
        verbose_name_plural = "FinQuest Görevler"
        ordering = ["quest_type", "required_level"]

    def __str__(self):
        return f"{self.title} ({self.get_quest_type_display()})"


class FinQuestPlayerQuest(models.Model):
    """Oyuncunun görev ilerlemesi"""

    character = models.ForeignKey(
        FinQuestCharacter, on_delete=models.CASCADE, related_name="active_quests"
    )
    quest = models.ForeignKey(FinQuestQuest, on_delete=models.CASCADE)

    progress = models.JSONField(default=dict)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["character", "quest"]
        verbose_name = "Karakter Görevi"
        verbose_name_plural = "Karakter Görevleri"

    def __str__(self):
        status = "✓" if self.is_completed else "⏳"
        return f"{status} {self.character.name} - {self.quest.title}"


class FinQuestNPC(models.Model):
    """Non-Player Characters (AI karakterler)"""

    NPC_TYPES = [
        ("merchant", "Tüccar"),
        ("banker", "Bankacı"),
        ("teacher", "Öğretmen"),
        ("quest_giver", "Görev Veren"),
        ("rival", "Rakip"),
    ]

    name = models.CharField(max_length=100)
    npc_type = models.CharField(max_length=20, choices=NPC_TYPES)
    city = models.CharField(max_length=50)

    # AI özelikleri
    ai_intelligence = models.FloatField(default=0.5, help_text="0.0 - 1.0")
    personality = models.CharField(max_length=50, default="neutral")

    # Görünüm
    model_path = models.CharField(max_length=200, blank=True)
    dialogue = models.JSONField(default=list)

    # Ticaret (eğer merchant ise)
    inventory = models.JSONField(default=dict)
    price_multiplier = models.FloatField(default=1.0)

    class Meta:
        verbose_name = "NPC"
        verbose_name_plural = "NPC'ler"

    def __str__(self):
        return f"{self.name} ({self.get_npc_type_display()})"


class FinQuestWorld(models.Model):
    """Şehir/dünya verileri"""

    name = models.CharField(max_length=100)
    description = models.TextField()

    # Lokasyon
    map_data = models.JSONField(default=dict)
    biomes = models.JSONField(default=list)

    # Ekonomi
    economic_level = models.IntegerField(default=1, help_text="1-10")
    tax_rate = models.FloatField(default=0.1)
    market_prices = models.JSONField(default=dict)

    # Hava durumu
    weather = models.CharField(max_length=20, default="sunny")
    time_of_day = models.CharField(max_length=20, default="day")

    is_unlocked = models.BooleanField(default=True)
    unlock_requirement = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Dünya/Şehir"
        verbose_name_plural = "Dünyalar/Şehirler"

    def __str__(self):
        return self.name


class FinQuestEvent(models.Model):
    """Dünya eventleri (random olaylar)"""

    EVENT_TYPES = [
        ("economic", "Ekonomik"),
        ("weather", "Hava Durumu"),
        ("social", "Sosyal"),
        ("quest", "Görev"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # Efektler
    effects = models.JSONField(default=dict)
    duration_minutes = models.IntegerField(default=10)

    # Oluşma şartları
    trigger_conditions = models.JSONField(default=dict)
    probability = models.FloatField(default=0.1, help_text="0.0 - 1.0")

    class Meta:
        verbose_name = "Olay"
        verbose_name_plural = "Olaylar"

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"


class FinQuestSession(models.Model):
    """Oyun oturumu kayıtları"""

    character = models.ForeignKey(
        FinQuestCharacter, on_delete=models.CASCADE, related_name="sessions"
    )

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)

    # Performans
    xp_earned = models.IntegerField(default=0)
    money_earned = models.IntegerField(default=0)
    quests_completed = models.IntegerField(default=0)
    cities_visited = models.IntegerField(default=0)

    # Detaylar
    session_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Oyun Oturumu"
        verbose_name_plural = "Oyun Oturumları"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.character.name} - {self.started_at.strftime('%d.%m.%Y %H:%M')}"
