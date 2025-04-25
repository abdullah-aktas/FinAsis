import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import pytesseract
from django.core.files.uploadedfile import InMemoryUploadedFile
import io

class Scanner:
    @staticmethod
    def scan_barcode(image):
        """
        Verilen görüntüden barkod okur
        """
        if isinstance(image, InMemoryUploadedFile):
            image = Image.open(image)
            image = np.array(image)
        
        decoded_objects = decode(image)
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        return None

    @staticmethod
    def scan_document(image):
        """
        Verilen görüntüden metin çıkarır
        """
        if isinstance(image, InMemoryUploadedFile):
            image = Image.open(image)
        
        text = pytesseract.image_to_string(image, lang='tur')
        return text.strip()

    @staticmethod
    def process_image(image):
        """
        Görüntüyü işler ve hem barkod hem de metin taraması yapar
        """
        results = {
            'barcode': None,
            'text': None
        }
        
        if isinstance(image, InMemoryUploadedFile):
            image_data = image.read()
            image = Image.open(io.BytesIO(image_data))
            image_np = np.array(image)
        else:
            image_np = image

        # Barkod taraması
        decoded_objects = decode(image_np)
        if decoded_objects:
            results['barcode'] = decoded_objects[0].data.decode('utf-8')

        # Metin taraması
        text = pytesseract.image_to_string(image, lang='tur')
        results['text'] = text.strip()

        return results 