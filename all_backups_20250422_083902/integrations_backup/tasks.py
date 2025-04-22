from celery import shared_task
from django.utils import timezone
from .models import IntegrationConfig, IntegrationTask, SyncLog
from .views import get_integration_instance
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_integration_sync(integration_id):
    """Entegrasyon senkronizasyonunu çalıştırır"""
    try:
        config = IntegrationConfig.objects.get(id=integration_id)
        if not config.is_active:
            logger.info(f"Integration {config.type} is not active")
            return
            
        # Görev oluştur
        task = IntegrationTask.objects.create(
            integration=config,
            task_type='sync',
            status='running'
        )
        
        # Entegrasyon instance'ı al
        integration = get_integration_instance(config.type)
        if not integration:
            task.mark_as_failed("Integration instance not found")
            return
            
        # Senkronizasyonu çalıştır
        result = integration.execute_sync()
        
        # Sonucu kaydet
        if result['status'] == 'success':
            task.mark_as_completed(result)
            SyncLog.objects.create(
                integration=config,
                status='success'
            )
        else:
            task.mark_as_failed(result.get('message', 'Unknown error'))
            SyncLog.objects.create(
                integration=config,
                status='error',
                error_message=result.get('message')
            )
            
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        if task:
            task.mark_as_failed(str(e))
            SyncLog.objects.create(
                integration=config,
                status='error',
                error_message=str(e)
            )

@shared_task
def process_webhook(integration_type, payload):
    """Webhook isteklerini işler"""
    try:
        config = IntegrationConfig.objects.filter(type=integration_type).first()
        if not config or not config.is_active:
            logger.info(f"Integration {integration_type} is not active")
            return
            
        # Görev oluştur
        task = IntegrationTask.objects.create(
            integration=config,
            task_type='webhook',
            status='running',
            payload=payload
        )
        
        # Entegrasyon instance'ı al
        integration = get_integration_instance(integration_type)
        if not integration:
            task.mark_as_failed("Integration instance not found")
            return
            
        # Webhook'u işle
        result = integration.handle_webhook(payload)
        
        # Sonucu kaydet
        if result['status'] == 'success':
            task.mark_as_completed(result)
        else:
            task.mark_as_failed(result.get('message', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        if task:
            task.mark_as_failed(str(e))

@shared_task
def cleanup_old_logs():
    """Eski logları temizler"""
    try:
        # 30 günden eski logları sil
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        SyncLog.objects.filter(created_at__lt=cutoff_date).delete()
        WebhookLog.objects.filter(created_at__lt=cutoff_date).delete()
        
        # Tamamlanmış görevleri temizle
        IntegrationTask.objects.filter(
            status__in=['completed', 'failed'],
            completed_at__lt=cutoff_date
        ).delete()
        
    except Exception as e:
        logger.error(f"Log cleanup error: {str(e)}")

@shared_task
def check_integration_health():
    """Entegrasyon sağlık kontrolü yapar"""
    try:
        integrations = IntegrationConfig.objects.filter(is_active=True)
        for config in integrations:
            integration = get_integration_instance(config.type)
            if not integration:
                continue
                
            # Kimlik doğrulama kontrolü
            is_authenticated = integration.authenticate()
            if not is_authenticated:
                SyncLog.objects.create(
                    integration=config,
                    status='error',
                    error_message='Authentication failed'
                )
                
    except Exception as e:
        logger.error(f"Health check error: {str(e)}") 