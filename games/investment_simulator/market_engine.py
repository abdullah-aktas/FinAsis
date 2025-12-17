# -*- coding: utf-8 -*-
"""
Yatırım Simülatörü Piyasa Motoru
Gerçekçi piyasa simülasyonu ve fiyat hareketleri
"""
import random
import math
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import Asset, MarketEvent


class MarketEngine:
    """Gerçekçi piyasa simülasyonu motoru"""
    
    def __init__(self):
        self.market_open = True
        self.volatility_multiplier = 1.0
        self.trend_strength = 0.5
    
    def update_all_assets(self):
        """Tüm araçların fiyatlarını güncelle"""
        assets = Asset.objects.filter(is_active=True)
        updated_count = 0
        
        for asset in assets:
            new_price = self.calculate_new_price(asset)
            if new_price and new_price > 0:
                asset.update_price(new_price)
                updated_count += 1
        
        return updated_count
    
    def calculate_new_price(self, asset):
        """Yeni fiyat hesapla - gerçekçi piyasa hareketleri"""
        current_price = asset.current_price
        
        # Temel volatilite
        volatility = float(asset.volatility) * self.volatility_multiplier
        
        # Trend etkisi
        trend_effect = 0.0
        if asset.trend == 'bullish':
            trend_effect = float(asset.expected_return) / 365 / 100  # Günlük getiri
        elif asset.trend == 'bearish':
            trend_effect = -float(asset.expected_return) / 365 / 100
        
        # Momentum etkisi
        momentum_effect = float(asset.momentum) / 10000  # Momentum'un küçük bir etkisi
        
        # Rastgele piyasa gürültüsü (normal dağılım)
        market_noise = random.gauss(0, volatility)
        
        # Piyasa olayları etkisi
        event_impact = self._get_market_event_impact(asset)
        
        # Fiyat değişimi hesapla
        price_change_percent = (
            trend_effect +
            momentum_effect +
            market_noise +
            event_impact
        )
        
        # Fiyatı güncelle
        new_price = current_price * Decimal(str(1 + price_change_percent))
        
        # Negatif fiyat kontrolü
        if new_price <= 0:
            new_price = current_price * Decimal('0.95')  # En fazla %5 düşüş
        
        # Çok büyük artış kontrolü (günlük %20'den fazla artış olmaz)
        max_increase = current_price * Decimal('1.20')
        if new_price > max_increase:
            new_price = max_increase
        
        # Çok büyük düşüş kontrolü (günlük %20'den fazla düşüş olmaz)
        max_decrease = current_price * Decimal('0.80')
        if new_price < max_decrease:
            new_price = max_decrease
        
        return new_price
    
    def _get_market_event_impact(self, asset):
        """Aktif piyasa olaylarının etkisini hesapla"""
        now = timezone.now()
        active_events = MarketEvent.objects.filter(
            is_active=True,
            event_date__lte=now,
            expires_at__gte=now
        ).filter(
            affected_assets=asset
        )
        
        total_impact = 0.0
        for event in active_events:
            # Etki seviyesine göre çarpan
            impact_multiplier = {
                'low': 0.3,
                'medium': 0.6,
                'high': 1.0,
                'critical': 1.5
            }.get(event.impact_level, 0.5)
            
            total_impact += float(event.price_impact_percentage) * impact_multiplier / 100
        
        return total_impact
    
    def create_market_event(self, event_type, impact_level, affected_assets, price_impact):
        """Rastgele piyasa olayı oluştur"""
        event_titles = {
            'news': [
                'Şirket kazanç açıklaması',
                'Yeni ürün lansmanı',
                'Piyasa analisti yorumu',
                'Sektör raporu yayınlandı',
            ],
            'crisis': [
                'Piyasa düşüşü',
                'Ekonomik belirsizlik',
                'Sektör krizi',
                'Küresel endişeler',
            ],
            'boom': [
                'Piyasa yükselişi',
                'Yeni yatırım dalgası',
                'Sektör büyümesi',
                'Olumlu ekonomik veriler',
            ],
            'regulation': [
                'Yeni düzenleme',
                'Yasal değişiklik',
                'Denetim kararı',
                'Politika güncellemesi',
            ],
        }
        
        title = random.choice(event_titles.get(event_type, ['Piyasa Güncellemesi']))
        description = f"{title} piyasayı etkiliyor."
        
        event = MarketEvent.objects.create(
            title=title,
            description=description,
            event_type=event_type,
            impact_level=impact_level,
            price_impact_percentage=price_impact,
            event_date=timezone.now(),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        event.affected_assets.set(affected_assets)
        return event
    
    def simulate_random_event(self):
        """Rastgele piyasa olayı simüle et"""
        if random.random() > 0.1:  # %10 şans
            return None
        
        event_types = ['news', 'crisis', 'boom', 'regulation']
        event_type = random.choice(event_types)
        
        impact_levels = ['low', 'medium', 'high']
        impact_level = random.choice(impact_levels)
        
        # Etkilenen araçlar (rastgele 1-3 araç)
        assets = list(Asset.objects.filter(is_active=True))
        if not assets:
            return None
        
        affected_count = random.randint(1, min(3, len(assets)))
        affected_assets = random.sample(assets, affected_count)
        
        # Fiyat etkisi
        price_impact = Decimal(str(random.uniform(-15, 15)))
        if event_type == 'crisis':
            price_impact = Decimal(str(random.uniform(-20, -5)))
        elif event_type == 'boom':
            price_impact = Decimal(str(random.uniform(5, 20)))
        
        return self.create_market_event(
            event_type,
            impact_level,
            affected_assets,
            price_impact
        )


class PortfolioAnalyzer:
    """Portföy analiz ve öneri motoru"""
    
    @staticmethod
    def analyze_portfolio(profile):
        """Portföy analizi yap"""
        from .models import Portfolio
        from decimal import Decimal
        
        holdings = Portfolio.objects.filter(profile=profile).select_related('asset')
        
        if not holdings.exists():
            return {
                'total_value': float(profile.cash_balance or 0),
                'diversification_score': 0,
                'risk_score': 0,
                'total_return': 0,
                'recommendations': ['Portföyünüz boş. Yatırım yapmaya başlayın!']
            }
        
        # Çeşitlendirme skoru
        asset_types = set(h.asset.asset_type for h in holdings if h.asset)
        diversification_score = min(100, len(asset_types) * 20) if asset_types else 0
        
        # Toplam değer ve risk skoru
        total_value = Decimal('0')
        for holding in holdings:
            if holding.asset:
                current_price = Decimal(str(holding.asset.current_price or 0))
                total_value += Decimal(str(holding.quantity or 0)) * current_price
        
        risk_score = Decimal('0')
        for holding in holdings:
            if holding.asset and total_value > 0:
                current_price = Decimal(str(holding.asset.current_price or 0))
                holding_value = Decimal(str(holding.quantity or 0)) * current_price
                weight = holding_value / total_value
                risk_value = {
                    'low': 1,
                    'medium': 2,
                    'high': 3,
                    'very_high': 4
                }.get(holding.asset.risk_level, 2)
                risk_score += weight * Decimal(str(risk_value))
        
        # Öneriler
        recommendations = []
        
        if diversification_score < 40:
            recommendations.append('Portföyünüzü daha fazla çeşitlendirin. Farklı yatırım araçlarına yatırım yapın.')
        
        if risk_score > 2.5:
            recommendations.append('Portföyünüz yüksek riskli. Daha güvenli araçlara yatırım yapmayı düşünün.')
        elif risk_score < 1.5:
            recommendations.append('Portföyünüz çok güvenli. Daha yüksek getiri için orta riskli araçlar ekleyebilirsiniz.')
        
        # Trend önerileri
        bullish_assets = [h for h in holdings if h.asset.trend == 'bullish']
        if bullish_assets:
            recommendations.append(f'{len(bullish_assets)} yatırımınız yükseliş trendinde. Bu fırsatı değerlendirin!')
        
        bearish_assets = [h for h in holdings if h.asset.trend == 'bearish']
        if bearish_assets:
            recommendations.append(f'{len(bearish_assets)} yatırımınız düşüş trendinde. Risk yönetimi yapın!')
        
        return {
            'diversification_score': diversification_score,
            'risk_score': risk_score,
            'total_holdings': holdings.count(),
            'recommendations': recommendations
        }
    
    @staticmethod
    def get_suggested_assets(profile, limit=5):
        """Önerilen yatırım araçları"""
        from .models import Portfolio
        
        # Mevcut portföydeki araçlar
        owned_asset_ids = Portfolio.objects.filter(profile=profile).values_list('asset_id', flat=True)
        
        # Trend ve momentum'a göre öner
        suggested = Asset.objects.filter(
            is_active=True
        ).exclude(
            id__in=owned_asset_ids
        ).order_by(
            '-momentum',
            '-expected_return'
        )[:limit]
        
        return suggested

