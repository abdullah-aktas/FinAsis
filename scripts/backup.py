# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import os
import sys
import logging
import subprocess
import datetime
import tarfile
import hashlib
import shutil
import json
from pathlib import Path
from google.cloud import storage
from google.api_core import exceptions
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any, Set
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from dataclasses import dataclass
from enum import Enum

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

class BackupType(Enum):
    DATABASE = "database"
    MEDIA = "media"

@dataclass
class BackupMetadata:
    type: BackupType
    timestamp: str
    file_name: str
    hash: str
    size: int
    gcs_path: str
    encryption_key: Optional[str] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class BackupManager:
    def __init__(self):
        self._validate_environment()
        self.storage_client = storage.Client()
        self.bucket_name = os.getenv('BACKUP_BUCKET_NAME', 'finasis-backups')
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
        self.encryption_key = self._generate_encryption_key()
        self.metadata_file = self.backup_dir / 'backup_metadata.json'
        self._load_metadata()
        
    def _validate_environment(self):
        """Ortam değişkenlerini kontrol et"""
        required_vars = [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'DB_HOST',
            'DB_USER',
            'DB_NAME',
            'DB_PASSWORD',
            'BACKUP_ENCRYPTION_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Eksik ortam değişkenleri: {', '.join(missing_vars)}")

    def _generate_encryption_key(self) -> bytes:
        """Şifreleme anahtarı oluştur"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(os.getenv('BACKUP_ENCRYPTION_KEY').encode()))
        return key

    def _load_metadata(self):
        """Yedek metadata dosyasını yükle"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    self.metadata = {
                        'backups': [BackupMetadata(**item) for item in data.get('backups', [])]
                    }
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Metadata dosyası bozuk, yeni bir dosya oluşturuluyor: {e}")
                self.metadata = {'backups': []}
        else:
            self.metadata = {'backups': []}

    def _save_metadata(self):
        """Yedek metadata dosyasını kaydet"""
        with open(self.metadata_file, 'w') as f:
            data = {
                'backups': [
                    {
                        'type': item.type.value,
                        'timestamp': item.timestamp,
                        'file_name': item.file_name,
                        'hash': item.hash,
                        'size': item.size,
                        'gcs_path': item.gcs_path,
                        'encryption_key': item.encryption_key,
                        'dependencies': item.dependencies
                    }
                    for item in self.metadata['backups']
                ]
            }
            json.dump(data, f, indent=4)

    def backup_database(self) -> bool:
        """Veritabanı yedeği alır ve Google Cloud Storage'a yükler"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f'db_backup_{timestamp}.sql'
            
            # PostgreSQL yedekleme komutu
            cmd = [
                'pg_dump',
                '-h', os.getenv('DB_HOST'),
                '-U', os.getenv('DB_USER'),
                '-d', os.getenv('DB_NAME'),
                '-F', 'c',  # Custom format
                '-Z', '9',  # Maximum compression
                '-f', str(backup_file)
            ]
            
            # PGPASSWORD environment variable'ı ayarla
            env = os.environ.copy()
            env['PGPASSWORD'] = os.getenv('DB_PASSWORD')
            
            # Yedekleme işlemini başlat
            logger.info("Veritabanı yedekleme başlatılıyor...")
            subprocess.run(cmd, env=env, check=True)
            
            # Dosya bütünlüğünü kontrol et
            file_hash = self._verify_file_integrity(backup_file)
            if not file_hash:
                raise ValueError("Yedek dosyası bütünlük kontrolünden geçemedi")
            
            # Şifreleme
            encrypted_file = self._encrypt_file(backup_file)
            
            # Google Cloud Storage'a yükle
            gcs_path = f'database/{encrypted_file.name}'
            self._upload_to_gcs(encrypted_file, gcs_path)
            
            # Metadata güncelle
            backup_metadata = BackupMetadata(
                type=BackupType.DATABASE,
                timestamp=timestamp,
                file_name=encrypted_file.name,
                hash=file_hash,
                size=os.path.getsize(encrypted_file),
                gcs_path=gcs_path,
                encryption_key=base64.urlsafe_b64encode(self.encryption_key).decode(),
                dependencies=['database']
            )
            self.metadata['backups'].append(backup_metadata)
            self._save_metadata()
            
            # Eski yedekleri temizle
            self._cleanup_old_backups('database/', 30)  # 30 gün
            
            logger.info(f"Veritabanı yedekleme tamamlandi: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Veritabanı yedekleme hatası: {str(e)}")
            return False

    def _verify_file_integrity(self, file_path: Path) -> Optional[str]:
        """Dosya bütünlüğünü kontrol et ve hash değerini döndür"""
        try:
            # SHA-256 hash hesapla
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            file_hash = sha256_hash.hexdigest()
            
            # Hash'i kaydet
            hash_file = file_path.with_suffix('.sha256')
            with open(hash_file, 'w') as f:
                f.write(file_hash)
            
            return file_hash
        except Exception as e:
            logger.error(f"Dosya bütünlük kontrolü hatası: {str(e)}")
            return None

    def _encrypt_file(self, file_path: Path) -> Path:
        """Dosyayı şifrele"""
        try:
            encrypted_file = file_path.with_suffix('.enc')
            fernet = Fernet(self.encryption_key)
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = fernet.encrypt(data)
            
            with open(encrypted_file, 'wb') as f:
                f.write(encrypted_data)
            
            return encrypted_file
        except Exception as e:
            logger.error(f"Dosya şifreleme hatası: {str(e)}")
            raise

    def _decrypt_file(self, file_path: Path) -> Path:
        """Dosyanın şifresini çöz"""
        try:
            decrypted_file = file_path.with_suffix('')
            fernet = Fernet(self.encryption_key)
            
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            
            with open(decrypted_file, 'wb') as f:
                f.write(decrypted_data)
            
            return decrypted_file
        except Exception as e:
            logger.error(f"Dosya şifre çözme hatası: {str(e)}")
            raise

    def _upload_to_gcs(self, file_path: Path, gcs_key: str):
        """Dosyayı Google Cloud Storage'a yükler"""
        try:
            blob = self.bucket.blob(gcs_key)
            blob.upload_from_filename(str(file_path))
            logger.info(f"Dosya Google Cloud Storage'a yüklendi: {gcs_key}")
        except exceptions.GoogleAPIError as e:
            logger.error(f"Google Cloud Storage yükleme hatası: {str(e)}")
            raise

    def _download_from_gcs(self, gcs_key: str, local_path: Path):
        """Dosyayı Google Cloud Storage'dan indirir"""
        try:
            blob = self.bucket.blob(gcs_key)
            blob.download_to_filename(str(local_path))
            logger.info(f"Dosya Google Cloud Storage'dan indirildi: {gcs_key}")
        except exceptions.GoogleAPIError as e:
            logger.error(f"Google Cloud Storage indirme hatası: {str(e)}")
            raise

    def _cleanup_old_backups(self, prefix: str, days: int):
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

    def restore_database(self, backup_file: str) -> bool:
        """Veritabanını yedekten geri yükler"""
        try:
            # Yedek dosyasını Google Cloud Storage'dan indir
            local_file = self.backup_dir / backup_file
            self._download_from_gcs(f'database/{backup_file}', local_file)
            
            # Şifreyi çöz
            decrypted_file = self._decrypt_file(local_file)
            
            # PostgreSQL geri yükleme komutu
            cmd = [
                'pg_restore',
                '-h', os.getenv('DB_HOST', 'localhost'),
                '-U', os.getenv('DB_USER', 'postgres'),
                '-d', os.getenv('DB_NAME', 'finasis'),
                '-c',  # Clean (drop) database objects before recreating
                '-v',  # Verbose mode
                str(decrypted_file)
            ]
            
            # PGPASSWORD environment variable'ı ayarla
            env = os.environ.copy()
            env['PGPASSWORD'] = os.getenv('DB_PASSWORD', '')
            
            # Geri yükleme işlemini başlat
            logger.info("Veritabanı geri yükleme başlatılıyor...")
            subprocess.run(cmd, env=env, check=True)
            
            logger.info("Veritabanı geri yükleme tamamlandı.")
            return True
            
        except Exception as e:
            logger.error(f"Veritabanı geri yükleme hatası: {str(e)}")
            return False

    def backup_media(self) -> bool:
        """Media dosyalarını yedekler ve Google Cloud Storage'a yükler"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            media_dir = Path('media')
            backup_file = self.backup_dir / f'media_backup_{timestamp}.tar.gz'
            
            # Media dosyalarını arşivle
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(media_dir, arcname='media')
            
            # Dosya bütünlüğünü kontrol et
            if not self._verify_file_integrity(backup_file):
                raise ValueError("Yedek dosyası bütünlük kontrolünden geçemedi")
            
            # Şifreleme
            if self.encryption_key:
                backup_file = self._encrypt_file(backup_file)
            
            # Google Cloud Storage'a yükle
            self._upload_to_gcs(backup_file, f'media/{backup_file.name}')
            
            # Eski yedekleri temizle
            self._cleanup_old_backups('media/', 30)  # 30 gün
            
            logger.info(f"Media yedekleme tamamlandi: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Media yedekleme hatası: {str(e)}")
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

def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FinAsis Yedekleme ve Geri Yükleme Aracı')
    parser.add_argument('--backup-db', action='store_true', help='Veritabanı yedeği al')
    parser.add_argument('--backup-media', action='store_true', help='Media dosyalarını yedekle')
    parser.add_argument('--restore-db', type=str, help='Veritabanını geri yükle')
    parser.add_argument('--restore-media', type=str, help='Media dosyalarını geri yükle')
    parser.add_argument('--list-backups', action='store_true', help='Mevcut yedekleri listele')
    
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
        elif args.list_backups:
            print(json.dumps(backup_manager.metadata, indent=4))
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"İşlem hatası: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 