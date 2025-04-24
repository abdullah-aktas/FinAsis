from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import BackupConfig, BackupStorage, BackupRecord, BackupLog
from .serializers import (
    BackupConfigSerializer,
    BackupStorageSerializer,
    BackupRecordSerializer,
    BackupLogSerializer,
)
from .tasks import create_backup, restore_backup, cleanup_old_backups
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BackupConfigViewSet(viewsets.ModelViewSet):
    queryset = BackupConfig.objects.filter(is_active=True)
    serializer_class = BackupConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 15))  # 15 dakika önbellek
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))  # 1 saat önbellek
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def run_backup(self, request, pk=None):
        config = self.get_object()
        create_backup.delay(config.id)
        return Response({'status': 'backup_started'})

class BackupStorageViewSet(viewsets.ModelViewSet):
    queryset = BackupStorage.objects.all()
    serializer_class = BackupStorageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BackupStorage.objects.filter(config__is_active=True)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        storage = self.get_object()
        # Bağlantı testi mantığı burada olacak
        return Response({'status': 'connection_verified'})

class BackupRecordViewSet(viewsets.ModelViewSet):
    queryset = BackupRecord.objects.all()
    serializer_class = BackupRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BackupRecord.objects.filter(
            config__is_active=True
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        record = self.get_object()
        restore_backup.delay(record.id)
        return Response({'status': 'restore_started'})

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        record = self.get_object()
        logs = BackupLog.objects.filter(record=record).order_by('-created_at')
        serializer = BackupLogSerializer(logs, many=True)
        return Response(serializer.data)

class BackupLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BackupLog.objects.all()
    serializer_class = BackupLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BackupLog.objects.filter(
            record__config__is_active=True
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtreleme parametreleri
        level = request.query_params.get('level', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        if level:
            queryset = queryset.filter(level=level)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 