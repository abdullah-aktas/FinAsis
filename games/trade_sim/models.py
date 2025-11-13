from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class City(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    sectors = models.JSONField(default=list)  # ['finans', 'tarım', 'teknoloji', ...]
    market_size = models.IntegerField(default=1000)
    coordinates = models.JSONField(default=dict)  # {'x': 0, 'y': 0}
    image = models.ImageField(upload_to='city_images/', null=True, blank=True)
    neighbors = models.ManyToManyField('self', blank=True, symmetrical=True)  # Komşu şehirler
    sector_markets = models.JSONField(default=dict, blank=True)  # {'finans': {'price': 100, 'demand': 80}, ...}
    weather = models.CharField(max_length=20, default='gunesli', blank=True)  # güneşli, yağmurlu, sisli, karlı, vb.
    time_of_day = models.CharField(max_length=10, default='oglen', blank=True)  # sabah, oglen, aksam, gece

    def __str__(self):
        return self.name 

class Character(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='characters')
    skills = models.JSONField(default=dict, blank=True)  # {'ticaret': 1, 'pazarlık': 2, ...}
    story_state = models.JSONField(default=dict, blank=True)  # {'ana_gorev': 'basladi', ...}
    choices = models.JSONField(default=dict, blank=True)  # {'ilk_secenek': 'A', ...}
    score = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})" 

class Quest(models.Model):
    QUEST_TYPE_CHOICES = [
        ('main', 'Ana Hikaye'),
        ('side', 'Yan Görev'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    quest_type = models.CharField(max_length=10, choices=QUEST_TYPE_CHOICES, default='side')
    requirements = models.JSONField(default=dict, blank=True)  # {'ticaret': 5, ...}
    rewards = models.JSONField(default=dict, blank=True)  # {'coins': 100, 'xp': 10}
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CharacterQuest(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='character_quests')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='character_quests')
    progress = models.JSONField(default=dict, blank=True)  # {'ticaret': 2, ...}
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.character.name} - {self.quest.name}" 

@receiver(post_save, sender=CharacterQuest)
def character_quest_completed(sender, instance, created, **kwargs):
    if instance.is_completed and not created:
        user = instance.character.user
        message = f"'{instance.quest.name}' görevi tamamlandı!"
        create_notification(user, message, notification_type='success')

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    prize_pool = models.JSONField(default=dict, blank=True)  # {'coins': 10000, 'badge': 'champion'}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TournamentEntry(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='entries')
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='tournament_entries')
    score = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    reward_claimed = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character.name} - {self.tournament.name}" 

@receiver(post_save, sender=TournamentEntry)
def tournament_entry_reward_claimed(sender, instance, created, **kwargs):
    if instance.reward_claimed and not created:
        user = instance.character.user
        message = f"{instance.tournament.name} turnuvasında ödül kazandın!"
        create_notification(user, message, notification_type='success')

class GameNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=[('success', 'Başarı'), ('info', 'Bilgi'), ('warning', 'Uyarı')], default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}" 

def create_notification(user, message, notification_type='info'):
    from .models import GameNotification
    GameNotification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type
    ) 

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.room}] {self.user}: {self.message[:30]}" 

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price = models.IntegerField(default=100)
    unit = models.CharField(max_length=20, default='adet')
    category = models.CharField(max_length=50, default='genel')

    def __str__(self):
        return self.name

class CityMarket(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='markets')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='city_markets')
    price = models.IntegerField(default=100)
    supply = models.IntegerField(default=100)
    demand = models.IntegerField(default=100)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('city', 'product')

    def __str__(self):
        return f"{self.city.name} - {self.product.name}" 

class QrReward(models.Model):
    code = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=255)
    reward = models.JSONField(default=dict)  # {'coins': 100, 'badge': 'market_explorer'}
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.description}"

class UserQrReward(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qr_reward = models.ForeignKey(QrReward, on_delete=models.CASCADE)
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'qr_reward')

    def __str__(self):
        return f"{self.user.username} - {self.qr_reward.code}"


# Ensure every new user gets a default Character to start playing
@receiver(post_save, sender=get_user_model())
def create_default_character_for_user(sender, instance, created, **kwargs):
    if not created:
        return
    # Pick first available city if exists
    default_city = City.objects.order_by('id').first()
    Character.objects.create(
        user=instance,
        name=f"{getattr(instance, 'username', 'Oyuncu')} Trader",
        city=default_city,
        skills={},
        story_state={},
        choices={},
    )