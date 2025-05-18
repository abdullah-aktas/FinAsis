# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import json
import logging
from datetime import datetime
from .models import IntegrationConfig, SyncLog, WebhookLog, IntegrationTask
from .ecommerce.hepsiburada.hepsiburada import HepsiburadaIntegration
from .ecommerce.shopify.shopify import ShopifyIntegration
from .payment.iyzico.iyzico import IyzicoIntegration
from .erp.luca.luca import LucaIntegration
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)

def get_integration_instance(integration_type):
    """Entegrasyon tipine göre instance oluşturur"""
    config = IntegrationConfig.objects.filter(type=integration_type).first()
    if not config:
        return None
        
    integration_classes = {
        'hepsiburada': HepsiburadaIntegration,
        'shopify': ShopifyIntegration,
        'iyzico': IyzicoIntegration,
        'luca': LucaIntegration
    }
    
    integration_class = integration_classes.get(integration_type)
    if not integration_class:
        return None
        
    return integration_class(config.config)

def dashboard(request):
    """Entegrasyon yönetim paneli"""
    if not request.user.has_perm('integrations.view_integration'):
        raise PermissionDenied
        
    integrations = IntegrationConfig.objects.all()
    context = {
        'integrations': integrations,
        'hepsiburada': IntegrationConfig.objects.filter(type='hepsiburada').first(),
        'shopify': IntegrationConfig.objects.filter(type='shopify').first(),
        'iyzico': IntegrationConfig.objects.filter(type='iyzico').first(),
        'luca': IntegrationConfig.objects.filter(type='luca').first()
    }
    return render(request, 'integrations/dashboard.html', context)

@require_http_methods(["POST"])
@csrf_exempt
def save_config(request, integration_type):
    """Entegrasyon konfigürasyonunu kaydeder"""
    if not request.user.has_perm('integrations.change_integration'):
        raise PermissionDenied
        
    try:
        data = json.loads(request.body)
        config, created = IntegrationConfig.objects.update_or_create(
            type=integration_type,
            defaults={
                'is_active': data.get('is_active', True),
                'config': data
            }
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Config save error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["POST"])
@csrf_exempt
def run_sync(request, integration_id):
    """Senkronizasyon işlemini başlatır"""
    if not request.user.has_perm('integrations.run_sync'):
        raise PermissionDenied
        
    try:
        config = IntegrationConfig.objects.get(id=integration_id)
        integration = get_integration_instance(config.type)
        if not integration:
            return JsonResponse({'status': 'error', 'message': 'Integration not found'}, status=404)
            
        # Senkronizasyon işlemini başlat
        result = integration.execute_sync()
        
        # Log kaydet
        SyncLog.objects.create(
            integration=config,
            status='success' if result['status'] == 'success' else 'error',
            error_message=result.get('message')
        )
        
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["GET"])
def get_logs(request, integration_id):
    """Entegrasyon loglarını getirir"""
    if not request.user.has_perm('integrations.view_synclog'):
        raise PermissionDenied
        
    try:
        logs = SyncLog.objects.filter(integration_id=integration_id).order_by('-created_at')[:100]
        return JsonResponse({
            'logs': [{
                'timestamp': log.created_at.isoformat(),
                'level': 'error' if log.status == 'error' else 'info',
                'message': log.error_message or 'Senkronizasyon başarılı'
            } for log in logs]
        })
    except Exception as e:
        logger.error(f"Log retrieval error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["POST"])
@csrf_exempt
def handle_webhook(request, integration_type):
    """Webhook isteklerini işler"""
    try:
        integration = get_integration_instance(integration_type)
        if not integration:
            return JsonResponse({'status': 'error', 'message': 'Integration not found'}, status=404)
            
        data = json.loads(request.body)
        result = integration.handle_webhook(data)
        
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# WebhookLog Views
class WebhookLogListView(ListView):
    model = WebhookLog
    template_name = 'integrations/webhooklog_list.html'
    context_object_name = 'logs'

class WebhookLogDetailView(DetailView):
    model = WebhookLog
    template_name = 'integrations/webhooklog_detail.html'
    context_object_name = 'log'

class WebhookLogCreateView(CreateView):
    model = WebhookLog
    template_name = 'integrations/webhooklog_form.html'
    fields = ['webhook', 'status', 'request_data', 'response_data', 'error_message']
    success_url = reverse_lazy('integrations:webhooklog_list')

class WebhookLogUpdateView(UpdateView):
    model = WebhookLog
    template_name = 'integrations/webhooklog_form.html'
    fields = ['webhook', 'status', 'request_data', 'response_data', 'error_message']
    success_url = reverse_lazy('integrations:webhooklog_list')

class WebhookLogDeleteView(DeleteView):
    model = WebhookLog
    template_name = 'integrations/webhooklog_confirm_delete.html'
    success_url = reverse_lazy('integrations:webhooklog_list')

# IntegrationTask Views
class IntegrationTaskListView(ListView):
    model = IntegrationTask
    template_name = 'integrations/integrationtask_list.html'
    context_object_name = 'tasks'

class IntegrationTaskDetailView(DetailView):
    model = IntegrationTask
    template_name = 'integrations/integrationtask_detail.html'
    context_object_name = 'task'

class IntegrationTaskCreateView(CreateView):
    model = IntegrationTask
    template_name = 'integrations/integrationtask_form.html'
    fields = ['integration', 'task_type', 'status', 'parameters', 'result']
    success_url = reverse_lazy('integrations:integrationtask_list')

class IntegrationTaskUpdateView(UpdateView):
    model = IntegrationTask
    template_name = 'integrations/integrationtask_form.html'
    fields = ['integration', 'task_type', 'status', 'parameters', 'result']
    success_url = reverse_lazy('integrations:integrationtask_list')

class IntegrationTaskDeleteView(DeleteView):
    model = IntegrationTask
    template_name = 'integrations/integrationtask_confirm_delete.html'
    success_url = reverse_lazy('integrations:integrationtask_list') 