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
] 