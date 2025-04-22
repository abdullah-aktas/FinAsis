from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'crm'

router = DefaultRouter()
router.register(r'leads', views.LeadViewSet, basename='lead')
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'opportunities', views.OpportunityViewSet, basename='opportunity')
router.register(r'activities', views.ActivityViewSet, basename='activity')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web views - Müşteriler
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Web views - Adaylar (Leads)
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/edit/', views.lead_edit, name='lead_edit'),
    path('leads/<int:pk>/delete/', views.lead_delete, name='lead_delete'),
    path('leads/<int:pk>/convert/', views.lead_convert, name='lead_convert'),
    
    # Web views - Fırsatlar
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/create/', views.opportunity_create, name='opportunity_create'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:pk>/edit/', views.opportunity_edit, name='opportunity_edit'),
    path('opportunities/<int:pk>/delete/', views.opportunity_delete, name='opportunity_delete'),
    
    # Web views - Aktiviteler
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('activities/<int:pk>/complete/', views.activity_complete, name='activity_complete'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # LoyaltyProgram URLs
    path('loyaltyprogram/', views.LoyaltyProgramListView.as_view(), name='loyaltyprogram_list'),
    path('loyaltyprogram/<int:pk>/', views.LoyaltyProgramDetailView.as_view(), name='loyaltyprogram_detail'),
    path('loyaltyprogram/create/', views.LoyaltyProgramCreateView.as_view(), name='loyaltyprogram_create'),
    path('loyaltyprogram/<int:pk>/update/', views.LoyaltyProgramUpdateView.as_view(), name='loyaltyprogram_update'),
    path('loyaltyprogram/<int:pk>/delete/', views.LoyaltyProgramDeleteView.as_view(), name='loyaltyprogram_delete'),

    # LoyaltyLevel URLs
    path('loyaltylevel/', views.LoyaltyLevelListView.as_view(), name='loyaltylevel_list'),
    path('loyaltylevel/<int:pk>/', views.LoyaltyLevelDetailView.as_view(), name='loyaltylevel_detail'),
    path('loyaltylevel/create/', views.LoyaltyLevelCreateView.as_view(), name='loyaltylevel_create'),
    path('loyaltylevel/<int:pk>/update/', views.LoyaltyLevelUpdateView.as_view(), name='loyaltylevel_update'),
    path('loyaltylevel/<int:pk>/delete/', views.LoyaltyLevelDeleteView.as_view(), name='loyaltylevel_delete'),

    # CustomerLoyalty URLs
    path('customerloyalty/', views.CustomerLoyaltyListView.as_view(), name='customerloyalty_list'),
    path('customerloyalty/<int:pk>/', views.CustomerLoyaltyDetailView.as_view(), name='customerloyalty_detail'),
    path('customerloyalty/create/', views.CustomerLoyaltyCreateView.as_view(), name='customerloyalty_create'),
    path('customerloyalty/<int:pk>/update/', views.CustomerLoyaltyUpdateView.as_view(), name='customerloyalty_update'),
    path('customerloyalty/<int:pk>/delete/', views.CustomerLoyaltyDeleteView.as_view(), name='customerloyalty_delete'),

    # SeasonalCampaign URLs
    path('seasonalcampaign/', views.SeasonalCampaignListView.as_view(), name='seasonalcampaign_list'),
    path('seasonalcampaign/<int:pk>/', views.SeasonalCampaignDetailView.as_view(), name='seasonalcampaign_detail'),
    path('seasonalcampaign/create/', views.SeasonalCampaignCreateView.as_view(), name='seasonalcampaign_create'),
    path('seasonalcampaign/<int:pk>/update/', views.SeasonalCampaignUpdateView.as_view(), name='seasonalcampaign_update'),
    path('seasonalcampaign/<int:pk>/delete/', views.SeasonalCampaignDeleteView.as_view(), name='seasonalcampaign_delete'),

    # PartnershipProgram URLs
    path('partnershipprogram/', views.PartnershipProgramListView.as_view(), name='partnershipprogram_list'),
    path('partnershipprogram/<int:pk>/', views.PartnershipProgramDetailView.as_view(), name='partnershipprogram_detail'),
    path('partnershipprogram/create/', views.PartnershipProgramCreateView.as_view(), name='partnershipprogram_create'),
    path('partnershipprogram/<int:pk>/update/', views.PartnershipProgramUpdateView.as_view(), name='partnershipprogram_update'),
    path('partnershipprogram/<int:pk>/delete/', views.PartnershipProgramDeleteView.as_view(), name='partnershipprogram_delete'),

    # Partner URLs
    path('partner/', views.PartnerListView.as_view(), name='partner_list'),
    path('partner/<int:pk>/', views.PartnerDetailView.as_view(), name='partner_detail'),
    path('partner/create/', views.PartnerCreateView.as_view(), name='partner_create'),
    path('partner/<int:pk>/update/', views.PartnerUpdateView.as_view(), name='partner_update'),
    path('partner/<int:pk>/delete/', views.PartnerDeleteView.as_view(), name='partner_delete'),

    # InteractionLog URLs
    path('interactionlog/', views.InteractionLogListView.as_view(), name='interactionlog_list'),
    path('interactionlog/<int:pk>/', views.InteractionLogDetailView.as_view(), name='interactionlog_detail'),
    path('interactionlog/create/', views.InteractionLogCreateView.as_view(), name='interactionlog_create'),
    path('interactionlog/<int:pk>/update/', views.InteractionLogUpdateView.as_view(), name='interactionlog_update'),
    path('interactionlog/<int:pk>/delete/', views.InteractionLogDeleteView.as_view(), name='interactionlog_delete'),
] 