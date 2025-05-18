# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import EDespatchAdviceLog, EDocumentBase
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Sum, Count
from .models import (
    EDocument, EDocumentLog, EDocumentItem,
    EDespatchAdvice, EDespatchAdviceItem
)
from .serializers import (
    EDocumentSerializer, EDocumentLogSerializer, EDocumentItemSerializer,
    EDespatchAdviceSerializer, EDespatchAdviceLogSerializer, EDespatchAdviceItemSerializer,
    EDocumentBaseSerializer
)
from .services import GIBInvoiceService, GIBDespatchService
from .permissions import (
    CanCreateDocument, CanUpdateDocument, CanDeleteDocument,
    CanViewDocument, CanSendDocument, CanCancelDocument
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Document, Category
from .forms import DocumentForm, CategoryForm

class EDespatchAdviceLogListView(ListView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_list.html'
    context_object_name = 'logs'

class EDespatchAdviceLogDetailView(DetailView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_detail.html'
    context_object_name = 'log'

class EDespatchAdviceLogCreateView(CreateView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_form.html'
    fields = ['despatch_advice', 'status', 'message', 'error_details']
    success_url = reverse_lazy('edocument:edespatchadvicelog_list')

class EDespatchAdviceLogUpdateView(UpdateView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_form.html'
    fields = ['despatch_advice', 'status', 'message', 'error_details']
    success_url = reverse_lazy('edocument:edespatchadvicelog_list')

class EDespatchAdviceLogDeleteView(DeleteView):
    model = EDespatchAdviceLog
    template_name = 'edocument/edespatchadvicelog_confirm_delete.html'
    success_url = reverse_lazy('edocument:edespatchadvicelog_list')

class EDocumentViewSet(viewsets.ModelViewSet):
    """E-Fatura işlemleri için viewset"""
    queryset = EDocument.objects.all()
    serializer_class = EDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type', 'sender', 'receiver_vkn']
    search_fields = ['invoice_number', 'receiver_name']
    ordering_fields = ['created_at', 'invoice_date', 'due_date', 'total_amount']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), CanCreateDocument()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), CanUpdateDocument()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), CanDeleteDocument()]
        elif self.action in ['send', 'cancel']:
            return [IsAuthenticated(), CanSendDocument()]
        return [IsAuthenticated(), CanViewDocument()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(sender=self.request.user) | 
                Q(receiver_vkn=self.request.user.company.vkn)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        document = self.get_object()
        if document.status != 'DRAFT':
            return Response(
                {'error': 'Sadece taslak durumundaki belgeler gönderilebilir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GIBInvoiceService()
        try:
            service.send_to_gib(document)
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        document = self.get_object()
        if document.status != 'SENT':
            return Response(
                {'error': 'Sadece gönderilmiş belgeler iptal edilebilir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason')
        if not reason:
            return Response(
                {'error': 'İptal sebebi belirtilmelidir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GIBInvoiceService()
        try:
            service.cancel_invoice(document, reason)
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        cache_key = f'document_stats_{request.user.id}'
        stats = cache.get(cache_key)
        
        if not stats:
            queryset = self.get_queryset()
            stats = {
                'total_count': queryset.count(),
                'status_counts': dict(queryset.values_list('status').annotate(count=Count('id'))),
                'type_counts': dict(queryset.values_list('document_type').annotate(count=Count('id'))),
                'total_amount': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
                'total_tax': queryset.aggregate(total=Sum('total_tax'))['total'] or 0,
            }
            cache.set(cache_key, stats, 300)  # 5 dakika cache
        
        return Response(stats)

class EDocumentItemViewSet(viewsets.ModelViewSet):
    """E-Fatura kalemleri için viewset"""
    queryset = EDocumentItem.objects.all()
    serializer_class = EDocumentItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['document', 'product_code']
    search_fields = ['product_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                document__sender=self.request.user
            )
        return queryset

class EDocumentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """E-Fatura logları için viewset"""
    queryset = EDocumentLog.objects.all()
    serializer_class = EDocumentLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['document', 'action', 'status', 'level']
    search_fields = ['message']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                document__sender=self.request.user
            )
        return queryset

class EDespatchAdviceViewSet(viewsets.ModelViewSet):
    """E-İrsaliye işlemleri için viewset"""
    queryset = EDespatchAdvice.objects.all()
    serializer_class = EDespatchAdviceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'transport_type', 'sender', 'receiver_vkn']
    search_fields = ['despatch_number', 'receiver_name', 'vehicle_plate']
    ordering_fields = ['created_at', 'despatch_date', 'delivery_date']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), CanCreateDocument()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), CanUpdateDocument()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), CanDeleteDocument()]
        elif self.action in ['send', 'accept', 'reject', 'partially_accept']:
            return [IsAuthenticated(), CanSendDocument()]
        return [IsAuthenticated(), CanViewDocument()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(sender=self.request.user) | 
                Q(receiver_vkn=self.request.user.company.vkn)
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        despatch = self.get_object()
        if despatch.status != 'DRAFT':
            return Response(
                {'error': 'Sadece taslak durumundaki irsaliyeler gönderilebilir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GIBDespatchService()
        try:
            service.send_to_gib(despatch)
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        despatch = self.get_object()
        if despatch.status != 'SENT':
            return Response(
                {'error': 'Sadece gönderilmiş irsaliyeler kabul edilebilir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GIBDespatchService()
        try:
            service.accept_despatch(despatch)
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        despatch = self.get_object()
        if despatch.status != 'SENT':
            return Response(
                {'error': 'Sadece gönderilmiş irsaliyeler reddedilebilir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason')
        if not reason:
            return Response(
                {'error': 'Red sebebi belirtilmelidir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GIBDespatchService()
        try:
            service.reject_despatch(despatch, reason)
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def partially_accept(self, request, pk=None):
        despatch = self.get_object()
        if despatch.status != 'SENT':
            return Response(
                {'error': 'Sadece gönderilmiş irsaliyeler kısmen kabul edilebilir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        accepted_items = request.data.get('accepted_items')
        if not accepted_items:
            return Response(
                {'error': 'Kabul edilen kalemler belirtilmelidir.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GIBDespatchService()
        try:
            service.partially_accept_despatch(despatch, accepted_items)
            return Response({'status': 'success'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        cache_key = f'despatch_stats_{request.user.id}'
        stats = cache.get(cache_key)
        
        if not stats:
            queryset = self.get_queryset()
            stats = {
                'total_count': queryset.count(),
                'status_counts': dict(queryset.values_list('status').annotate(count=Count('id'))),
                'transport_type_counts': dict(queryset.values_list('transport_type').annotate(count=Count('id'))),
                'total_items': queryset.aggregate(total=Sum('items__quantity'))['total'] or 0,
            }
            cache.set(cache_key, stats, 300)  # 5 dakika cache
        
        return Response(stats)

class EDespatchAdviceItemViewSet(viewsets.ModelViewSet):
    """E-İrsaliye kalemleri için viewset"""
    queryset = EDespatchAdviceItem.objects.all()
    serializer_class = EDespatchAdviceItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['despatch', 'product_code']
    search_fields = ['product_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                despatch__sender=self.request.user
            )
        return queryset

class EDespatchAdviceLogViewSet(viewsets.ReadOnlyModelViewSet):
    """E-İrsaliye logları için viewset"""
    queryset = EDespatchAdviceLog.objects.all()
    serializer_class = EDespatchAdviceLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['despatch', 'action', 'status', 'level']
    search_fields = ['message']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                despatch__sender=self.request.user
            )
        return queryset

class EDocumentBaseViewSet(viewsets.ModelViewSet):
    queryset = EDocumentBase.objects.all()
    serializer_class = EDocumentBaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

@login_required
def dashboard(request):
    """E-Doküman dashboard görünümü"""
    recent_docs = Document.objects.filter(user=request.user).order_by('-created_at')[:5]
    shared_docs = Document.objects.filter(shared_with=request.user).order_by('-created_at')[:5]
    
    context = {
        'recent_docs': recent_docs,
        'shared_docs': shared_docs,
    }
    return render(request, 'edocument/dashboard.html', context)

@login_required
def documents(request):
    """Doküman listesi görünümü"""
    documents = Document.objects.filter(user=request.user)
    
    # Arama filtresi
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Kategori filtresi
    category_id = request.GET.get('category')
    if category_id:
        documents = documents.filter(category_id=category_id)
    
    # Sayfalama
    paginator = Paginator(documents, 10)
    page = request.GET.get('page')
    documents = paginator.get_page(page)
    
    context = {
        'documents': documents,
        'categories': Category.objects.all(),
    }
    return render(request, 'edocument/documents.html', context)

@login_required
def document_detail(request, pk):
    """Doküman detay görünümü"""
    document = get_object_or_404(Document, pk=pk)
    if not document.can_view(request.user):
        messages.error(request, 'Bu dokümana erişim izniniz yok.')
        return redirect('edocument:documents')
    
    context = {
        'document': document,
    }
    return render(request, 'edocument/document_detail.html', context)

@login_required
def document_create(request):
    """Yeni doküman oluşturma görünümü"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Doküman başarıyla oluşturuldu.')
            return redirect('edocument:document_detail', pk=document.pk)
    else:
        form = DocumentForm()
    
    context = {
        'form': form,
    }
    return render(request, 'edocument/document_form.html', context)

@login_required
def categories(request):
    """Kategori listesi görünümü"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'edocument/categories.html', context)

@login_required
def shared_documents(request):
    """Paylaşılan dokümanlar görünümü"""
    documents = Document.objects.filter(shared_with=request.user)
    context = {
        'documents': documents,
    }
    return render(request, 'edocument/shared.html', context)

@login_required
def archive(request):
    """Arşiv görünümü"""
    documents = Document.objects.filter(user=request.user, is_archived=True)
    context = {
        'documents': documents,
    }
    return render(request, 'edocument/archive.html', context)

@login_required
def settings(request):
    """Ayarlar görünümü"""
    if request.method == 'POST':
        # Ayarları kaydet
        messages.success(request, 'Ayarlar başarıyla güncellendi.')
        return redirect('edocument:settings')
    
    return render(request, 'edocument/settings.html') 