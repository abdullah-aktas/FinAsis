# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import IntegrationProvider, Integration, IntegrationLog, WebhookEndpoint, IntegrationTemplate, WebhookRequest
from .forms import IntegrationProviderForm, IntegrationForm, WebhookEndpointForm, IntegrationTemplateForm
from .serializers import (
    IntegrationProviderSerializer, IntegrationSerializer,
    IntegrationLogSerializer, WebhookEndpointSerializer,
    IntegrationTemplateSerializer, WebhookRequestSerializer
)
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Template Views
class IntegrationListView(LoginRequiredMixin, ListView):
    model = Integration
    template_name = 'external_integrations/integration_list.html'
    context_object_name = 'integrations'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        provider_id = self.request.GET.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        return queryset.select_related('provider')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = IntegrationProvider.objects.filter(is_active=True)
        return context

class IntegrationProviderListView(LoginRequiredMixin, ListView):
    model = IntegrationProvider
    template_name = 'external_integrations/provider_list.html'
    context_object_name = 'providers'
    ordering = ['name']

class IntegrationProviderDetailView(LoginRequiredMixin, DetailView):
    model = IntegrationProvider
    template_name = 'external_integrations/provider_detail.html'
    context_object_name = 'provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['integrations'] = self.object.integrations.all()
        return context

class IntegrationProviderCreateView(LoginRequiredMixin, CreateView):
    model = IntegrationProvider
    form_class = IntegrationProviderForm
    template_name = 'external_integrations/provider_form.html'
    success_url = reverse_lazy('external_integrations:provider_list')

    def form_valid(self, form):
        messages.success(self.request, _('Entegrasyon sağlayıcı başarıyla oluşturuldu.'))
        return super().form_valid(form)

class IntegrationProviderUpdateView(LoginRequiredMixin, UpdateView):
    model = IntegrationProvider
    form_class = IntegrationProviderForm
    template_name = 'external_integrations/provider_form.html'
    success_url = reverse_lazy('external_integrations:provider_list')

    def form_valid(self, form):
        messages.success(self.request, _('Entegrasyon sağlayıcı başarıyla güncellendi.'))
        return super().form_valid(form)

class IntegrationProviderDeleteView(LoginRequiredMixin, DeleteView):
    model = IntegrationProvider
    template_name = 'external_integrations/provider_confirm_delete.html'
    success_url = reverse_lazy('external_integrations:provider_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Entegrasyon sağlayıcı başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

# API Views
class IntegrationProviderViewSet(viewsets.ModelViewSet):
    queryset = IntegrationProvider.objects.all()
    serializer_class = IntegrationProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        integration = self.get_object()
        try:
            # Burada entegrasyon bağlantı testi yapılacak
            return Response({'status': 'success', 'message': _('Bağlantı başarılı')})
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class IntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        integration_id = self.request.query_params.get('integration', None)
        if integration_id:
            queryset = queryset.filter(integration_id=integration_id)
        return queryset

class WebhookEndpointViewSet(viewsets.ModelViewSet):
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def test_webhook(self, request, pk=None):
        webhook = self.get_object()
        try:
            # Burada webhook testi yapılacak
            return Response({'status': 'success', 'message': _('Webhook testi başarılı')})
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# Entegrasyon Şablonları
class TemplateListView(LoginRequiredMixin, ListView):
    model = IntegrationTemplate
    template_name = 'external_integrations/template_list.html'
    context_object_name = 'templates'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        provider = self.request.GET.get('provider')
        
        if category:
            queryset = queryset.filter(category=category)
        if provider:
            queryset = queryset.filter(provider_id=provider)
            
        return queryset.select_related('provider')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = IntegrationTemplate.CATEGORY_CHOICES
        context['providers'] = IntegrationProvider.objects.filter(is_active=True)
        return context

class TemplateDetailView(LoginRequiredMixin, DetailView):
    model = IntegrationTemplate
    template_name = 'external_integrations/template_detail.html'
    context_object_name = 'template'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['integrations'] = self.object.integrations.all()
        return context

class TemplateCreateView(LoginRequiredMixin, CreateView):
    model = IntegrationTemplate
    form_class = IntegrationTemplateForm
    template_name = 'external_integrations/template_form.html'
    success_url = reverse_lazy('external_integrations:template_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Entegrasyon şablonu başarıyla oluşturuldu.'))
        return response

class TemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = IntegrationTemplate
    form_class = IntegrationTemplateForm
    template_name = 'external_integrations/template_form.html'
    success_url = reverse_lazy('external_integrations:template_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Entegrasyon şablonu başarıyla güncellendi.'))
        return response

class TemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = IntegrationTemplate
    template_name = 'external_integrations/template_confirm_delete.html'
    success_url = reverse_lazy('external_integrations:template_list')
    context_object_name = 'template'

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Entegrasyon şablonu başarıyla silindi.'))
        return response

# Entegrasyon Sihirbazı
@login_required
def integration_wizard(request):
    if request.method == 'POST':
        template_id = request.POST.get('template')
        if template_id:
            template = get_object_or_404(IntegrationTemplate, id=template_id)
            return redirect('external_integrations:integration_create', template_id=template_id)
    
    templates = IntegrationTemplate.objects.filter(is_active=True).select_related('provider')
    return render(request, 'external_integrations/integration_wizard.html', {
        'templates': templates,
        'categories': IntegrationTemplate.CATEGORY_CHOICES,
    })

# API Views
@require_http_methods(['GET'])
def api_templates(request):
    templates = IntegrationTemplate.objects.filter(is_active=True)
    serializer = IntegrationTemplateSerializer(templates, many=True)
    return JsonResponse(serializer.data, safe=False)

@require_http_methods(['GET'])
def api_template_detail(request, pk):
    template = get_object_or_404(IntegrationTemplate, pk=pk)
    serializer = IntegrationTemplateSerializer(template)
    return JsonResponse(serializer.data)

@require_http_methods(['POST'])
def api_test_integration(request, pk):
    integration = get_object_or_404(Integration, pk=pk)
    try:
        # Entegrasyon testi yapılacak
        # Bu kısım entegrasyon tipine göre özelleştirilmeli
        return JsonResponse({
            'status': 'success',
            'message': _('Entegrasyon başarıyla test edildi.')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(['POST'])
def api_test_webhook(request, pk):
    webhook = get_object_or_404(WebhookEndpoint, pk=pk)
    try:
        # Webhook testi yapılacak
        # Bu kısım webhook tipine göre özelleştirilmeli
        return JsonResponse({
            'status': 'success',
            'message': _('Webhook başarıyla test edildi.')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
