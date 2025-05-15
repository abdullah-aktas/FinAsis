# -*- coding: utf-8 -*-
from celery import shared_task
from django.db import connection
from django.conf import settings
import logging
from django.utils import timezone
from finance.accounting.models import FinancialReport

logger = logging.getLogger(__name__)

@shared_task
def vacuum_analyze_database():
    """
    PostgreSQL veritabanı için VACUUM ANALYZE işlemi gerçekleştirir.
    Bu işlem, veritabanı performansını optimize etmek için düzenli olarak çalıştırılmalıdır.
    """
    try:
        with connection.cursor() as cursor:
            # VACUUM ANALYZE işlemi
            cursor.execute("VACUUM ANALYZE;")
            logger.info("VACUUM ANALYZE işlemi başarıyla tamamlandı.")
    except Exception as e:
        logger.error(f"VACUUM ANALYZE işlemi sırasında hata oluştu: {str(e)}")
        raise

@shared_task
def reindex_database():
    """
    PostgreSQL veritabanı indekslerini yeniden oluşturur.
    Bu işlem, indeks performansını optimize etmek için düzenli olarak çalıştırılmalıdır.
    """
    try:
        with connection.cursor() as cursor:
            # Tüm indeksleri yeniden oluştur
            cursor.execute("""
                SELECT schemaname, tablename, indexname 
                FROM pg_indexes 
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                AND indexname NOT LIKE 'pg_%';
            """)
            
            for schema, table, index in cursor.fetchall():
                try:
                    cursor.execute(f'REINDEX INDEX CONCURRENTLY {schema}.{index};')
                    logger.info(f"İndeks yeniden oluşturuldu: {schema}.{index}")
                except Exception as e:
                    logger.error(f"İndeks yeniden oluşturma hatası ({schema}.{index}): {str(e)}")
                    continue
                    
            logger.info("Tüm indeksler başarıyla yeniden oluşturuldu.")
    except Exception as e:
        logger.error(f"İndeks yeniden oluşturma işlemi sırasında hata oluştu: {str(e)}")
        raise

@shared_task
def cleanup_old_data():
    """
    Eski verileri temizler ve arşivler.
    Bu işlem, veritabanı boyutunu yönetmek için düzenli olarak çalıştırılmalıdır.
    """
    try:
        with connection.cursor() as cursor:
            # 1 yıldan eski silinmiş kayıtları temizle
            cursor.execute("""
                DELETE FROM accounting_invoice 
                WHERE is_deleted = true 
                AND updated_at < NOW() - INTERVAL '1 year';
            """)
            
            # 6 aydan eski log kayıtlarını temizle
            cursor.execute("""
                DELETE FROM django_admin_log 
                WHERE action_time < NOW() - INTERVAL '6 months';
            """)
            
            logger.info("Eski veriler başarıyla temizlendi.")
    except Exception as e:
        logger.error(f"Veri temizleme işlemi sırasında hata oluştu: {str(e)}")
        raise

@shared_task
def optimize_tables():
    """
    PostgreSQL tablolarını optimize eder.
    Bu işlem, tablo performansını artırmak için düzenli olarak çalıştırılmalıdır.
    """
    try:
        with connection.cursor() as cursor:
            # Tablo istatistiklerini güncelle
            cursor.execute("""
                SELECT schemaname, tablename 
                FROM pg_tables 
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
            """)
            
            for schema, table in cursor.fetchall():
                try:
                    cursor.execute(f'ANALYZE {schema}.{table};')
                    logger.info(f"Tablo analiz edildi: {schema}.{table}")
                except Exception as e:
                    logger.error(f"Tablo analiz hatası ({schema}.{table}): {str(e)}")
                    continue
                    
            logger.info("Tüm tablolar başarıyla optimize edildi.")
    except Exception as e:
        logger.error(f"Tablo optimizasyon işlemi sırasında hata oluştu: {str(e)}")
        raise

@shared_task
def generate_weekly_trial_balance():
    """
    Haftalık mizan raporu oluşturur ve kaydeder.
    Gerçek ortamda PDF/Excel çıktısı da eklenebilir.
    """
    now = timezone.now()
    start_date = now - timezone.timedelta(days=7)
    end_date = now
    report = FinancialReport.objects.create(
        name=f"Otomatik Haftalık Mizan ({start_date:%d.%m.%Y}-{end_date:%d.%m.%Y})",
        type="trial_balance",
        company_id=1,  # Örnek, gerçek ortamda dinamik olmalı
        start_date=start_date,
        end_date=end_date,
        description="Otomatik oluşturulan haftalık mizan raporu."
    )
    # Burada PDF/Excel export fonksiyonu çağrılabilir
    return report.id 