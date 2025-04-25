from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from .models import CheckType, CheckResult, CheckSchedule
import logging
import json
import time

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def run_check(self, check_type_id):
    """
    Belirli bir kontrol tipini çalıştırır.
    """
    try:
        check_type = CheckType.objects.get(id=check_type_id)
        logger.info(f"Kontrol başlatılıyor: {check_type.name}")

        # Kontrol sonucu oluştur
        result = CheckResult.objects.create(
            check_type=check_type,
            started_at=timezone.now(),
            status='running'
        )

        try:
            # Kontrol kurallarını al
            rules = check_type.checkrule_set.filter(is_active=True)
            total_score = 0
            total_weight = 0
            details = []

            # Her kuralı değerlendir
            for rule in rules:
                rule_start = time.time()
                try:
                    # Koşulu değerlendir
                    passed = eval(rule.condition)
                    score = 1.0 if passed else 0.0
                    
                    # Detayları kaydet
                    details.append({
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'passed': passed,
                        'score': score,
                        'weight': rule.weight,
                        'duration': time.time() - rule_start
                    })

                    # Toplam puanı hesapla
                    total_score += score * rule.weight
                    total_weight += rule.weight

                except Exception as e:
                    logger.error(f"Kural değerlendirme hatası: {str(e)}")
                    details.append({
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'error': str(e),
                        'duration': time.time() - rule_start
                    })

            # Sonucu güncelle
            final_score = total_score / total_weight if total_weight > 0 else 0
            status = 'passed' if final_score >= 0.8 else 'failed'

            result.status = status
            result.score = final_score
            result.details = json.dumps(details)
            result.completed_at = timezone.now()
            result.duration = result.completed_at - result.started_at
            result.save()

            # Cache'i temizle
            cache.delete('check_results_statistics')

            logger.info(f"Kontrol tamamlandı: {check_type.name} - {status}")
            return result.id

        except Exception as e:
            logger.error(f"Kontrol çalıştırma hatası: {str(e)}")
            result.status = 'error'
            result.details = json.dumps({'error': str(e)})
            result.completed_at = timezone.now()
            result.duration = result.completed_at - result.started_at
            result.save()
            raise

    except CheckType.DoesNotExist:
        logger.error(f"Kontrol tipi bulunamadı: {check_type_id}")
        raise
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        raise self.retry(exc=e, countdown=60)

@shared_task
def run_scheduled_checks():
    """
    Zamanı gelmiş kontrolleri çalıştırır.
    """
    now = timezone.now()
    due_schedules = CheckSchedule.objects.filter(
        is_active=True,
        next_run__lte=now
    )

    for schedule in due_schedules:
        try:
            # Kontrolü çalıştır
            run_check.delay(schedule.check_type.id)
            
            # Sonraki çalıştırma zamanını güncelle
            schedule.last_run = now
            # TODO: Sonraki çalıştırma zamanını hesapla
            schedule.next_run = now + timezone.timedelta(hours=1)
            schedule.save()

        except Exception as e:
            logger.error(f"Zamanlanmış kontrol çalıştırma hatası: {str(e)}")

@shared_task
def cleanup_old_results(days=30):
    """
    Eski kontrol sonuçlarını temizler.
    """
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        old_results = CheckResult.objects.filter(created_at__lt=cutoff_date)
        count = old_results.count()
        old_results.delete()
        logger.info(f"{count} adet eski kontrol sonucu silindi")
    except Exception as e:
        logger.error(f"Eski sonuçları temizleme hatası: {str(e)}")
        raise 