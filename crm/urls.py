"""
CRM Modülü - URL Yapılandırması
------------------------------
Bu dosya, Müşteri İlişkileri Yönetimi modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/crm/ - Ana CRM API endpoint'i
- /api/v1/crm/customers/ - Müşteri yönetimi
- /api/v1/crm/contacts/ - İletişim yönetimi
- /api/v1/crm/opportunities/ - Fırsat yönetimi
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'crm'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'opportunities', views.OpportunityViewSet, basename='opportunity')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Müşteri Yönetimi
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/<uuid:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<uuid:pk>/update/', views.CustomerUpdateView.as_view(), name='customer-update'),
    path('customers/<uuid:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer-delete'),
    
    # İletişim Yönetimi
    path('contacts/', views.ContactListView.as_view(), name='contact-list'),
    path('contacts/<uuid:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/create/', views.ContactCreateView.as_view(), name='contact-create'),
    path('contacts/<uuid:pk>/update/', views.ContactUpdateView.as_view(), name='contact-update'),
    path('contacts/<uuid:pk>/delete/', views.ContactDeleteView.as_view(), name='contact-delete'),
    
    # Fırsat Yönetimi
    path('opportunities/', views.OpportunityListView.as_view(), name='opportunity-list'),
    path('opportunities/<uuid:pk>/', views.OpportunityDetailView.as_view(), name='opportunity-detail'),
    path('opportunities/create/', views.OpportunityCreateView.as_view(), name='opportunity-create'),
    path('opportunities/<uuid:pk>/update/', views.OpportunityUpdateView.as_view(), name='opportunity-update'),
    path('opportunities/<uuid:pk>/delete/', views.OpportunityDeleteView.as_view(), name='opportunity-delete'),
    
    # CRM Raporları
    path('reports/customer-analysis/', views.CustomerAnalysisView.as_view(), name='customer-analysis'),
    path('reports/sales-performance/', views.SalesPerformanceView.as_view(), name='sales-performance'),
    path('reports/opportunity-funnel/', views.OpportunityFunnelView.as_view(), name='opportunity-funnel'),
] 