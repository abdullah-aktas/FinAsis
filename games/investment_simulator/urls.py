# -*- coding: utf-8 -*-
"""
Yatırım Simülatörü URLs
"""
from django.urls import path
from . import views

app_name = 'investment_simulator'

urlpatterns = [
    path('', views.investment_simulator, name='investment_simulator'),
    path('api/assets/', views.api_assets, name='api_assets'),
    path('api/portfolio/', views.api_portfolio, name='api_portfolio'),
    path('api/buy/', views.api_buy, name='api_buy'),
    path('api/sell/', views.api_sell, name='api_sell'),
    path('api/leaderboard/', views.api_leaderboard, name='api_leaderboard'),
    path('api/market-events/', views.api_market_events, name='api_market_events'),
    path('api/analysis/', views.api_analysis, name='api_analysis'),
]

