from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BackupConfigViewSet,
    BackupStorageViewSet,
    BackupRecordViewSet,
    BackupLogViewSet
)

router = DefaultRouter()
router.register(r'configs', BackupConfigViewSet, basename='backup-config')
router.register(r'storages', BackupStorageViewSet, basename='backup-storage')
router.register(r'records', BackupRecordViewSet, basename='backup-record')
router.register(r'logs', BackupLogViewSet, basename='backup-log')

urlpatterns = [
    # Ana API endpoint'leri
    path('', include(router.urls)),
    
    # Özel endpoint'ler
    path('configs/<int:pk>/run/', BackupConfigViewSet.as_view({'post': 'run_backup'}), name='run-backup'),
    path('storages/<int:pk>/test/', BackupStorageViewSet.as_view({'post': 'test_connection'}), name='test-storage'),
    path('records/<int:pk>/restore/', BackupRecordViewSet.as_view({'post': 'restore'}), name='restore-backup'),
    path('records/<int:pk>/logs/', BackupRecordViewSet.as_view({'get': 'logs'}), name='backup-logs'),
] 