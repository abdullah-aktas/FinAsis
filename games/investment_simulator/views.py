# -*- coding: utf-8 -*-
"""
Yatırım Simülatörü Views
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from decimal import Decimal
import json

from .models import (
    InvestmentProfile,
    Asset,
    Portfolio,
    Transaction,
    MarketEvent,
    InvestmentLeaderboard,
)
from .market_engine import MarketEngine, PortfolioAnalyzer
from games.models import PlayerProfile


@login_required
def investment_simulator(request):
    """Yatırım simülatörü ana sayfası"""
    profile, _ = InvestmentProfile.objects.get_or_create(user=request.user)
    player_profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    # Portföy analizi
    analyzer = PortfolioAnalyzer()
    analysis = analyzer.analyze_portfolio(profile)
    suggested_assets = analyzer.get_suggested_assets(profile, limit=5)
    
    # Liderlik tablosu
    weekly_leaderboard = InvestmentLeaderboard.objects.filter(
        leaderboard_type='weekly',
        period_start__lte=timezone.now().date(),
        period_end__gte=timezone.now().date()
    ).order_by('rank')[:10]
    
    # Aktif piyasa olayları
    active_events = MarketEvent.objects.filter(
        is_active=True,
        event_date__lte=timezone.now(),
        expires_at__gte=timezone.now()
    )[:5]
    
    context = {
        'profile': profile,
        'player_profile': player_profile,
        'analysis': analysis,
        'suggested_assets': suggested_assets,
        'weekly_leaderboard': weekly_leaderboard,
        'active_events': active_events,
    }
    
    return render(request, 'investment_simulator/investment_simulator.html', context)


@login_required
@require_http_methods(["GET"])
def api_assets(request):
    """Tüm yatırım araçlarını getir"""
    assets = Asset.objects.filter(is_active=True)
    
    data = [{
        'id': asset.id,
        'name': asset.name,
        'symbol': asset.symbol,
        'type': asset.asset_type,
        'risk_level': asset.risk_level,
        'current_price': float(asset.current_price),
        'base_price': float(asset.base_price),
        'volatility': float(asset.volatility),
        'expected_return': float(asset.expected_return),
        'trend': asset.trend,
        'momentum': float(asset.momentum),
        'icon': asset.icon,
        'price_change_24h': asset.price_history[-1]['change_percent'] if asset.price_history else 0,
    } for asset in assets]
    
    return JsonResponse({'assets': data})


@login_required
@require_http_methods(["GET"])
def api_portfolio(request):
    """Kullanıcının portföyünü getir"""
    profile = get_object_or_404(InvestmentProfile, user=request.user)
    holdings = Portfolio.objects.filter(profile=profile)
    
    portfolio_data = [{
        'asset_id': holding.asset.id,
        'asset_name': holding.asset.name,
        'asset_symbol': holding.asset.symbol,
        'quantity': float(holding.quantity),
        'average_cost': float(holding.average_cost),
        'current_price': float(holding.asset.current_price),
        'current_value': float(holding.current_value),
        'total_cost': float(holding.total_cost),
        'profit_loss': float(holding.profit_loss),
        'profit_loss_percent': float(holding.profit_loss_percentage),
    } for holding in holdings]
    
    return JsonResponse({
        'portfolio': portfolio_data,
        'cash_balance': float(profile.cash_balance),
        'portfolio_value': float(profile.portfolio_value),
        'total_profit_loss': float(profile.total_profit_loss_calculated),
        'total_return_percentage': float(profile.total_return_percentage),
    })


@login_required
@require_http_methods(["POST"])
def api_buy(request):
    """Yatırım aracı satın al"""
    profile = get_object_or_404(InvestmentProfile, user=request.user)
    
    try:
        data = json.loads(request.body)
        asset_id = data.get('asset_id')
        quantity = Decimal(str(data.get('quantity', 0)))
        
        if quantity <= 0:
            return JsonResponse({'error': 'Geçersiz miktar'}, status=400)
        
        asset = get_object_or_404(Asset, id=asset_id, is_active=True)
        
        # Toplam maliyet
        total_cost = asset.current_price * quantity
        commission = total_cost * Decimal('0.001')  # %0.1 komisyon
        total_with_commission = total_cost + commission
        
        # Nakit kontrolü
        if total_with_commission > profile.cash_balance:
            return JsonResponse({
                'error': 'Yetersiz nakit',
                'required': float(total_with_commission),
                'available': float(profile.cash_balance)
            }, status=400)
        
        # Portföyde var mı kontrol et
        holding, created = Portfolio.objects.get_or_create(
            profile=profile,
            asset=asset,
            defaults={
                'quantity': quantity,
                'average_cost': asset.current_price,
                'total_cost': total_cost,
            }
        )
        
        if not created:
            # Mevcut holding'i güncelle (weighted average)
            total_quantity = holding.quantity + quantity
            total_cost_new = holding.total_cost + total_cost
            holding.quantity = total_quantity
            holding.average_cost = total_cost_new / total_quantity
            holding.total_cost = total_cost_new
            holding.save()
        
        # Nakit azalt
        profile.cash_balance -= total_with_commission
        profile.total_invested += total_cost
        profile.total_transactions += 1
        profile.save(update_fields=['cash_balance', 'total_invested', 'total_transactions'])
        
        # İşlem kaydı
        Transaction.objects.create(
            profile=profile,
            asset=asset,
            transaction_type='buy',
            quantity=quantity,
            price_per_unit=asset.current_price,
            total_amount=total_cost,
            commission=commission,
            status='completed'
        )
        
        # XP ve beceri güncelle
        profile.add_xp(10)
        profile.skill_analysis = min(100, profile.skill_analysis + 1)
        profile.save(update_fields=['skill_analysis'])
        
        # PlayerProfile'a da XP ekle
        try:
            player_profile = PlayerProfile.objects.get(user=request.user)
            player_profile.add_xp(10)
            player_profile.record_event('investment', True)
        except PlayerProfile.DoesNotExist:
            pass
        
        return JsonResponse({
            'success': True,
            'message': f'{quantity} adet {asset.name} satın alındı',
            'cash_balance': float(profile.cash_balance),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def api_sell(request):
    """Yatırım aracı sat"""
    profile = get_object_or_404(InvestmentProfile, user=request.user)
    
    try:
        data = json.loads(request.body)
        asset_id = data.get('asset_id')
        quantity = Decimal(str(data.get('quantity', 0)))
        
        if quantity <= 0:
            return JsonResponse({'error': 'Geçersiz miktar'}, status=400)
        
        asset = get_object_or_404(Asset, id=asset_id)
        holding = get_object_or_404(Portfolio, profile=profile, asset=asset)
        
        if holding.quantity < quantity:
            return JsonResponse({
                'error': 'Yetersiz miktar',
                'available': float(holding.quantity),
                'requested': float(quantity)
            }, status=400)
        
        # Satış geliri
        total_revenue = asset.current_price * quantity
        commission = total_revenue * Decimal('0.001')  # %0.1 komisyon
        net_revenue = total_revenue - commission
        
        # Kar/zarar hesapla
        cost_of_sold = (holding.total_cost / holding.quantity) * quantity
        profit_loss = net_revenue - cost_of_sold
        
        # Nakit ekle
        profile.cash_balance += net_revenue
        profile.total_transactions += 1
        
        if profit_loss > 0:
            profile.successful_trades += 1
        else:
            profile.failed_trades += 1
        
        profile.save(update_fields=['cash_balance', 'total_transactions', 'successful_trades', 'failed_trades'])
        profile.update_stats()
        
        # Portföyden çıkar
        holding.quantity -= quantity
        holding.total_cost -= cost_of_sold
        
        if holding.quantity <= 0:
            holding.delete()
        else:
            holding.average_cost = holding.total_cost / holding.quantity
            holding.save()
        
        # İşlem kaydı
        Transaction.objects.create(
            profile=profile,
            asset=asset,
            transaction_type='sell',
            quantity=quantity,
            price_per_unit=asset.current_price,
            total_amount=total_revenue,
            commission=commission,
            profit_loss=profit_loss,
            status='completed'
        )
        
        # XP ve beceri güncelle
        xp_gain = 20 if profit_loss > 0 else 5
        profile.add_xp(xp_gain)
        profile.skill_timing = min(100, profile.skill_timing + 1)
        profile.save(update_fields=['skill_timing'])
        
        # PlayerProfile'a da XP ekle
        try:
            player_profile = PlayerProfile.objects.get(user=request.user)
            player_profile.add_xp(xp_gain)
            player_profile.record_event('investment', profit_loss > 0)
        except PlayerProfile.DoesNotExist:
            pass
        
        return JsonResponse({
            'success': True,
            'message': f'{quantity} adet {asset.name} satıldı',
            'profit_loss': float(profit_loss),
            'cash_balance': float(profile.cash_balance),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_leaderboard(request):
    """Liderlik tablosu"""
    leaderboard_type = request.GET.get('type', 'weekly')
    
    if leaderboard_type == 'weekly':
        period_start = timezone.now().date() - timezone.timedelta(days=7)
        period_end = timezone.now().date()
    elif leaderboard_type == 'monthly':
        period_start = timezone.now().date().replace(day=1)
        period_end = timezone.now().date()
    else:
        period_start = None
        period_end = None
    
    entries = InvestmentLeaderboard.objects.filter(
        leaderboard_type=leaderboard_type
    )
    
    if period_start and period_end:
        entries = entries.filter(
            period_start=period_start,
            period_end=period_end
        )
    
    entries = entries.order_by('rank')[:100]
    
    data = [{
        'rank': entry.rank,
        'username': entry.profile.user.username,
        'total_return_percentage': float(entry.total_return_percentage),
        'portfolio_value': float(entry.portfolio_value),
    } for entry in entries]
    
    # Kullanıcının sırası
    user_rank = None
    try:
        user_entry = entries.get(profile__user=request.user)
        user_rank = {
            'rank': user_entry.rank,
            'total_return_percentage': float(user_entry.total_return_percentage),
            'portfolio_value': float(user_entry.portfolio_value),
        }
    except InvestmentLeaderboard.DoesNotExist:
        pass
    
    return JsonResponse({
        'leaderboard': data,
        'user_rank': user_rank,
        'type': leaderboard_type,
    })


@login_required
@require_http_methods(["GET"])
def api_market_events(request):
    """Aktif piyasa olayları"""
    events = MarketEvent.objects.filter(
        is_active=True,
        event_date__lte=timezone.now(),
        expires_at__gte=timezone.now()
    ).order_by('-event_date')[:10]
    
    data = [{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'event_type': event.event_type,
        'impact_level': event.impact_level,
        'price_impact_percentage': float(event.price_impact_percentage),
        'affected_assets': [a.symbol for a in event.affected_assets.all()],
        'event_date': event.event_date.isoformat(),
    } for event in events]
    
    return JsonResponse({'events': data})


@login_required
@require_http_methods(["GET"])
def api_analysis(request):
    """Portföy analizi"""
    profile = get_object_or_404(InvestmentProfile, user=request.user)
    analyzer = PortfolioAnalyzer()
    analysis = analyzer.analyze_portfolio(profile)
    
    return JsonResponse(analysis)

