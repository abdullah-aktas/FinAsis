# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'game_app'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('games/', views.games, name='games'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('investor/', views.investor_dashboard, name='investor_dashboard'),
    path('virtual-company/', views.virtual_company_dashboard, name='virtual_company_dashboard'),
    path('kobi/', views.kobi_dashboard, name='kobi_dashboard'),
    path('trade-trail-3d/', views.trade_trail_3d, name='trade_trail_3d'),
    path('stock-market/', views.stock_market_game, name='stock_market'),
    path('budget-challenge/', views.budget_challenge, name='budget_challenge'),
    path('investment-simulator/', views.investment_simulator, name='investment_simulator'),
    path('trade-trail/', views.trade_trail, name='trade_trail'),
    path('kobi-dashboard/', views.kobi_dashboard, name='kobi_dashboard'),
] 