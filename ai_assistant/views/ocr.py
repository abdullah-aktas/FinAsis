# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..services.ocr_service import OCRService
import os
import json
from django.conf import settings
import uuid
import numpy as np
import cv2

@csrf_exempt
@require_http_methods(["POST"])
def process_document(request):
    """
    Belge yükleme ve OCR işleme endpoint'i
    """
    try:
        # Dosya kontrolü
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Dosya yüklenmedi'
            }, status=400)

        uploaded_file = request.FILES['file']
        
        # Dosya uzantısı kontrolü
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': 'Geçersiz dosya formatı. Sadece JPG, PNG ve PDF dosyaları kabul edilir.'
            }, status=400)

        # Benzersiz dosya adı oluştur
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_filename)
        
        # Uploads klasörünü oluştur
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Dosyayı kaydet
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # OCR servisini başlat
        ocr_service = OCRService(use_google_vision=settings.USE_GOOGLE_VISION)
        
        # Belgeyi işle
        result = ocr_service.process_image(file_path)
        
        # Geçici dosyayı sil
        os.remove(file_path)
        
        return JsonResponse({
            'success': True,
            'data': result
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def ocr_status(request):
    """
    OCR servis durumunu kontrol eden endpoint
    """
    try:
        ocr_service = OCRService(use_google_vision=settings.USE_GOOGLE_VISION)
        
        status = {
            'success': True,
            'status': 'active',
            'supported_languages': ['tur', 'eng'],
            'google_vision_enabled': settings.USE_GOOGLE_VISION
        }
        
        # Google Vision durumunu kontrol et
        if settings.USE_GOOGLE_VISION:
            try:
                # Test görüntüsü oluştur
                test_image = np.zeros((100, 100, 3), dtype=np.uint8)
                cv2.putText(test_image, 'Test', (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Geçici dosya oluştur
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_test.jpg')
                cv2.imwrite(temp_path, test_image)
                
                # Google Vision'ı test et
                result = ocr_service._extract_with_google_vision(temp_path)
                
                # Geçici dosyayı sil
                os.remove(temp_path)
                
                status['google_vision_status'] = 'active'
            except Exception as e:
                status['google_vision_status'] = f'error: {str(e)}'
        
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 