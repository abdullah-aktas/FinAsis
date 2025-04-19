from celery import shared_task
from django.db import connection
from django.conf import settings
import logging

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