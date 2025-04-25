from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'edocument'

# Ana router
router = DefaultRouter()
router.register(r'documents', views.EDocumentViewSet, basename='document')
router.register(r'despatches', views.EDespatchAdviceViewSet, basename='despatch')

# E-Fatura nested router
document_router = routers.NestedDefaultRouter(router, r'documents', lookup='document')
document_router.register(r'items', views.EDocumentItemViewSet, basename='document-item')
document_router.register(r'logs', views.EDocumentLogViewSet, basename='document-log')

# E-İrsaliye nested router
despatch_router = routers.NestedDefaultRouter(router, r'despatches', lookup='despatch')
despatch_router.register(r'items', views.EDespatchAdviceItemViewSet, basename='despatch-item')
despatch_router.register(r'logs', views.EDespatchAdviceLogViewSet, basename='despatch-log')

# Template view URL'leri
urlpatterns = [
    # API URL'leri
    path('api/', include(router.urls)),
    path('api/', include(document_router.urls)),
    path('api/', include(despatch_router.urls)),
    
    # Template view URL'leri
    path('despatch-logs/', views.EDespatchAdviceLogListView.as_view(), name='edespatchadvicelog_list'),
    path('despatch-logs/<int:pk>/', views.EDespatchAdviceLogDetailView.as_view(), name='edespatchadvicelog_detail'),
    path('despatch-logs/create/', views.EDespatchAdviceLogCreateView.as_view(), name='edespatchadvicelog_create'),
    path('despatch-logs/<int:pk>/update/', views.EDespatchAdviceLogUpdateView.as_view(), name='edespatchadvicelog_update'),
    path('despatch-logs/<int:pk>/delete/', views.EDespatchAdviceLogDeleteView.as_view(), name='edespatchadvicelog_delete'),
] 