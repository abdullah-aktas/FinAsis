# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'crm'

# Ana router
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'opportunities', views.OpportunityViewSet, basename='opportunity')
router.register(r'activities', views.ActivityViewSet, basename='activity')
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'communications', views.CommunicationViewSet, basename='communication')
router.register(r'notes', views.NoteViewSet, basename='note')

# Müşteri altındaki nested router'lar
customer_router = routers.NestedDefaultRouter(router, r'customers', lookup='customer')
customer_router.register(r'contacts', views.ContactViewSet, basename='customer-contact')
customer_router.register(r'opportunities', views.OpportunityViewSet, basename='customer-opportunity')
customer_router.register(r'activities', views.ActivityViewSet, basename='customer-activity')
customer_router.register(r'documents', views.DocumentViewSet, basename='customer-document')
customer_router.register(r'communications', views.CommunicationViewSet, basename='customer-communication')
customer_router.register(r'notes', views.NoteViewSet, basename='customer-note')

# Fırsat altındaki nested router'lar
opportunity_router = routers.NestedDefaultRouter(router, r'opportunities', lookup='opportunity')
opportunity_router.register(r'activities', views.ActivityViewSet, basename='opportunity-activity')
opportunity_router.register(r'documents', views.DocumentViewSet, basename='opportunity-document')

# Aktivite altındaki nested router'lar
activity_router = routers.NestedDefaultRouter(router, r'activities', lookup='activity')
activity_router.register(r'documents', views.DocumentViewSet, basename='activity-document')

# Sadakat programı URL'leri
loyalty_urlpatterns = [
    path('programs/', views.LoyaltyProgramListView.as_view(), name='loyaltyprogram_list'),
    path('programs/<int:pk>/', views.LoyaltyProgramDetailView.as_view(), name='loyaltyprogram_detail'),
    path('programs/create/', views.LoyaltyProgramCreateView.as_view(), name='loyaltyprogram_create'),
    path('programs/<int:pk>/update/', views.LoyaltyProgramUpdateView.as_view(), name='loyaltyprogram_update'),
    path('programs/<int:pk>/delete/', views.LoyaltyProgramDeleteView.as_view(), name='loyaltyprogram_delete'),
]

# Sadakat seviyesi URL'leri
loyalty_level_urlpatterns = [
    path('levels/', views.LoyaltyLevelListView.as_view(), name='loyaltylevel_list'),
    path('levels/<int:pk>/', views.LoyaltyLevelDetailView.as_view(), name='loyaltylevel_detail'),
    path('levels/create/', views.LoyaltyLevelCreateView.as_view(), name='loyaltylevel_create'),
    path('levels/<int:pk>/update/', views.LoyaltyLevelUpdateView.as_view(), name='loyaltylevel_update'),
    path('levels/<int:pk>/delete/', views.LoyaltyLevelDeleteView.as_view(), name='loyaltylevel_delete'),
]

# Müşteri sadakati URL'leri
customer_loyalty_urlpatterns = [
    path('customer-loyalties/', views.CustomerLoyaltyListView.as_view(), name='customerloyalty_list'),
    path('customer-loyalties/<int:pk>/', views.CustomerLoyaltyDetailView.as_view(), name='customerloyalty_detail'),
    path('customer-loyalties/create/', views.CustomerLoyaltyCreateView.as_view(), name='customerloyalty_create'),
    path('customer-loyalties/<int:pk>/update/', views.CustomerLoyaltyUpdateView.as_view(), name='customerloyalty_update'),
    path('customer-loyalties/<int:pk>/delete/', views.CustomerLoyaltyDeleteView.as_view(), name='customerloyalty_delete'),
]

# Sezonluk kampanya URL'leri
seasonal_campaign_urlpatterns = [
    path('campaigns/', views.SeasonalCampaignListView.as_view(), name='seasonalcampaign_list'),
    path('campaigns/<int:pk>/', views.SeasonalCampaignDetailView.as_view(), name='seasonalcampaign_detail'),
    path('campaigns/create/', views.SeasonalCampaignCreateView.as_view(), name='seasonalcampaign_create'),
    path('campaigns/<int:pk>/update/', views.SeasonalCampaignUpdateView.as_view(), name='seasonalcampaign_update'),
    path('campaigns/<int:pk>/delete/', views.SeasonalCampaignDeleteView.as_view(), name='seasonalcampaign_delete'),
]

# Ortaklık programı URL'leri
partnership_urlpatterns = [
    path('partnerships/', views.PartnershipProgramListView.as_view(), name='partnershipprogram_list'),
    path('partnerships/<int:pk>/', views.PartnershipProgramDetailView.as_view(), name='partnershipprogram_detail'),
    path('partnerships/create/', views.PartnershipProgramCreateView.as_view(), name='partnershipprogram_create'),
    path('partnerships/<int:pk>/update/', views.PartnershipProgramUpdateView.as_view(), name='partnershipprogram_update'),
    path('partnerships/<int:pk>/delete/', views.PartnershipProgramDeleteView.as_view(), name='partnershipprogram_delete'),
]

# Ortak URL'leri
partner_urlpatterns = [
    path('partners/', views.PartnerListView.as_view(), name='partner_list'),
    path('partners/<int:pk>/', views.PartnerDetailView.as_view(), name='partner_detail'),
    path('partners/create/', views.PartnerCreateView.as_view(), name='partner_create'),
    path('partners/<int:pk>/update/', views.PartnerUpdateView.as_view(), name='partner_update'),
    path('partners/<int:pk>/delete/', views.PartnerDeleteView.as_view(), name='partner_delete'),
]

# Etkileşim log URL'leri
interaction_log_urlpatterns = [
    path('interactions/', views.InteractionLogListView.as_view(), name='interactionlog_list'),
    path('interactions/<int:pk>/', views.InteractionLogDetailView.as_view(), name='interactionlog_detail'),
    path('interactions/create/', views.InteractionLogCreateView.as_view(), name='interactionlog_create'),
    path('interactions/<int:pk>/update/', views.InteractionLogUpdateView.as_view(), name='interactionlog_update'),
    path('interactions/<int:pk>/delete/', views.InteractionLogDeleteView.as_view(), name='interactionlog_delete'),
]

# API URL'leri
api_urlpatterns = [
    path('', include(router.urls)),
    path('', include(customer_router.urls)),
    path('', include(opportunity_router.urls)),
    path('', include(activity_router.urls)),
]

# Tüm URL'leri birleştir
urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('loyalty/', include(loyalty_urlpatterns)),
    path('loyalty/', include(loyalty_level_urlpatterns)),
    path('loyalty/', include(customer_loyalty_urlpatterns)),
    path('campaigns/', include(seasonal_campaign_urlpatterns)),
    path('partnerships/', include(partnership_urlpatterns)),
    path('partners/', include(partner_urlpatterns)),
    path('interactions/', include(interaction_log_urlpatterns)),
] 