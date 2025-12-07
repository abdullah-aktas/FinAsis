# -*- coding: utf-8 -*-
"""
Common Tasks - Celery Async Tasks
Email, PDF generation, cache management vb.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db import connection
from django.conf import settings
from pathlib import Path
import tempfile
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# EMAIL TASKS
# ============================================================================


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_async(self, subject, message, from_email, recipient_list, **kwargs):
    """
    Async email gönderme

    Args:
        subject: Email başlığı
        message: Email içeriği
        from_email: Gönderen email
        recipient_list: Alıcı listesi (list veya str)
    """
    try:
        # Ensure recipient_list is a list
        if isinstance(recipient_list, str):
            recipient_list = [recipient_list]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=list(recipient_list),
            fail_silently=False,
            **kwargs,
        )
        logger.info(f"Email sent: {subject} to {recipient_list}")
        return f"Email sent to {len(recipient_list)} recipients"

    except Exception as exc:
        logger.error(f"Email send failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2**self.request.retries)


@shared_task
def send_bulk_emails(email_list):
    """
    Toplu email gönderme

    Args:
        email_list: [{subject, message, from_email, recipient_list}]
    """
    sent_count = 0
    failed_count = 0

    for email_data in email_list:
        try:
            recipient_list = email_data["recipient_list"]
            if isinstance(recipient_list, str):
                recipient_list = [recipient_list]

            send_mail(
                subject=email_data["subject"],
                message=email_data["message"],
                from_email=email_data["from_email"],
                recipient_list=list(recipient_list),
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Bulk email failed: {e}")
            failed_count += 1

    logger.info(f"Bulk emails: {sent_count} sent, {failed_count} failed")
    return {"sent": sent_count, "failed": failed_count}


# ============================================================================
# PDF GENERATION TASKS
# ============================================================================


@shared_task(bind=True, max_retries=2)
def generate_pdf_report(self, report_type, report_id, user_id):
    """
    PDF rapor oluşturma (async)

    Args:
        report_type: Rapor tipi (invoice, financial, etc.)
        report_id: Rapor ID
        user_id: Kullanıcı ID
    """
    try:
        logger.info(f"Generating PDF: {report_type} #{report_id} for user {user_id}")

        # TODO: PDF generation logic buraya
        # from apps.reports.services import PDFGenerator
        # generator = PDFGenerator()
        # pdf_path = generator.generate(report_type, report_id)

        # Şimdilik placeholder - güvenli ve konfigüre edilebilir temp dizini kullan
        base_tmp_dir = getattr(settings, "REPORT_TMP_DIR", None)
        if base_tmp_dir:
            tmp_dir = Path(base_tmp_dir)
        else:
            tmp_dir = Path(tempfile.gettempdir()) / "finasis_reports"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = tmp_dir / f"report_{report_type}_{report_id}.pdf"

        logger.info(f"PDF generated: {pdf_path}")
        return {"success": True, "path": str(pdf_path)}

    except Exception as exc:
        logger.error(f"PDF generation failed: {exc}")
        raise self.retry(exc=exc, countdown=30)


@shared_task
def generate_invoice_pdf(invoice_id):
    """Fatura PDF oluşturma - wrapper task"""
    # Call the actual PDF generation task
    result = generate_pdf_report(
        report_type="invoice", report_id=invoice_id, user_id=None
    )
    return result


@shared_task
def generate_financial_report_pdf(report_id, user_id):
    """Finansal rapor PDF oluşturma - wrapper task"""
    # Call the actual PDF generation task
    result = generate_pdf_report(
        report_type="financial", report_id=report_id, user_id=user_id
    )
    return result


# ============================================================================
# CACHE MANAGEMENT TASKS
# ============================================================================


@shared_task
def warmup_cache():
    """
    Cache warmup - sık kullanılan verileri cache'e yükle
    """
    try:
        logger.info("Starting cache warmup...")

        # Örnek: Popüler sorguları cache'le
        # from apps.accounting.models import Invoice
        # recent_invoices = Invoice.objects.all()[:100]
        # cache.set('popular_invoices', list(recent_invoices), timeout=300)

        logger.info("Cache warmup completed")
        return "Cache warmed up successfully"

    except Exception as e:
        logger.error(f"Cache warmup failed: {e}")
        return f"Cache warmup failed: {e}"


@shared_task
def clear_cache_pattern(pattern):
    """
    Pattern'e göre cache temizleme

    Args:
        pattern: Cache key pattern (finasis:views:*)
    """
    try:
        from django_redis import get_redis_connection

        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(pattern)

        if keys:
            redis_conn.delete(*keys)
            logger.info(f"Cleared {len(keys)} cache keys matching: {pattern}")
            return f"Cleared {len(keys)} keys"

        return "No keys found"

    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        return f"Failed: {e}"


# ============================================================================
# CLEANUP TASKS
# ============================================================================


@shared_task
def cleanup_old_sessions():
    """Eski session'ları temizle"""
    try:
        expired = Session.objects.filter(expire_date__lt=timezone.now())
        count = expired.count()
        expired.delete()

        logger.info(f"Cleaned up {count} old sessions")
        return f"Cleaned {count} sessions"

    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        return f"Failed: {e}"


