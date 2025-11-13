# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    # Use string reference to avoid hard import dependency on optional app
    virtual_company = models.ForeignKey('virtual_company.VirtualCompany', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class UrsinaGame(BaseModel):
    """Oyun"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    game_type = models.CharField(max_length=20, choices=[
        ('pygame', 'Pygame'),
        ('ursina', 'Ursina'),
    ])
    scene_file = models.FileField(upload_to='games/')
    max_score = models.IntegerField(default=100)
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Kolay'),
        ('medium', 'Orta'),
        ('hard', 'Zor'),
    ])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Ursina Oyunu'
        verbose_name_plural = 'Ursina Oyunları'

class GameScore(BaseModel):
    """Oyun Skoru"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(UrsinaGame, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completion_percentage = models.FloatField(default=0)
    played_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(help_text='Saniye cinsinden süre')

    def __str__(self):
        return f"{self.user.username} - {self.game.title}"

    class Meta:
        verbose_name = 'Oyun Skoru'
        verbose_name_plural = 'Oyun Skorları'

class GameAchievement(BaseModel):
    """Oyun Başarısı"""
    game = models.ForeignKey(UrsinaGame, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    criteria = models.TextField(help_text='Başarı kazanma kriterleri')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.game.title} - {self.title}"

    class Meta:
        verbose_name = 'Oyun Başarısı'
        verbose_name_plural = 'Oyun Başarıları'

class UserGameAchievement(BaseModel):
    """Kullanıcı Oyun Başarısı"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.ForeignKey(GameAchievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"

    class Meta:
        verbose_name = 'Kullanıcı Oyun Başarısı'
        verbose_name_plural = 'Kullanıcı Oyun Başarıları'

class GameState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    virtual_company = models.ForeignKey('virtual_company.VirtualCompany', on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Game State"

class UrsinaPlayer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30, unique=True)
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    gems = models.IntegerField(default=0)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname

class PlayerWallet(models.Model):
    player = models.OneToOneField(UrsinaPlayer, on_delete=models.CASCADE)
    coins = models.IntegerField(default=0)
    gems = models.IntegerField(default=0)
    tokens = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

class UrsinaGameSession(models.Model):
    player = models.ForeignKey(UrsinaPlayer, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    duration = models.IntegerField(default=0, help_text='Saniye cinsinden')
    # Oyun içi istatistikler, json olarak tutulabilir
    stats = models.JSONField(default=dict, blank=True)

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    prize_pool = models.IntegerField(default=0)
    participants = models.ManyToManyField(UrsinaPlayer, related_name='tournaments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Achievement(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField(default=0)
    icon = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PlayerAchievement(models.Model):
    player = models.ForeignKey(UrsinaPlayer, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'achievement')
