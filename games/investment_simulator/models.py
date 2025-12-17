# -*- coding: utf-8 -*-
"""
Yatırım Simülatörü Modelleri
Gerçekçi portföy yönetimi ve yatırım simülasyonu
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class InvestmentProfile(models.Model):
    """Oyuncunun yatırım profili"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="investment_profile",
        verbose_name="Kullanıcı"
    )
    
    # Başlangıç sermayesi
    initial_capital = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('100000.00'),
        verbose_name="Başlangıç Sermayesi"
    )
    
    # Mevcut durum
    cash_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('100000.00'),
        verbose_name="Nakit Bakiye"
    )
    
    # İstatistikler
    total_invested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Toplam Yatırım"
    )
    
    total_profit_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Toplam Kar/Zarar"
    )
    
    total_return_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Toplam Getiri %"
    )
    
    # Progression
    level = models.PositiveIntegerField(default=1, verbose_name="Seviye")
    xp = models.PositiveIntegerField(default=0, verbose_name="Deneyim Puanı")
    xp_to_next_level = models.PositiveIntegerField(default=1000, verbose_name="Sonraki Seviyeye XP")
    
    # Beceriler (0-100)
    skill_analysis = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Analiz Becerisi"
    )
    skill_timing = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Zamanlama Becerisi"
    )
    skill_risk_management = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Risk Yönetimi"
    )
    skill_diversification = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Çeşitlendirme"
    )
    
    # İstatistikler
    total_transactions = models.PositiveIntegerField(default=0, verbose_name="Toplam İşlem")
    successful_trades = models.PositiveIntegerField(default=0, verbose_name="Başarılı İşlem")
    failed_trades = models.PositiveIntegerField(default=0, verbose_name="Başarısız İşlem")
    win_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Kazanma Oranı %"
    )
    
    # En iyi performanslar
    best_daily_return = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="En İyi Günlük Getiri %"
    )
    best_weekly_return = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="En İyi Haftalık Getiri %"
    )
    best_monthly_return = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="En İyi Aylık Getiri %"
    )
    
    # Streak
    daily_streak = models.PositiveIntegerField(default=0, verbose_name="Günlük Seri")
    last_played_date = models.DateField(null=True, blank=True, verbose_name="Son Oynama Tarihi")
    
    # Meta
    preferences = models.JSONField(default=dict, blank=True, verbose_name="Tercihler")
    stats = models.JSONField(default=dict, blank=True, verbose_name="İstatistikler")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    
    class Meta:
        verbose_name = "Yatırım Profili"
        verbose_name_plural = "Yatırım Profilleri"
        ordering = ["-total_return_percentage", "-total_profit_loss"]
    
    def __str__(self):
        return f"{self.user.username} - {self.total_return_percentage}% Getiri"
    
    @property
    def portfolio_value(self):
        """Portföyün toplam değeri"""
        from .models import Portfolio
        holdings = Portfolio.objects.filter(profile=self)
        total = self.cash_balance
        for holding in holdings:
            total += holding.current_value
        return total
    
    @property
    def total_profit_loss_calculated(self):
        """Hesaplanan kar/zarar"""
        return self.portfolio_value - self.initial_capital
    
    def add_xp(self, amount):
        """XP ekle ve level güncelle"""
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = int(1000 * (1.3 ** (self.level - 1)))
            # Level bonusu
            self.cash_balance += Decimal(str(1000 * self.level))
        self.save(update_fields=['xp', 'level', 'xp_to_next_level', 'cash_balance'])
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        if self.total_transactions > 0:
            self.win_rate = Decimal(str((self.successful_trades / self.total_transactions) * 100))
        
        total_value = self.portfolio_value
        if self.initial_capital > 0:
            self.total_return_percentage = Decimal(
                str(((total_value - self.initial_capital) / self.initial_capital) * 100)
            )
        
        self.total_profit_loss = self.total_profit_loss_calculated
        self.save(update_fields=['win_rate', 'total_return_percentage', 'total_profit_loss'])


