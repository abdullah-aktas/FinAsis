#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Veritabanı kontrol scripti.
"""
import os
import sys
import django
import psycopg2
import logging
from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line
from django.db.migrations.executor import MigrationExecutor

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Veritabanı bağlantısını kontrol et"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            logger.info(f"✓ Veritabanı bağlantısı başarılı (PostgreSQL {version})")
        return True
    except Exception as e:
        logger.error(f"✗ Veritabanı bağlantı hatası: {str(e)}")
        return False

def check_migrations():
    """Bekleyen migrasyonları kontrol et"""
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    
    if plan:
        logger.warning("⚠ Bekleyen migrasyonlar var:")
        for migration, _ in plan:
            logger.warning(f"  - {migration.app_label}.{migration.name}")
        return False
    else:
        logger.info("✓ Tüm migrasyonlar güncel")
        return True

def check_indexes():
    """Veritabanı indekslerini kontrol et"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT schemaname, tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        indexes = cursor.fetchall()
        
        logger.info(f"\nToplam {len(indexes)} indeks bulundu:")
        for idx in indexes:
            logger.info(f"✓ {idx[1]}: {idx[2]}")
        return True

def check_connections():
    """Aktif bağlantıları kontrol et"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT count(*) FROM pg_stat_activity 
            WHERE datname = current_database();
        """)
        active_connections = cursor.fetchone()[0]
        
        cursor.execute("SHOW max_connections;")
        max_connections = cursor.fetchone()[0]
        
        usage_percent = (active_connections / int(max_connections)) * 100
        logger.info(f"\nBağlantı durumu:")
        logger.info(f"✓ Aktif bağlantı: {active_connections}")
        logger.info(f"✓ Maksimum bağlantı: {max_connections}")
        logger.info(f"✓ Kullanım oranı: {usage_percent:.1f}%")
        
        if usage_percent > 80:
            logger.warning("⚠ Bağlantı havuzu yüksek kullanımda")
            return False
    return True

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
    django.setup()
    
    logger.info("\nVeritabanı Kontrol Aracı")
    logger.info("=" * 50)
    
    success = True
    
    # Kontrolleri çalıştır
    checks = [
        check_database_connection,
        check_migrations,
        check_indexes,
        check_connections
    ]
    
    for check in checks:
        if not check():
            success = False
            
    if success:
        logger.info("\n✓ Tüm veritabanı kontrolleri başarılı")
        sys.exit(0)
    else:
        logger.error("\n✗ Bazı kontroller başarısız oldu")
        sys.exit(1)

if __name__ == "__main__":
    main()
