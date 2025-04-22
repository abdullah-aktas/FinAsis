from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, permissions
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Integration
from .serializers import ServiceSerializer, IntegrationSerializer

# Create your views here.

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

@login_required
def dashboard(request):
    services = Service.objects.all()
    integrations = Integration.objects.all()
    return render(request, 'ext_services/dashboard.html', {
        'services': services,
        'integrations': integrations
    })

@login_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'ext_services/service_list.html', {'services': services})

@login_required
def service_create(request):
    if request.method == 'POST':
        serializer = ServiceSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Servis başarıyla oluşturuldu.')
            return redirect('ext_services:service_list')
        else:
            messages.error(request, 'Servis oluşturulurken hata oluştu.')
    return render(request, 'ext_services/service_form.html')

@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'ext_services/service_detail.html', {'service': service})

@login_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        serializer = ServiceSerializer(service, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Servis başarıyla güncellendi.')
            return redirect('ext_services:service_detail', pk=pk)
        else:
            messages.error(request, 'Servis güncellenirken hata oluştu.')
    return render(request, 'ext_services/service_form.html', {'service': service})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Servis başarıyla silindi.')
        return redirect('ext_services:service_list')
    return render(request, 'ext_services/service_confirm_delete.html', {'service': service})
