from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'games', views.GameViewSet)
router.register(r'scores', views.GameScoreViewSet, basename='score')
router.register(r'achievements', views.GameAchievementViewSet)
router.register(r'user-achievements', views.UserGameAchievementViewSet, basename='user-achievement')

app_name = 'ursina_game'

urlpatterns = [
    path('', include(router.urls)),
    path('', views.game_view, name='game'),
    path('start/', views.start_game, name='start_game'),
    path('pause/', views.pause_game, name='pause_game'),
    path('resume/', views.resume_game, name='resume_game'),
    path('end/', views.end_game, name='end_game'),
] 