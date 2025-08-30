# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from .models import Game
# Burada artık model importu yok. Eğer yeni view fonksiyonu ekleyecekseniz buraya yazabilirsiniz.

def game_home(request):
    return render(request, 'games/home.html') 

def game_accounting(request):
    return render(request, 'games/accounting.html')

def game_trading(request):
    return render(request, 'games/trading.html')

def game_investing(request):
    return render(request, 'games/investing.html')

def game_social(request):
    return render(request, 'games/social.html')

def game_collection(request):
    return render(request, 'games/collection.html')

def game_achievements(request):
    return render(request, 'games/achievements.html')

def game_inventory(request):
    return render(request, 'games/inventory.html')

def game_tax(request):
    return render(request, 'games/tax.html')

def game_learning(request):
    return render(request, 'games/learning.html')

def game_market(request):
    return render(request, 'games/market.html')

def games_home(request):
    return render(request, 'games/games_home.html')

def home(request):
    return render(request, 'games/home.html')

def index(request):
    games = Game.objects.all()
    return render(request, 'games/index.html', {'games': games})

def detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request, 'games/detail.html', {'game': game})
