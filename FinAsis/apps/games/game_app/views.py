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
