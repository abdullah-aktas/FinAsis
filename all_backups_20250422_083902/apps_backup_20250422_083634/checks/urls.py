from django.urls import path
from . import views

app_name = 'check_management'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Banka URL'leri
    path('banks/', views.bank_list, name='bank_list'),
    path('banks/create/', views.bank_create, name='bank_create'),
    
    # Çek URL'leri
    path('checks/', views.check_list, name='check_list'),
    path('checks/create/', views.check_create, name='check_create'),
    path('checks/<int:pk>/', views.check_detail, name='check_detail'),
    path('checks/<int:pk>/update/', views.check_update, name='check_update'),
    path('checks/<int:pk>/delete/', views.check_delete, name='check_delete'),
    path('checks/<int:check_pk>/transaction/create/', views.check_transaction_create, name='check_transaction_create'),
    
    # Senet URL'leri
    path('notes/', views.promissory_note_list, name='promissory_note_list'),
    path('notes/create/', views.promissory_note_create, name='promissory_note_create'),
    path('notes/<int:pk>/', views.promissory_note_detail, name='promissory_note_detail'),
    path('notes/<int:pk>/update/', views.promissory_note_update, name='promissory_note_update'),
    path('notes/<int:pk>/delete/', views.promissory_note_delete, name='promissory_note_delete'),
    path('notes/<int:note_pk>/transaction/create/', views.promissory_note_transaction_create, name='promissory_note_transaction_create'),
] 