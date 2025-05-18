# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('<int:pk>/', views.game_detail, name='game_detail'),
    path('<int:pk>/join/', views.join_game, name='join_game'),
    path('player/<int:pk>/transaction/', views.make_transaction, name='make_transaction'),
    path('challenge/<int:pk>/complete/', views.complete_challenge, name='complete_challenge'),
    path('game/<int:game_id>/start/', views.start_game, name='start_game'),
    path('player/<int:player_id>/state/', views.get_game_state, name='get_game_state'),
    path('player/<int:player_id>/save/', views.save_game_state, name='save_game_state'),
    path('player/<int:player_id>/transaction/', views.record_transaction, name='record_transaction'),
] 