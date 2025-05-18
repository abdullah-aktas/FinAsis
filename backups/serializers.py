# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import BackupConfig, BackupStorage, BackupRecord, BackupLog

class BackupConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupConfig
        fields = [
            'id', 'name', 'backup_type', 'storage_type',
            'schedule', 'retention_days', 'is_active'
        ]
        read_only_fields = ['id']

class BackupStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupStorage
        fields = [
            'id', 'config', 'storage_path',
            'is_encrypted'
        ]
        read_only_fields = ['id']

    def validate_credentials(self, value):
        # Kimlik bilgileri doğrulama mantığı
        return value

class BackupRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupRecord
        fields = [
            'id', 'config', 'storage', 'backup_path',
            'size_bytes', 'checksum', 'status',
            'started_at', 'completed_at', 'error_message'
        ]
        read_only_fields = [
            'id', 'status', 'started_at',
            'completed_at', 'error_message'
        ]

    def validate(self, data):
        if data['config'].backup_type == 'incremental':
            # Artırımlı yedek için önceki yedek kontrolü
            last_backup = BackupRecord.objects.filter(
                config=data['config'],
                status='completed'
            ).order_by('-created_at').first()
            
            if not last_backup:
                raise serializers.ValidationError(
                    "Artırımlı yedek için önceki yedek bulunamadı"
                )
        return data

class BackupLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupLog
        fields = ['id', 'record', 'level', 'message', 'created_at']
        read_only_fields = ['id', 'created_at'] 