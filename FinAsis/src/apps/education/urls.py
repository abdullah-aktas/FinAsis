# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import FinancialTermCardViewSet
from . import views
from .views import education_home

router = DefaultRouter()
router.register(r'financial-term-cards', FinancialTermCardViewSet, basename='financial-term-card')

app_name = 'education'

urlpatterns = [
    path('', education_home, name='education_home'),
    path('kobi-tutorials/', views.kobi_tutorials, name='kobi_tutorials'),
    # Meetings pages
    path('meetings/', views.MeetingListView.as_view(), name='meetings_list'),
    path('meetings/add/', views.MeetingCreateView.as_view(), name='meetings_add'),
    path('meetings/<int:pk>/', views.MeetingDetailView.as_view(), name='meetings_detail'),
    path('meetings/<int:pk>/ics/', views.meeting_ics, name='meetings_ics'),
    # FinancialTermCard CRUD
    path('financial-term-cards/', views.FinancialTermCardListView.as_view(), name='financialtermcard_list'),
    path('financial-term-cards/add/', views.FinancialTermCardCreateView.as_view(), name='financialtermcard_add'),
    path('financial-term-cards/<int:pk>/', views.FinancialTermCardDetailView.as_view(), name='financialtermcard_detail'),
    path('financial-term-cards/<int:pk>/edit/', views.FinancialTermCardUpdateView.as_view(), name='financialtermcard_edit'),
    path('financial-term-cards/<int:pk>/delete/', views.FinancialTermCardDeleteView.as_view(), name='financialtermcard_delete'),
    # Pruned non-LMS APIs
    path('api/', include(router.urls)),
    # LMS API router
    path('api/lms/', include('src.apps.education.api_urls')),
] 