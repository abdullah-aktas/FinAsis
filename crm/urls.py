from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Müşteri URL'leri
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # İletişim Kişisi URL'leri
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/create/', views.contact_create, name='contact_create'),
    path('contacts/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('contacts/<int:pk>/update/', views.contact_update, name='contact_update'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    
    # Fırsat URL'leri
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/create/', views.opportunity_create, name='opportunity_create'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:pk>/update/', views.opportunity_update, name='opportunity_update'),
    path('opportunities/<int:pk>/delete/', views.opportunity_delete, name='opportunity_delete'),
    
    # Aktivite URL'leri
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activities/<int:pk>/update/', views.activity_update, name='activity_update'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    
    # Belge URL'leri
    path('documents/', views.document_list, name='document_list'),
    path('documents/create/', views.document_create, name='document_create'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:pk>/update/', views.document_update, name='document_update'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
] 