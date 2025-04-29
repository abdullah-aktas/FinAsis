# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from virtual_company.models import VirtualCompany

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    virtual_company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class Game(BaseModel):
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
        verbose_name = 'Oyun'
        verbose_name_plural = 'Oyunlar'

class GameScore(BaseModel):
    """Oyun Skoru"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
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
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
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
