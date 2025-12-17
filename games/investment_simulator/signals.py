# -*- coding: utf-8 -*-
"""
Yatırım Simülatörü Signal Handlers
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import InvestmentProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_investment_profile(sender, instance, created, **kwargs):
    """Yeni kullanıcı için otomatik yatırım profili oluştur"""
    if created:
        InvestmentProfile.objects.get_or_create(user=instance)
