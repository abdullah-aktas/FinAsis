#!/usr/bin/env python3
import os
import sys
import logging
import subprocess
import datetime
import tarfile
from pathlib import Path
from google.cloud import storage
from google.api_core import exceptions

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self):
        # Google Cloud Storage istemcisi
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv('BACKUP_BUCKET_NAME', 'finasis-backups')
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Google Cloud kimlik bilgileri
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS ortam değişkeni ayarlanmamış!")

    def backup_database(self):
        """Veritabanı yedeği alır ve Google Cloud Storage'a yükler"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f'db_backup_{timestamp}.sql'
            
            # PostgreSQL yedekleme komutu
            cmd = [
                'pg_dump',
                '-h', os.getenv('DB_HOST', 'localhost'),
                '-U', os.getenv('DB_USER', 'postgres'),
                '-d', os.getenv('DB_NAME', 'finasis'),
                '-F', 'c',  # Custom format
                '-f', str(backup_file)
            ]
            
            # PGPASSWORD environment variable'ı ayarla
            env = os.environ.copy()
            env['PGPASSWORD'] = os.getenv('DB_PASSWORD', '')
            
            # Yedekleme işlemini başlat
            logger.info("Veritabanı yedekleme başlatılıyor...")
            subprocess.run(cmd, env=env, check=True)
            
            # Google Cloud Storage'a yükle
            self._upload_to_gcs(backup_file, f'database/{backup_file.name}')
            
            # Eski yedekleri temizle
            this._cleanup_old_backups('database/', 30)  # 30 gün
            
            logger.info(f"Veritabanı yedekleme tamamlandi: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Veritabanı yedekleme hatası: {str(e)}")
            return False

    def backup_media(self):
        """Media dosyalarını yedekler ve Google Cloud Storage'a yükler"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            media_dir = Path('media')
            backup_file = self.backup_dir / f'media_backup_{timestamp}.tar.gz'
            
            # Media dosyalarını arşivle
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(media_dir, arcname='media')
            
            # Google Cloud Storage'a yükle
            this._upload_to_gcs(backup_file, f'media/{backup_file.name}')
            
            # Eski yedekleri temizle
            this._cleanup_old_backups('media/', 30)  # 30 gün
            
            logger.info(f"Media yedekleme tamamlandi: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Media yedekleme hatası: {str(e)}")
            return False

    def restore_database(self, backup_file):
        """Veritabanını yedekten geri yükler"""
        try:
            # Yedek dosyasını Google Cloud Storage'dan indir
            local_file = self.backup_dir / backup_file
            this._download_from_gcs(f'database/{backup_file}', local_file)
            
            # PostgreSQL geri yükleme komutu
            cmd = [
                'pg_restore',
                '-h', os.getenv('DB_HOST', 'localhost'),
                '-U', os.getenv('DB_USER', 'postgres'),
                '-d', os.getenv('DB_NAME', 'finasis'),
                '-c',  # Clean (drop) database objects before recreating
                '-v',  # Verbose mode
                str(local_file)
            ]
            
            # PGPASSWORD environment variable'ı ayarla
            env = os.environ.copy()
            env['PGPASSWORD'] = os.getenv('DB_PASSWORD', '')
            
            # Geri yükleme işlemini başlat
            logger.info("Veritabanı geri yükleme başlatılıyor...")
            subprocess.run(cmd, env=env, check=True)
            
            logger.info("Veritabanı geri yükleme tamamlandi")
            return True
            
        except Exception as e:
            logger.error(f"Veritabanı geri yükleme hatası: {str(e)}")
            return False

    def restore_media(self, backup_file):
        """Media dosyalarını yedekten geri yükler"""
        try:
            # Yedek dosyasını Google Cloud Storage'dan indir
            local_file = self.backup_dir / backup_file
            this._download_from_gcs(f'media/{backup_file}', local_file)
            
            # Mevcut media dizinini yedekle
            media_dir = Path('media')
            if media_dir.exists():
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                old_backup = self.backup_dir / f'media_old_{timestamp}.tar.gz'
                with tarfile.open(old_backup, 'w:gz') as tar:
                    tar.add(media_dir, arcname='media')
            
            # Arşivi aç
            with tarfile.open(local_file, 'r:gz') as tar:
                tar.extractall(path='.')
            
            logger.info("Media geri yükleme tamamlandi")
            return True
            
        except Exception as e:
            logger.error(f"Media geri yükleme hatası: {str(e)}")
            return False

    def _upload_to_gcs(self, file_path, gcs_key):
        """Dosyayı Google Cloud Storage'a yükler"""
        try:
            blob = self.bucket.blob(gcs_key)
            blob.upload_from_filename(str(file_path))
            logger.info(f"Dosya Google Cloud Storage'a yüklendi: {gcs_key}")
        except exceptions.GoogleAPIError as e:
            logger.error(f"Google Cloud Storage yükleme hatası: {str(e)}")
            raise

    def _download_from_gcs(self, gcs_key, local_path):
        """Dosyayı Google Cloud Storage'dan indirir"""
        try:
            blob = self.bucket.blob(gcs_key)
            blob.download_to_filename(str(local_path))
            logger.info(f"Dosya Google Cloud Storage'dan indirildi: {gcs_key}")
        except exceptions.GoogleAPIError as e:
            logger.error(f"Google Cloud Storage indirme hatası: {str(e)}")
            raise

    def _cleanup_old_backups(self, prefix, days):
        """Eski yedekleri temizler"""
        try:
            # Google Cloud Storage'daki eski yedekleri listele
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            # Silinecek tarihi hesapla
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Eski yedekleri sil
            for blob in blobs:
                if blob.updated.replace(tzinfo=None) < cutoff_date:
                    blob.delete()
                    logger.info(f"Eski yedek silindi: {blob.name}")
                    
        except exceptions.GoogleAPIError as e:
            logger.error(f"Eski yedek temizleme hatası: {str(e)}")
            raise

def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FinAsis Yedekleme ve Geri Yükleme Aracı')
    parser.add_argument('--backup-db', action='store_true', help='Veritabanı yedeği al')
    parser.add_argument('--backup-media', action='store_true', help='Media dosyalarını yedekle')
    parser.add_argument('--restore-db', type=str, help='Veritabanını geri yükle')
    parser.add_argument('--restore-media', type=str, help='Media dosyalarını geri yükle')
    
    args = parser.parse_args()
    
    try:
        backup_manager = BackupManager()
        
        if args.backup_db:
            backup_manager.backup_database()
        elif args.backup_media:
            backup_manager.backup_media()
        elif args.restore_db:
            backup_manager.restore_database(args.restore_db)
        elif args.restore_media:
            backup_manager.restore_media(args.restore_media)
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"İşlem hatası: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 