# apps/ai_assistant/services/ocr_service.py

import pytesseract
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """Görsellerden metin okumak için OCR hizmeti"""

    def __init__(self):
        # Gerekirse yapılandırma ayarları buraya eklenebilir
        pass

    def extract_text_from_image_file(self, file) -> str:
        """
        Django'dan gelen bir image file (InMemoryUploadedFile gibi) üzerinden metin okur.
        :param file: Django upload edilen dosya nesnesi
        :return: çözümlenmiş metin
        """
        try:
            image = Image.open(file)
            text = pytesseract.image_to_string(image, lang="tur")  # Türkçe destekli OCR
            return text.strip()
        except Exception as e:
            logger.error(f"OCR hatası (image_file): {str(e)}")
            raise

    def extract_text_from_path(self, image_path: str) -> str:
        """
        Dosya yolundan OCR ile metin okur.
        :param image_path: Görselin dosya yolu
        :return: çözümlenmiş metin
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang="tur")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR hatası (image_path): {str(e)}")
            raise