class Asset(models.Model):
    """Yatırım araçları (hisse, tahvil, altın, vb.)"""
    
    ASSET_TYPES = [
        ('stock', 'Hisse Senedi'),
        ('bond', 'Tahvil'),
        ('gold', 'Altın'),
        ('crypto', 'Kripto Para'),
        ('forex', 'Döviz'),
        ('fund', 'Yatırım Fonu'),
        ('realestate', 'Gayrimenkul Fonu'),
        ('commodity', 'Emtia'),
    ]
    
    RISK_LEVELS = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('very_high', 'Çok Yüksek'),
    ]
    
    # Temel bilgiler
    name = models.CharField(max_length=200, verbose_name="Araç Adı")
    symbol = models.CharField(max_length=20, unique=True, verbose_name="Sembol")
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES, verbose_name="Araç Tipi")
    
    # Risk ve getiri
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, verbose_name="Risk Seviyesi")
    base_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Başlangıç Fiyatı"
    )
    current_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Güncel Fiyat"
    )
    
    # Piyasa özellikleri
    volatility = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.02'),
        verbose_name="Volatilite",
        help_text="Fiyat değişkenliği (0.02 = %2)"
    )
    
    expected_return = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        verbose_name="Beklenen Getiri %",
        help_text="Yıllık beklenen getiri yüzdesi"
    )
    
    # Trend ve momentum
    trend = models.CharField(
        max_length=20,
        choices=[('bullish', 'Yükseliş'), ('bearish', 'Düşüş'), ('neutral', 'Nötr')],
        default='neutral',
        verbose_name="Trend"
    )
    
    momentum = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Momentum",
        help_text="Fiyat momentumu (-100 ile +100 arası)"
    )
    
    # Piyasa verileri
    market_cap = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Piyasa Değeri"
    )
    
    volume_24h = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="24 Saatlik Hacim"
    )
    
    # Fiyat geçmişi (JSON)
    price_history = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Fiyat Geçmişi",
        help_text="Son 100 fiyat güncellemesi"
    )
    
    # Meta
    description = models.TextField(blank=True, verbose_name="Açıklama")
    icon = models.CharField(max_length=50, default='graph-up', verbose_name="İkon")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Yatırım Aracı"
        verbose_name_plural = "Yatırım Araçları"
        ordering = ['asset_type', 'name']
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"
    
    def update_price(self, new_price):
        """Fiyatı güncelle ve geçmişe ekle"""
        old_price = self.current_price
        self.current_price = new_price
        
        # Fiyat geçmişine ekle
        if not self.price_history:
            self.price_history = []
        
        self.price_history.append({
            'price': float(new_price),
            'timestamp': timezone.now().isoformat(),
            'change': float(new_price - old_price),
            'change_percent': float(((new_price - old_price) / old_price) * 100) if old_price > 0 else 0
        })
        
        # Son 100 kaydı tut
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
        
        # Trend ve momentum hesapla
        self._calculate_trend_and_momentum()
        
        self.save(update_fields=['current_price', 'price_history', 'trend', 'momentum', 'updated_at'])
    
    def _calculate_trend_and_momentum(self):
        """Trend ve momentum hesapla"""
        if len(self.price_history) < 5:
            return
        
        recent_prices = [p['price'] for p in self.price_history[-20:]]
        
        # Trend: Son 20 fiyatın ortalaması
        avg_short = sum(recent_prices[-5:]) / 5
        avg_long = sum(recent_prices[-20:]) / 20
        
        if avg_short > avg_long * 1.02:
            self.trend = 'bullish'
        elif avg_short < avg_long * 0.98:
            self.trend = 'bearish'
        else:
            self.trend = 'neutral'
        
        # Momentum: Son 5 fiyat değişimi
        if len(recent_prices) >= 5:
            change = ((recent_prices[-1] - recent_prices[-5]) / recent_prices[-5]) * 100
            self.momentum = Decimal(str(min(100, max(-100, change))))


class Portfolio(models.Model):
    """Oyuncunun portföyünde bulunan yatırımlar"""
    
    profile = models.ForeignKey(
        InvestmentProfile,
        on_delete=models.CASCADE,
        related_name='holdings',
        verbose_name="Profil"
    )
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='portfolios',
        verbose_name="Araç"
    )
    
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name="Miktar"
    )
    
    average_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Ortalama Maliyet",
        help_text="Birim başına ortalama alış fiyatı"
    )
    
    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Toplam Maliyet"
    )
    
    # Meta
    first_purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="İlk Alış")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")
    
    class Meta:
        verbose_name = "Portföy"
        verbose_name_plural = "Portföyler"
        unique_together = ['profile', 'asset']
        ordering = ['-total_cost']
    
    def __str__(self):
        return f"{self.profile.user.username} - {self.asset.symbol} ({self.quantity})"
    
    @property
    def current_value(self):
        """Güncel değer"""
        return self.quantity * self.asset.current_price
    
    @property
    def profit_loss(self):
        """Kar/Zarar"""
        return self.current_value - self.total_cost
    
    @property
    def profit_loss_percentage(self):
        """Kar/Zarar yüzdesi"""
        if self.total_cost > 0:
            return ((self.current_value - self.total_cost) / self.total_cost) * 100
        return Decimal('0.00')


