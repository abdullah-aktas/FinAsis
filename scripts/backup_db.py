# -*- coding: utf-8 -*-
import os
import sys
import datetime
import subprocess
from pathlib import Path
from typing import Dict, Optional
from decouple import config

def get_env() -> Dict[str, str]:
    """Ortam değişkenlerini döndürür"""
    return {'PGPASSWORD': str(config('DB_PASSWORD'))}

def create_backup():
    """Veritabanı yedeği oluşturur"""
    try:
        # Yedekleme dizini oluştur
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)

        # Yedek dosya adı oluştur
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'backup_{timestamp}.sql'

        # PostgreSQL yedekleme komutu
        command = [
            'pg_dump',
            '-h', str(config('DB_HOST')),
            '-U', str(config('DB_USER')),
            '-d', str(config('DB_NAME')),
            '-F', 'c',  # Custom format
            '-f', str(backup_file)
        ]

        # Yedekleme işlemini başlat
        subprocess.run(command, env=get_env(), check=True)
        print(f'Veritabanı yedeği başarıyla oluşturuldu: {backup_file}')

        # AWS S3'e yedekleme
        if config('USE_S3_BACKUP', cast=bool, default=False):
            s3_backup(backup_file)

    except Exception as e:
        print(f'Yedekleme hatası: {e}')
        sys.exit(1)

def restore_backup(backup_file: str):
    """Veritabanı yedeğini geri yükler"""
    try:
        if not os.path.exists(backup_file):
            print(f'Yedek dosyası bulunamadı: {backup_file}')
            sys.exit(1)

        # Mevcut bağlantıları sonlandır
        kill_connections()

        # PostgreSQL geri yükleme komutu
        command = [
            'pg_restore',
            '-h', str(config('DB_HOST')),
            '-U', str(config('DB_USER')),
            '-d', str(config('DB_NAME')),
            '-c',  # Clean (drop) database objects before recreating
            '-F', 'c',  # Custom format
            str(backup_file)
        ]

        # Geri yükleme işlemini başlat
        subprocess.run(command, env=get_env(), check=True)
        print(f'Veritabanı yedeği başarıyla geri yüklendi: {backup_file}')

    except Exception as e:
        print(f'Geri yükleme hatası: {e}')
        sys.exit(1)

def kill_connections():
    """Veritabanına olan tüm bağlantıları sonlandırır"""
    try:
        command = f"""
        psql -h {str(config('DB_HOST'))} -U {str(config('DB_USER'))} -d {str(config('DB_NAME'))} -c "
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{str(config('DB_NAME'))}'
        AND pid <> pg_backend_pid();"
        """
        subprocess.run(command, shell=True, env=get_env(), check=True)
    except Exception as e:
        print(f'Bağlantı sonlandırma hatası: {e}')

def s3_backup(backup_file):
    """Yedeği AWS S3'e yükler"""
    try:
        import boto3

        s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name=config('AWS_S3_REGION_NAME')
        )

        bucket_name = config('AWS_BACKUP_BUCKET_NAME')
        s3_key = f'db_backups/{backup_file.name}'

        # S3'e yükle
        s3.upload_file(str(backup_file), bucket_name, s3_key)
        print(f'Yedek S3\'e yüklendi: s3://{bucket_name}/{s3_key}')

    except Exception as e:
        print(f'S3 yükleme hatası: {e}')

def cleanup_old_backups():
    """30 günden eski yedekleri temizler"""
    try:
        backup_dir = Path('backups')
        if not backup_dir.exists():
            return

        # 30 gün önceki tarihi hesapla
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)

        # Eski yedekleri temizle
        for backup_file in backup_dir.glob('backup_*.sql'):
            # Dosya tarihini al
            file_date_str = backup_file.stem.split('_')[1]
            file_date = datetime.datetime.strptime(file_date_str, '%Y%m%d')

            if file_date < cutoff_date:
                backup_file.unlink()
                print(f'Eski yedek silindi: {backup_file}')

    except Exception as e:
        print(f'Temizleme hatası: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Kullanım: python backup_db.py [backup|restore] [yedek_dosyası]')
        sys.exit(1)

    action = sys.argv[1]

    if action == 'backup':
        create_backup()
        cleanup_old_backups()
    elif action == 'restore':
        if len(sys.argv) < 3:
            print('Geri yükleme için yedek dosyası belirtilmeli')
            sys.exit(1)
        restore_backup(sys.argv[2])
    else:
        print('Geçersiz işlem. Kullanım: python backup_db.py [backup|restore] [yedek_dosyası]')
        sys.exit(1) 