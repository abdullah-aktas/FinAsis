from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('<int:pk>/', views.game_detail, name='game_detail'),
    path('<int:pk>/join/', views.join_game, name='join_game'),
    path('player/<int:pk>/transaction/', views.make_transaction, name='make_transaction'),
    path('challenge/<int:pk>/complete/', views.complete_challenge, name='complete_challenge'),
] 