# -*- coding: utf-8 -*-
from celery import shared_task
from django.core.cache import cache
from .models import BackupConfig, BackupRecord, BackupLog
import logging
import os
import shutil
import hashlib
from datetime import datetime, timedelta
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage

logger = logging.getLogger(__name__)

@shared_task
def create_backup(config_id):
    """
    Yedekleme oluşturur.
    """
    try:
        config = BackupConfig.objects.get(id=config_id)
        storage = config.storages.first()
        
        # Yedekleme kaydı oluştur
        record = BackupRecord.objects.create(
            config=config,
            storage=storage,
            status='in_progress',
            started_at=datetime.now()
        )
        
        # Log kaydı
        BackupLog.objects.create(
            record=record,
            level='info',
            message='Yedekleme başlatıldı'
        )
        
        # Yedekleme yolu
        backup_path = os.path.join(
            storage.storage_path,
            f"backup_{record.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Yedekleme işlemi
        if config.backup_type == 'full':
            # Tam yedek
            backup_data = perform_full_backup()
        elif config.backup_type == 'incremental':
            # Artırımlı yedek
            backup_data = perform_incremental_backup(config)
        else:
            # Fark yedek
            backup_data = perform_differential_backup(config)
        
        # Yedekleme dosyasını kaydet
        save_backup(backup_data, backup_path, storage)
        
        # Kontrol toplamı hesapla
        checksum = calculate_checksum(backup_path)
        
        # Kaydı güncelle
        record.backup_path = backup_path
        record.size_bytes = os.path.getsize(backup_path)
        record.checksum = checksum
        record.status = 'completed'
        record.completed_at = datetime.now()
        record.save()
        
        # Log kaydı
        BackupLog.objects.create(
            record=record,
            level='info',
            message='Yedekleme tamamlandı'
        )
        
    except Exception as e:
        logger.error(f"Yedekleme hatası: {str(e)}")
        if 'record' in locals():
            record.status = 'failed'
            record.error_message = str(e)
            record.completed_at = datetime.now()
            record.save()
            
            BackupLog.objects.create(
                record=record,
                level='error',
                message=f"Yedekleme hatası: {str(e)}"
            )
        raise

@shared_task
def restore_backup(record_id):
    """
    Yedekten geri yükleme yapar.
    """
    try:
        record = BackupRecord.objects.get(id=record_id)
        
        # Log kaydı
        BackupLog.objects.create(
            record=record,
            level='info',
            message='Geri yükleme başlatıldı'
        )
        
        # Yedekten geri yükleme
        restore_from_backup(record)
        
        # Kaydı güncelle
        record.status = 'restored'
        record.save()
        
        # Log kaydı
        BackupLog.objects.create(
            record=record,
            level='info',
            message='Geri yükleme tamamlandı'
        )
        
    except Exception as e:
        logger.error(f"Geri yükleme hatası: {str(e)}")
        if 'record' in locals():
            BackupLog.objects.create(
                record=record,
                level='error',
                message=f"Geri yükleme hatası: {str(e)}"
            )
        raise

@shared_task
def cleanup_old_backups():
    """
    Eski yedekleri temizler.
    """
    try:
        configs = BackupConfig.objects.filter(is_active=True)
        for config in configs:
            # Saklama süresini aşan yedekleri bul
            cutoff_date = datetime.now() - timedelta(days=config.retention_days)
            old_records = BackupRecord.objects.filter(
                config=config,
                created_at__lt=cutoff_date
            )
            
            for record in old_records:
                try:
                    # Yedek dosyasını sil
                    if os.path.exists(record.backup_path):
                        os.remove(record.backup_path)
                    
                    # Kaydı sil
                    record.delete()
                    
                    logger.info(f"Eski yedek silindi: {record.backup_path}")
                    
                except Exception as e:
                    logger.error(f"Yedek silme hatası: {str(e)}")
                    continue
                    
    except Exception as e:
        logger.error(f"Temizleme hatası: {str(e)}")
        raise

def perform_full_backup():
    """
    Tam yedek oluşturur.
    """
    # Tam yedekleme mantığı
    pass

def perform_incremental_backup(config):
    """
    Artırımlı yedek oluşturur.
    """
    # Artırımlı yedekleme mantığı
    pass

def perform_differential_backup(config):
    """
    Fark yedek oluşturur.
    """
    # Fark yedekleme mantığı
    pass

def save_backup(data, path, storage):
    """
    Yedeklemeyi kaydeder.
    """
    if storage.config.storage_type == 'local':
        # Yerel depolama
        with open(path, 'wb') as f:
            f.write(data)
            
    elif storage.config.storage_type == 's3':
        # Amazon S3
        s3 = boto3.client('s3', **storage.credentials)
        s3.upload_fileobj(data, storage.credentials['bucket'], path)
        
    elif storage.config.storage_type == 'azure':
        # Azure Blob
        blob_service = BlobServiceClient(**storage.credentials)
        blob_client = blob_service.get_blob_client(container=storage.credentials['container'], blob=path)
        blob_client.upload_blob(data)
        
    elif storage.config.storage_type == 'gcp':
        # Google Cloud Storage
        client = storage.Client(**storage.credentials)
        bucket = client.bucket(storage.credentials['bucket'])
        blob = bucket.blob(path)
        blob.upload_from_string(data)

def restore_from_backup(record):
    """
    Yedekten geri yükleme yapar.
    """
    if record.storage.config.storage_type == 'local':
        # Yerel depolama
        with open(record.backup_path, 'rb') as f:
            data = f.read()
            
    elif record.storage.config.storage_type == 's3':
        # Amazon S3
        s3 = boto3.client('s3', **record.storage.credentials)
        data = s3.get_object(Bucket=record.storage.credentials['bucket'], Key=record.backup_path)['Body'].read()
        
    elif record.storage.config.storage_type == 'azure':
        # Azure Blob
        blob_service = BlobServiceClient(**record.storage.credentials)
        blob_client = blob_service.get_blob_client(container=record.storage.credentials['container'], blob=record.backup_path)
        data = blob_client.download_blob().readall()
        
    elif record.storage.config.storage_type == 'gcp':
        # Google Cloud Storage
        client = storage.Client(**record.storage.credentials)
        bucket = client.bucket(record.storage.credentials['bucket'])
        blob = bucket.blob(record.backup_path)
        data = blob.download_as_bytes()
    
    # Geri yükleme işlemi
    # ...

def calculate_checksum(file_path):
    """
    Dosya kontrol toplamını hesaplar.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() 