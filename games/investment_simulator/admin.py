# -*- coding: utf-8 -*-
"""
Yatırım Simülatörü Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    InvestmentProfile,
    Asset,
    Portfolio,
    Transaction,
    MarketEvent,
    InvestmentLeaderboard,
)


@admin.register(InvestmentProfile)
class InvestmentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'level',
        'portfolio_value_display',
        'total_return_percentage',
        'total_profit_loss',
        'win_rate',
        'skill_analysis',
        'daily_streak',
    )
    list_filter = ('level', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'created_at',
        'updated_at',
        'portfolio_value_display',
        'total_profit_loss_calculated',
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Kullanıcı'), {
            'fields': ('user',)
        }),
        (_('Sermaye'), {
            'fields': ('initial_capital', 'cash_balance', 'total_invested')
        }),
        (_('Performans'), {
            'fields': (
                'total_profit_loss',
                'total_return_percentage',
                'portfolio_value_display',
                'total_profit_loss_calculated',
            )
        }),
        (_('Progression'), {
            'fields': ('level', 'xp', 'xp_to_next_level', 'daily_streak', 'last_played_date')
        }),
        (_('Beceriler'), {
            'fields': (
                'skill_analysis',
                'skill_timing',
                'skill_risk_management',
                'skill_diversification',
            )
        }),
        (_('İstatistikler'), {
            'fields': (
                'total_transactions',
                'successful_trades',
                'failed_trades',
                'win_rate',
                'best_daily_return',
                'best_weekly_return',
                'best_monthly_return',
            )
        }),
        (_('Meta'), {
            'fields': ('preferences', 'stats', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def portfolio_value_display(self, obj):
        """Portföy değeri gösterimi"""
        value = obj.portfolio_value
        return f"₺{value:,.2f}"
    portfolio_value_display.short_description = "Portföy Değeri"
    
    def total_profit_loss_calculated(self, obj):
        """Hesaplanan kar/zarar"""
        profit = obj.total_profit_loss_calculated
        color = 'green' if profit >= 0 else 'red'
        return format_html(
            '<span style="color: {};">₺{:,.2f}</span>',
            color,
            profit
        )
    total_profit_loss_calculated.short_description = "Hesaplanan Kar/Zarar"


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'symbol',
        'name',
        'asset_type',
        'risk_level',
        'current_price',
        'price_change_display',
        'trend',
        'momentum',
        'is_active',
    )
    list_filter = ('asset_type', 'risk_level', 'trend', 'is_active', 'created_at')
    search_fields = ('name', 'symbol', 'description')
    readonly_fields = (
        'current_price',
        'price_history',
        'trend',
        'momentum',
        'created_at',
        'updated_at',
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Temel Bilgiler'), {
            'fields': ('name', 'symbol', 'asset_type', 'description', 'icon')
        }),
        (_('Fiyat'), {
            'fields': ('base_price', 'current_price', 'price_history')
        }),
        (_('Risk ve Getiri'), {
            'fields': ('risk_level', 'volatility', 'expected_return')
        }),
        (_('Piyasa'), {
            'fields': ('trend', 'momentum', 'market_cap', 'volume_24h')
        }),
        (_('Durum'), {
            'fields': ('is_active',)
        }),
        (_('Meta'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_change_display(self, obj):
        """Fiyat değişimi gösterimi"""
        if len(obj.price_history) >= 2:
            current = obj.price_history[-1]['price']
            previous = obj.price_history[-2]['price']
            change = current - previous
            change_percent = ((current - previous) / previous) * 100 if previous > 0 else 0
            
            color = 'green' if change >= 0 else 'red'
            arrow = '↑' if change >= 0 else '↓'
            return format_html(
                '<span style="color: {};">{} {:.2f}%</span>',
                color,
                arrow,
                change_percent
            )
        return '-'
    price_change_display.short_description = "Değişim"
    
    actions = ['update_prices', 'create_market_event']
    
    @admin.action(description="Seçili araçların fiyatlarını güncelle")
    def update_prices(self, request, queryset):
        from .market_engine import MarketEngine
        engine = MarketEngine()
        count = 0
        for asset in queryset:
            new_price = engine.calculate_new_price(asset)
            if new_price:
                asset.update_price(new_price)
                count += 1
        self.message_user(request, f"{count} aracın fiyatı güncellendi.")


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'asset',
        'quantity',
        'average_cost',
        'current_value_display',
        'profit_loss_display',
        'profit_loss_percentage_display',
    )
    list_filter = ('asset__asset_type', 'asset__risk_level', 'first_purchased_at')
    search_fields = ('profile__user__username', 'asset__name', 'asset__symbol')
    readonly_fields = (
        'current_value_display',
        'profit_loss_display',
        'profit_loss_percentage_display',
        'first_purchased_at',
        'last_updated_at',
    )
    
    def current_value_display(self, obj):
        """Güncel değer"""
        return f"₺{obj.current_value:,.2f}"
    current_value_display.short_description = "Güncel Değer"
    
    def profit_loss_display(self, obj):
        """Kar/Zarar"""
        profit = obj.profit_loss
        color = 'green' if profit >= 0 else 'red'
        return format_html(
            '<span style="color: {};">₺{:,.2f}</span>',
            color,
            profit
        )
    profit_loss_display.short_description = "Kar/Zarar"
    
    def profit_loss_percentage_display(self, obj):
        """Kar/Zarar %"""
        percent = obj.profit_loss_percentage
        color = 'green' if percent >= 0 else 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color,
            percent
        )
    profit_loss_percentage_display.short_description = "Kar/Zarar %"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'asset',
        'transaction_type',
        'quantity',
        'price_per_unit',
        'total_amount',
        'profit_loss',
        'status',
        'created_at',
    )
    list_filter = ('transaction_type', 'status', 'created_at', 'asset__asset_type')
    search_fields = ('profile__user__username', 'asset__name', 'asset__symbol')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('İşlem Bilgisi'), {
            'fields': ('profile', 'asset', 'transaction_type', 'status')
        }),
        (_('Miktar ve Fiyat'), {
            'fields': ('quantity', 'price_per_unit', 'total_amount', 'commission')
        }),
        (_('Sonuç'), {
            'fields': ('profit_loss',)
        }),
        (_('Notlar'), {
            'fields': ('notes',)
        }),
        (_('Meta'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketEvent)
class MarketEventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'event_type',
        'impact_level',
        'price_impact_percentage',
        'event_date',
        'is_active',
    )
    list_filter = ('event_type', 'impact_level', 'is_active', 'event_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('affected_assets',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'event_date'
    
    fieldsets = (
        (_('Olay Bilgisi'), {
            'fields': ('title', 'description', 'event_type', 'impact_level')
        }),
        (_('Etki'), {
            'fields': ('affected_assets', 'price_impact_percentage')
        }),
        (_('Zamanlama'), {
            'fields': ('event_date', 'expires_at', 'is_active')
        }),
        (_('Meta'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvestmentLeaderboard)
class InvestmentLeaderboardAdmin(admin.ModelAdmin):
    list_display = (
        'rank',
        'profile',
        'leaderboard_type',
        'total_return_percentage',
        'portfolio_value',
        'period_start',
        'period_end',
    )
    list_filter = ('leaderboard_type', 'period_start', 'period_end')
    search_fields = ('profile__user__username',)
    readonly_fields = ('updated_at',)
    ordering = ('leaderboard_type', 'rank')

