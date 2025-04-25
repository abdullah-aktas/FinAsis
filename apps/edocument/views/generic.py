from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import EDocument, EDocumentLog, EDespatchAdvice
from .services import GIBService, GIBDespatchService
from django.contrib import messages
from django.urls import reverse
from django.urls import reverse_lazy

@login_required
def document_list(request):
    """E-Belge listesi görünümü"""
    documents = EDocument.objects.filter(sender=request.user)
    
    # Filtreleme
    status = request.GET.get('status')
    if status:
        documents = documents.filter(status=status)
    
    # Sayfalama
    paginator = Paginator(documents, 10)
    page = request.GET.get('page')
    documents = paginator.get_page(page)
    
    return render(request, 'edocument/document_list.html', {
        'documents': documents,
        'status_choices': EDocument.STATUS_CHOICES
    })

@login_required
def document_detail(request, uuid):
    """E-Belge detay görünümü"""
    document = get_object_or_404(EDocument, uuid=uuid, sender=request.user)
    logs = document.logs.all()
    
    return render(request, 'edocument/document_detail.html', {
        'document': document,
        'logs': logs
    })

@login_required
@require_http_methods(['POST'])
def send_document(request, uuid):
    """E-Belge gönderim işlemi"""
    document = get_object_or_404(EDocument, uuid=uuid, sender=request.user)
    
    if document.status != 'DRAFT':
        return JsonResponse({
            'status': 'error',
            'message': 'Sadece taslak durumundaki belgeler gönderilebilir.'
        })
    
    try:
        gib_service = GIBService()
        gib_service.send_to_gib(document)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Belge başarıyla gönderildi.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def preview_xml(request, uuid):
    """XML önizleme"""
    document = get_object_or_404(EDocument, uuid=uuid, sender=request.user)
    
    return JsonResponse({
        'xml': document.xml_content,
        'signed_xml': document.signed_xml
    })

@login_required
def despatch_list(request):
    """E-İrsaliye listesi görünümü"""
    despatches = EDespatchAdvice.objects.filter(sender=request.user)
    
    # Filtreleme
    status = request.GET.get('status')
    if status:
        despatches = despatches.filter(status=status)
    
    # Sayfalama
    paginator = Paginator(despatches, 10)
    page = request.GET.get('page')
    despatches = paginator.get_page(page)
    
    return render(request, 'edocument/despatch_list.html', {
        'despatches': despatches,
        'status_choices': EDespatchAdvice.STATUS_CHOICES
    })

@login_required
def despatch_detail(request, uuid):
    """E-İrsaliye detay görünümü"""
    despatch = get_object_or_404(EDespatchAdvice, uuid=uuid, sender=request.user)
    logs = despatch.logs.all()
    
    return render(request, 'edocument/despatch_detail.html', {
        'despatch': despatch,
        'logs': logs
    })

@login_required
@require_http_methods(['POST'])
def send_despatch(request, uuid):
    """E-İrsaliye gönderim işlemi"""
    despatch = get_object_or_404(EDespatchAdvice, uuid=uuid, sender=request.user)
    
    if despatch.status != 'DRAFT':
        return JsonResponse({
            'status': 'error',
            'message': 'Sadece taslak durumundaki irsaliyeler gönderilebilir.'
        })
    
    try:
        gib_service = GIBDespatchService()
        gib_service.send_to_gib(despatch)
        
        return JsonResponse({
            'status': 'success',
            'message': 'İrsaliye başarıyla gönderildi.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def preview_despatch_xml(request, uuid):
    """İrsaliye XML önizleme"""
    despatch = get_object_or_404(EDespatchAdvice, uuid=uuid, sender=request.user)
    
    return JsonResponse({
        'xml': despatch.xml_content,
        'signed_xml': despatch.signed_xml
    })

@login_required
@require_http_methods(['POST'])
def accept_despatch(request, uuid):
    """E-İrsaliye kabul işlemi"""
    despatch = get_object_or_404(EDespatchAdvice, uuid=uuid)
    
    try:
        gib_service = GIBDespatchService()
        gib_service.accept_despatch(despatch)
        
        return JsonResponse({
            'status': 'success',
            'message': 'İrsaliye başarıyla kabul edildi.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
@require_http_methods(['POST'])
def reject_despatch(request, uuid):
    """E-İrsaliye red işlemi"""
    despatch = get_object_or_404(EDespatchAdvice, uuid=uuid)
    reason = request.POST.get('reason', '')
    
    try:
        gib_service = GIBDespatchService()
        gib_service.reject_despatch(despatch, reason)
        
        return JsonResponse({
            'status': 'success',
            'message': 'İrsaliye başarıyla reddedildi.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def xml_preview(request, document_id):
    try:
        document = EDocument.objects.get(id=document_id)
        xml_content = document.xml_content
        
        context = {
            'document': document,
            'xml_content': xml_content
        }
        return render(request, 'edocument/xml_preview.html', context)
    except EDocument.DoesNotExist:
        messages.error(request, 'Belge bulunamadı.')
        return reverse_lazy('document_list')
