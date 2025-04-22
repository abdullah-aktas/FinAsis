from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Game(models.Model):
    """Finansal simülasyon oyunu modeli"""
    name = models.CharField(_("Oyun Adı"), max_length=100)
    description = models.TextField(_("Açıklama"))
    start_date = models.DateTimeField(_("Başlangıç Tarihi"))
    end_date = models.DateTimeField(_("Bitiş Tarihi"))
    is_active = models.BooleanField(_("Aktif mi?"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Oyun")
        verbose_name_plural = _("Oyunlar")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Player(models.Model):
    """Oyun oyuncusu modeli"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_players')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    company_name = models.CharField(_("Şirket Adı"), max_length=100)
    initial_balance = models.DecimalField(_("Başlangıç Bakiyesi"), max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(_("Mevcut Bakiye"), max_digits=10, decimal_places=2)
    score = models.IntegerField(_("Puan"), default=0)
    is_active = models.BooleanField(_("Aktif mi?"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Oyuncu")
        verbose_name_plural = _("Oyuncular")
        ordering = ['-score']

    def __str__(self):
        return f"{self.user.username} - {self.company_name}"

class Transaction(models.Model):
    """Oyuncu işlemleri modeli"""
    TRANSACTION_TYPES = (
        ('income', _('Gelir')),
        ('expense', _('Gider')),
        ('investment', _('Yatırım')),
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(_("İşlem Tipi"), max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(_("Miktar"), max_digits=10, decimal_places=2)
    description = models.TextField(_("Açıklama"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("İşlem")
        verbose_name_plural = _("İşlemler")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.player.company_name} - {self.get_transaction_type_display()}"

class Challenge(models.Model):
    """Oyun görevleri modeli"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='challenges')
    title = models.CharField(_("Başlık"), max_length=200)
    description = models.TextField(_("Açıklama"))
    points = models.IntegerField(_("Puan"))
    is_completed = models.BooleanField(_("Tamamlandı mı?"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Görev")
        verbose_name_plural = _("Görevler")
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class PlayerChallenge(models.Model):
    """Oyuncu görev takibi modeli"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='player_challenges')
    is_completed = models.BooleanField(_("Tamamlandı mı?"), default=False)
    completed_at = models.DateTimeField(_("Tamamlanma Tarihi"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Oyuncu Görevi")
        verbose_name_plural = _("Oyuncu Görevleri")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.player.company_name} - {self.challenge.title}" 