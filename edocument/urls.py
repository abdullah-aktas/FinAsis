from django.urls import path
from . import views

app_name = 'edocument'

urlpatterns = [
    # E-Fatura URL'leri
    path('', views.document_list, name='document_list'),
    path('<uuid:uuid>/', views.document_detail, name='document_detail'),
    path('<uuid:uuid>/send/', views.send_document, name='send_document'),
    path('<uuid:uuid>/preview-xml/', views.preview_xml, name='preview_xml'),
    
    # E-İrsaliye URL'leri
    path('despatch/', views.despatch_list, name='despatch_list'),
    path('despatch/<uuid:uuid>/', views.despatch_detail, name='despatch_detail'),
    path('despatch/<uuid:uuid>/send/', views.send_despatch, name='send_despatch'),
    path('despatch/<uuid:uuid>/preview-xml/', views.preview_despatch_xml, name='preview_despatch_xml'),
    path('despatch/<uuid:uuid>/accept/', views.accept_despatch, name='accept_despatch'),
    path('despatch/<uuid:uuid>/reject/', views.reject_despatch, name='reject_despatch'),
    path('document/<int:document_id>/xml-preview/', views.xml_preview, name='xml_preview'),
] 