# -*- coding: utf-8 -*-
from django.urls import path, include
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.index, name='games_index'),
    path('<int:game_id>/', views.detail, name='game_detail'),
    path('accounting/', views.game_accounting, name='game_accounting'),
    path('trading/', views.game_trading, name='game_trading'),
    path('investing/', views.game_investing, name='game_investing'),
    path('social/', views.game_social, name='game_social'),
    path('collection/', views.game_collection, name='game_collection'),
    path('achievements/', views.game_achievements, name='game_achievements'),
    path('inventory/', views.game_inventory, name='game_inventory'),
    path('tax/', views.game_tax, name='game_tax'),
    path('learning/', views.game_learning, name='game_learning'),
    path('market/', views.game_market, name='game_market'),
    path('trade-sim/', include('FinAsis.apps.games.trade_sim.urls')),
    # Game App alt uygulaması
    path('game_app/', include('FinAsis.apps.games.game_app.urls')),
] 