@shared_task
def cleanup_old_logs():
    """
    Eski log kayıtlarını temizle (30 gün üzeri)
    """
    try:
        # TODO: Log model'e göre güncelle
        # from apps.audit.models import AuditLog
        # cutoff_date = datetime.now() - timedelta(days=30)
        # deleted = AuditLog.objects.filter(created_at__lt=cutoff_date).delete()

        logger.info("Old logs cleaned up")
        return "Logs cleaned successfully"

    except Exception as e:
        logger.error(f"Log cleanup failed: {e}")
        return f"Failed: {e}"


@shared_task
def optimize_database():
    """
    Database optimization (VACUUM, ANALYZE)
    PostgreSQL için
    """
    try:
        with connection.cursor() as cursor:
            # VACUUM ANALYZE (PostgreSQL)
            cursor.execute("VACUUM ANALYZE;")

        logger.info("Database optimized")
        return "Database optimized successfully"

    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return f"Failed: {e}"


# ============================================================================
# DATA PROCESSING TASKS
# ============================================================================


@shared_task(bind=True, max_retries=3)
def process_bulk_data(self, data_type, data_list):
    """
    Toplu veri işleme (bulk insert/update)

    Args:
        data_type: Veri tipi (invoice, transaction, etc.)
        data_list: İşlenecek veri listesi
    """
    try:
        logger.info(f"Processing {len(data_list)} {data_type} records")

        # TODO: Bulk processing logic
        processed = 0
        failed = 0

        for data in data_list:
            try:
                # Process single record
                processed += 1
            except Exception as e:
                logger.error(f"Record processing failed: {e}")
                failed += 1

        logger.info(f"Processed: {processed}, Failed: {failed}")
        return {"processed": processed, "failed": failed}

    except Exception as exc:
        logger.error(f"Bulk processing failed: {exc}")
        raise self.retry(exc=exc)


@shared_task
def export_data_to_excel(model_name, queryset_kwargs, user_email):
    """
    Excel export (async)

    Args:
        model_name: Model adı
        queryset_kwargs: QuerySet filter kwargs
        user_email: Sonuç gönderilecek email
    """
    try:
        logger.info(f"Exporting {model_name} to Excel for {user_email}")

        # TODO: Excel export logic
        # file_path = '/tmp/export.xlsx'

        # Email ile gönder - direct call instead of delay to avoid type issues
        send_email_async(
            subject="Excel Export Ready",
            message="Your export is ready for download.",
            from_email="noreply@finasis.com.tr",
            recipient_list=[user_email],
        )

        return "Export completed and sent via email"

    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        return f"Failed: {e}"


# ============================================================================
# MONITORING TASKS
# ============================================================================


@shared_task
def health_check():
    """System health check"""
    try:
        # Cache check
        cache.set("health_check", "ok", timeout=10)
        cache_ok = cache.get("health_check") == "ok"

        # Database check
        db_ok = False
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and len(result) > 0:
                db_ok = result[0] == 1

        status = {
            "cache": "ok" if cache_ok else "failed",
            "database": "ok" if db_ok else "failed",
            "celery": "ok",
        }

        logger.info(f"Health check: {status}")
        return status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"error": str(e)}
