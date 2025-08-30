# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import FinancialTermCardViewSet
from . import views
from .views import education_home, StudentAnalyticsViewSet, adaptive_recommendation_api, BadgeViewSet, LevelViewSet, StudentGamificationProgressViewSet, LearningContentViewSet, ForumViewSet, ForumTopicViewSet, ForumPostViewSet, GroupAssignmentViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'financial-term-cards', FinancialTermCardViewSet, basename='financial-term-card')
router.register(r'student-analytics', StudentAnalyticsViewSet, basename='student-analytics')
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'levels', LevelViewSet, basename='level')
router.register(r'gamification-progress', StudentGamificationProgressViewSet, basename='gamification-progress')
router.register(r'learning-content', LearningContentViewSet, basename='learning-content')
router.register(r'forum', ForumViewSet, basename='forum')
router.register(r'forum-topic', ForumTopicViewSet, basename='forum-topic')
router.register(r'forum-post', ForumPostViewSet, basename='forum-post')
router.register(r'group-assignment', GroupAssignmentViewSet, basename='group-assignment')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

app_name = 'education'

urlpatterns = [
    path('', education_home, name='education_home'),
    path('kobi-tutorials/', views.kobi_tutorials, name='kobi_tutorials'),
    # FinancialTermCard CRUD
    path('financial-term-cards/', views.FinancialTermCardListView.as_view(), name='financialtermcard_list'),
    path('financial-term-cards/add/', views.FinancialTermCardCreateView.as_view(), name='financialtermcard_add'),
    path('financial-term-cards/<int:pk>/', views.FinancialTermCardDetailView.as_view(), name='financialtermcard_detail'),
    path('financial-term-cards/<int:pk>/edit/', views.FinancialTermCardUpdateView.as_view(), name='financialtermcard_edit'),
    path('financial-term-cards/<int:pk>/delete/', views.FinancialTermCardDeleteView.as_view(), name='financialtermcard_delete'),
    path('api/adaptive-recommendation/', adaptive_recommendation_api, name='adaptive_recommendation_api'),
    path('api/', include(router.urls)),
] 