# -*- coding: utf-8 -*-
from django.shortcuts import render
from .game import Game
from .ar_trade_trail import ARTradeTrail

# Create your views here.

# Oyun listesi view

def games(request):
    oyunlar = [
        {
            'title': 'Borsa Simülasyonu',
            'description': 'Sanal borsada alım-satım yaparak yatırım deneyimi kazanın.',
            'category': 'borsa',
            'image': '/static/img/games/stock.jpg',
            'url': '/games/game_app/stock-market/'
        },
        {
            'title': 'Bütçe Mücadelesi',
            'description': 'Gerçek hayat senaryolarıyla bütçe yönetimini öğrenin.',
            'category': 'finans',
            'image': '/static/img/games/budget.jpg',
            'url': '/games/game_app/budget-challenge/'
        },
        {
            'title': 'Yatırım Simülatörü',
            'description': 'Yatırım stratejilerinizi test edin ve deneyim kazanın.',
            'category': 'yatırım',
            'image': '/static/img/games/investment.jpg',
            'url': '/games/game_app/investment-simulator/'
        },
        {
            'title': 'Ticaretin İzinde 3D',
            'description': '3D dünyada ticaret ve finansı deneyimleyin.',
            'category': 'ticaret',
            'image': '/static/img/games/trade3d.jpg',
            'url': '/games/game_app/trade-trail-3d/'
        },
    ]
    return render(request, 'game_app/games.html', {'games': oyunlar})

# Her oyun için ayrı view

def stock_market_game(request):
    return render(request, 'game_app/stock_market.html')

def budget_challenge(request):
    return render(request, 'game_app/budget_challenge.html')

def investment_simulator(request):
    return render(request, 'game_app/investment_simulator.html')

def trade_trail_3d(request):
    return render(request, 'game_app/trade_trail_3d.html')

def tradesim(request):
    return render(request, 'game_app/tradesim.html')

def quiz(request):
    return render(request, 'game_app/quiz.html')

def game_detail(request, game_key):
    """Her oyun için detay sayfası"""
    # Oyun bilgileri (örnek, ileride veritabanı veya dict ile dinamik yapılabilir)
    games_info = {
        'tradesim': {
            'title': 'TradeSim & Ticaretin İzinde',
            'description': 'Şehirler arası ticaret, şirket yönetimi, finansal eğitim ve görevlerle birleşik simülasyon.',
            'image': '/static/img/games/tradesim.jpg',
            'how_to_play': 'Şirketini kur, şehirler arası ticaret yap, görevleri tamamla ve finansal okuryazarlığını geliştir.',
            'features': ['Şehirler arası ticaret', 'Şirket ve karakter yönetimi', 'Finansal eğitim', 'Görev ve başarımlar', 'Skor tablosu'],
            'play_url': '/games/game_app/tradesim/'
        },
        'stock-market': {
            'title': 'Borsa Simülasyonu',
            'description': 'Sanal borsada al-sat yaparak yatırım deneyimi kazan.',
            'image': '/static/img/games/stock.jpg',
            'how_to_play': 'Hisse senetlerini analiz et, al-sat yap, portföyünü büyüt.',
            'features': ['Gerçek zamanlı fiyatlar', 'Portföy yönetimi', 'Yatırım stratejileri'],
            'play_url': '/games/game_app/stock-market/'
        },
        'budget-challenge': {
            'title': 'Bütçe Mücadelesi',
            'description': 'Gerçek hayat senaryolarıyla bütçe yönetimini öğren.',
            'image': '/static/img/games/budget.jpg',
            'how_to_play': 'Gelir ve giderlerini yönet, tasarruf et, finansal hedeflere ulaş.',
            'features': ['Senaryo tabanlı', 'Gider analizi', 'Tasarruf ipuçları'],
            'play_url': '/games/game_app/budget-challenge/'
        },
        'investment-simulator': {
            'title': 'Yatırım Simülatörü',
            'description': 'Yatırım stratejilerini test et ve deneyim kazan.',
            'image': '/static/img/games/investment.jpg',
            'how_to_play': 'Farklı yatırım araçlarını dene, riskleri analiz et, portföyünü büyüt.',
            'features': ['Çeşitli yatırım araçları', 'Risk analizi', 'Getiri simülasyonu'],
            'play_url': '/games/game_app/investment-simulator/'
        },
        'trade-trail-3d': {
            'title': 'Ticaretin İzinde 3D',
            'description': '3D dünyada ticaret ve finansı deneyimle.',
            'image': '/static/img/games/trade3d.jpg',
            'how_to_play': 'Karakterini seç, şirketini kur, 3D dünyada ticaret yap.',
            'features': ['3D ortam', 'Karakter ve şirket seçimi', 'Görevler ve eğitim'],
            'play_url': '/games/game_app/trade-trail-3d/'
        },
    }
    game = games_info.get(game_key)
    if not game:
        return render(request, 'game_app/game_not_found.html', {'game_key': game_key})
    return render(request, 'game_app/game_detail.html', {'game': game})
