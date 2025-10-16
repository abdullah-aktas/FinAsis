# -*- coding: utf-8 -*-
import logging
import re
from datetime import datetime
import json
import os
from typing import Any, Dict, Optional

# Optional heavy dependencies; guard to avoid import-time errors.
try:
    import pytesseract  # type: ignore
except Exception:
    pytesseract = None

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None

try:
    import numpy as np  # type: ignore
except Exception:
    np = None

try:
    from google.cloud import vision  # type: ignore
    from google.cloud.vision_v1 import types  # type: ignore
except Exception:
    vision = None
    types = None

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, use_google_vision: bool = False):
        """
        OCR servisi başlatıcı
        """
        self.use_google_vision = use_google_vision
        self.language = os.getenv('OCR_LANGUAGE', 'tur+eng')
        
        # Tesseract yolu Windows için ayarlanıyor
        if os.name == 'nt':  # Windows işletim sistemi
            if pytesseract is not None:
                # Önce ortam değişkeni ile ayarlanmışsa onu kullan
                env_cmd = os.getenv('TESSERACT_CMD')
                default_paths = [
                    r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
                    r'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
                ]
                cmd = env_cmd or next((p for p in default_paths if os.path.exists(p)), None)
                if cmd:
                    try:
                        pytesseract.pytesseract.tesseract_cmd = cmd
                    except Exception:
                        # Ayarlama başarısız olsa da çalışma PATH üzerinden devam eder
                        logger.debug('Tesseract yolu ayarlanamadı, PATH üzerinden deneniyor: %s', cmd)
                else:
                    # Hiçbiri bulunamazsa PATH üzerinden çalışmayı dener
                    logger.debug('Tesseract varsayılan yolu bulunamadı; PATH kullanılacak.')
            
        # Google Cloud Vision istemcisi
        if use_google_vision:
            if vision is None:
                raise RuntimeError("'google-cloud-vision' paketi kurulu değil. 'pip install google-cloud-vision' ile yükleyin veya use_google_vision=False kullanın.")
            self.vision_client = vision.ImageAnnotatorClient()
            
    def preprocess_image(self, image):
        """
        Görüntüyü OCR için hazırlar
        
        Args:
            image (numpy.ndarray): İşlenecek görüntü
            
        Returns:
            numpy.ndarray: İşlenmiş görüntü
        """
        try:
            if cv2 is None:
                raise RuntimeError("'opencv-python' (cv2) paketi kurulu değil.")
            # Gri tonlamaya çevir
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Gürültü azaltma
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Adaptif eşikleme
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return binary
            
        except Exception as e:
            logger.error(f"Görüntü işleme hatası: {str(e)}")
            raise
        
    def extract_invoice_data(self, image_path: str) -> Dict[str, str]:
        """
        Fatura görüntüsünden veri çıkarır
        
        Args:
            image_path (str): Fatura görüntüsü dosya yolu
            
        Returns:
            dict: Fatura bilgileri
        """
        if self.use_google_vision:
            return self._extract_with_google_vision(image_path)
        else:
            return self._extract_with_tesseract(image_path)
            
    def _extract_with_tesseract(self, image_path: str) -> Dict[str, str]:
        """
        Tesseract OCR ile fatura verilerini çıkarır
        """
        try:
            if pytesseract is None or cv2 is None:
                raise RuntimeError("Tesseract için gerekli bağımlılıklar eksik: 'pytesseract' ve/veya 'opencv-python'.")
            # Görüntüyü oku
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Görüntü okunamadı")
            
            # Görüntüyü işle
            processed_image = self.preprocess_image(image)
            
            # OCR işlemi
            text = pytesseract.image_to_string(processed_image, lang=self.language)
            
            # Veri çıkarma
            return self._parse_invoice_text(text)
            
        except Exception as e:
            logger.error(f"Metin çıkarma hatası: {str(e)}")
            raise
        
    def _extract_with_google_vision(self, image_path: str) -> Dict[str, str]:
        """
        Google Cloud Vision ile fatura verilerini çıkarır
        """
        try:
            if vision is None or types is None:
                raise RuntimeError("'google-cloud-vision' paketi kurulu değil.")
            # Görüntüyü oku
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = types.Image(content=content)
            
            # OCR işlemi
            response = self.vision_client.text_detection(image=image)  # type: ignore[attr-defined]
            texts = response.text_annotations
            
            if not texts:
                return {
                    'error': 'Metin bulunamadı',
                    'invoice_number': '',
                    'date': '',
                    'total': '',
                    'tax_rate': '',
                    'company_name': ''
                }
                
            # Tüm metni birleştir
            text = texts[0].description
            
            # Veri çıkarma
            return self._parse_invoice_text(text)
            
        except Exception as e:
            logger.error(f"Google Vision hatası: {str(e)}")
            return {
                'error': f'Google Vision hatası: {str(e)}',
                'invoice_number': '',
                'date': '',
                'total': '',
                'tax_rate': '',
                'company_name': ''
            }

    def _parse_invoice_text(self, text: str) -> Dict[str, str]:
        """
        OCR metninden fatura bilgilerini çıkarır
        
        Args:
            text (str): OCR ile çıkarılan metin
            
        Returns:
            dict: Fatura bilgileri
        """
        result = {
            'invoice_number': '',
            'date': '',
            'total': '',
            'tax_rate': '',
            'company_name': ''
        }
        
        # Fatura numarası için regex
        invoice_patterns = [
            r'Fatura No[:\s]*([A-Z0-9-]+)',
            r'Fatura No[:\s]*([A-Z0-9]+)',
            r'FTR[:\s]*([A-Z0-9-]+)'
        ]
        
        # Tarih için regex
        date_patterns = [
            r'(\d{2}[./]\d{2}[./]\d{4})',
            r'(\d{4}[./]\d{2}[./]\d{2})'
        ]
        
        # Toplam tutar için regex
        total_patterns = [
            r'Toplam[:\s]*([\d.,]+)\s*TL',
            r'Genel Toplam[:\s]*([\d.,]+)\s*TL'
        ]
        
        # KDV oranı için regex
        tax_patterns = [
            r'KDV[:\s]*%?([\d.,]+)',
            r'KDV Oranı[:\s]*%?([\d.,]+)'
        ]
        
        # Firma adı için regex
        company_patterns = [
            r'Firma[:\s]*([^\n]+)',
            r'Ünvan[:\s]*([^\n]+)'
        ]
        
        # Fatura numarası bul
        for pattern in invoice_patterns:
            match = re.search(pattern, text)
            if match:
                result['invoice_number'] = match.group(1).strip()
                break
                
        # Tarih bul
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                try:
                    # Tarihi standart formata çevir
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    result['date'] = date_obj.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
                    
        # Toplam tutar bul
        for pattern in total_patterns:
            match = re.search(pattern, text)
            if match:
                result['total'] = match.group(1).strip()
                break
                
        # KDV oranı bul
        for pattern in tax_patterns:
            match = re.search(pattern, text)
            if match:
                result['tax_rate'] = match.group(1).strip()
                break
                
        # Firma adı bul
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                result['company_name'] = match.group(1).strip()
                break
                
        return result
        
    def process_invoice(self, image_path: str) -> Dict[str, str]:
        """
        Fatura görüntüsünü işler ve sonuçları döndürür
        
        Args:
            image_path (str): Fatura görüntüsü dosya yolu
            
        Returns:
            dict: İşlenmiş fatura bilgileri
        """
        try:
            # Basit PDF tespiti: pdf2image entegrasyonu yoksa nazikçe uyar.
            _, ext = os.path.splitext(image_path.lower())
            if ext == '.pdf':
                return {
                    'error': 'PDF önizleme/OCR henüz etkin değil. Lütfen JPG/PNG yükleyin veya pdf2image kurulumu ile etkinleştiriniz.',
                    'invoice_number': '', 'date': '', 'total': '', 'tax_rate': '', 'company_name': ''
                }
            return self.extract_invoice_data(image_path)
        except Exception as e:
            logger.error(f"Fatura işleme hatası: {str(e)}")
            return {
                'error': str(e),
                'invoice_number': '',
                'date': '',
                'total': '',
                'tax_rate': '',
                'company_name': ''
            }
        
    def validate_invoice_data(self, data):
        """
        Çıkarılan fatura bilgilerini doğrular
        
        Args:
            data (dict): Fatura bilgileri
            
        Returns:
            tuple: (bool, list) - Doğrulama sonucu ve hata mesajları
        """
        errors = []
        
        if not data.get('invoice_number'):
            errors.append("Fatura numarası bulunamadı")
            
        if not data.get('date'):
            errors.append("Fatura tarihi bulunamadı")
            
        if not data.get('total'):
            errors.append("Toplam tutar bulunamadı")
            
        if not data.get('company_name'):
            errors.append("Firma adı bulunamadı")
            
        return len(errors) == 0, errors 