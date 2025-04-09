from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'games', views.GameViewSet)
router.register(r'scores', views.GameScoreViewSet, basename='score')
router.register(r'achievements', views.GameAchievementViewSet)
router.register(r'user-achievements', views.UserGameAchievementViewSet, basename='user-achievement')

urlpatterns = [
    path('', include(router.urls)),
] 