class Transaction(models.Model):
    """Yatırım işlemleri (alış/satış)"""
    
    TRANSACTION_TYPES = [
        ('buy', 'Alış'),
        ('sell', 'Satış'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    profile = models.ForeignKey(
        InvestmentProfile,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Profil"
    )
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Araç"
    )
    
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        verbose_name="İşlem Tipi"
    )
    
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name="Miktar"
    )
    
    price_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Birim Fiyat"
    )
    
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Toplam Tutar"
    )
    
    # Komisyon ve masraflar
    commission = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Komisyon"
    )
    
    # Sonuç
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='completed',
        verbose_name="Durum"
    )
    
    profit_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Kar/Zarar",
        help_text="Satış işlemlerinde hesaplanır"
    )
    
    # Meta
    notes = models.TextField(blank=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="İşlem Tarihi")
    
    class Meta:
        verbose_name = "İşlem"
        verbose_name_plural = "İşlemler"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', '-created_at']),
            models.Index(fields=['asset', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.profile.user.username} - {self.get_transaction_type_display()} {self.asset.symbol}"


class MarketEvent(models.Model):
    """Piyasa olayları (haberler, krizler, vb.)"""
    
    EVENT_TYPES = [
        ('news', 'Haber'),
        ('crisis', 'Kriz'),
        ('boom', 'Patlama'),
        ('regulation', 'Düzenleme'),
        ('earnings', 'Kazanç Açıklaması'),
        ('merger', 'Birleşme'),
    ]
    
    IMPACT_LEVELS = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('critical', 'Kritik'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Başlık")
    description = models.TextField(verbose_name="Açıklama")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name="Olay Tipi")
    impact_level = models.CharField(max_length=20, choices=IMPACT_LEVELS, verbose_name="Etki Seviyesi")
    
    # Etkilenen araçlar
    affected_assets = models.ManyToManyField(
        Asset,
        related_name='market_events',
        blank=True,
        verbose_name="Etkilenen Araçlar"
    )
    
    # Fiyat etkisi
    price_impact_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Fiyat Etkisi %",
        help_text="Pozitif = artış, Negatif = düşüş"
    )
    
    # Zamanlama
    event_date = models.DateTimeField(verbose_name="Olay Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Piyasa Olayı"
        verbose_name_plural = "Piyasa Olayları"
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"


class InvestmentLeaderboard(models.Model):
    """Yatırım simülatörü liderlik tablosu"""
    
    LEADERBOARD_TYPES = [
        ('global', 'Global'),
        ('weekly', 'Haftalık'),
        ('monthly', 'Aylık'),
        ('all_time', 'Tüm Zamanlar'),
    ]
    
    profile = models.ForeignKey(
        InvestmentProfile,
        on_delete=models.CASCADE,
        related_name='leaderboard_entries',
        verbose_name="Profil"
    )
    
    leaderboard_type = models.CharField(
        max_length=20,
        choices=LEADERBOARD_TYPES,
        verbose_name="Liderlik Tipi"
    )
    
    rank = models.PositiveIntegerField(verbose_name="Sıra")
    
    # Metrikler
    total_return_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Toplam Getiri %"
    )
    
    portfolio_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Portföy Değeri"
    )
    
    # Zaman aralığı
    period_start = models.DateField(null=True, blank=True, verbose_name="Dönem Başlangıcı")
    period_end = models.DateField(null=True, blank=True, verbose_name="Dönem Bitişi")
    
    # Meta
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    
    class Meta:
        verbose_name = "Liderlik Tablosu"
        verbose_name_plural = "Liderlik Tabloları"
        unique_together = ['leaderboard_type', 'profile', 'period_start', 'period_end']
        ordering = ['leaderboard_type', 'rank']
        indexes = [
            models.Index(fields=['leaderboard_type', 'rank']),
        ]
    
    def __str__(self):
        return f"#{self.rank} {self.profile.user.username} - {self.total_return_percentage}%"

