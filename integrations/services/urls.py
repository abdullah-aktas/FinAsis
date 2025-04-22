from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('services', views.ServiceViewSet)
router.register('integrations', views.IntegrationViewSet)

app_name = 'ext_services'

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
] 