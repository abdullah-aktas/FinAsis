import os
import requests
import pytesseract
from PIL import Image
from io import BytesIO
from datetime import datetime
from django.conf import settings
from .models import EInvoice, EArchive, BankIntegration

class EInvoiceService:
    def __init__(self):
        self.api_url = settings.EINVOICE_API_URL
        self.api_key = settings.EINVOICE_API_KEY

    def create_invoice(self, data):
        """E-fatura oluştur"""
        invoice = EInvoice.objects.create(
            invoice_number=self.generate_invoice_number(),
            sender=data['sender'],
            receiver_vkn=data['receiver_vkn'],
            receiver_name=data['receiver_name'],
            amount=data['amount'],
            currency=data.get('currency', 'TRY')
        )
        
        # E-fatura servisine gönder
        response = requests.post(
            f"{self.api_url}/invoices",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=self.prepare_invoice_data(invoice)
        )
        
        if response.status_code == 201:
            invoice.status = 'SENT'
            invoice.save()
            return invoice
        else:
            invoice.status = 'ERROR'
            invoice.save()
            raise Exception("E-fatura gönderilemedi")

    def generate_invoice_number(self):
        """Benzersiz fatura numarası oluştur"""
        prefix = "INV"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}{timestamp}"

    def prepare_invoice_data(self, invoice):
        """E-fatura verilerini hazırla"""
        return {
            "invoiceNumber": invoice.invoice_number,
            "date": datetime.now().isoformat(),
            "sender": {
                "vkn": invoice.sender.vkn,
                "name": invoice.sender.get_full_name()
            },
            "receiver": {
                "vkn": invoice.receiver_vkn,
                "name": invoice.receiver_name
            },
            "amount": float(invoice.amount),
            "currency": invoice.currency
        }

class EArchiveService:
    def __init__(self):
        self.ocr = pytesseract.pytesseract
        self.ocr.tesseract_cmd = settings.TESSERACT_PATH

    def archive_document(self, file, metadata):
        """Dokümanı arşivle ve OCR uygula"""
        archive = EArchive.objects.create(
            archive_number=self.generate_archive_number(),
            document_type=metadata['type'],
            document_date=metadata['date'],
            document_owner=metadata['owner'],
            file=file,
            metadata=metadata
        )

        # OCR işlemi
        try:
            image = Image.open(file)
            ocr_text = self.ocr.image_to_string(image, lang='tur')
            archive.ocr_content = ocr_text
            archive.status = 'ARCHIVED'
            archive.save()
        except Exception as e:
            archive.status = 'ERROR'
            archive.save()
            raise Exception(f"OCR işlemi başarısız: {str(e)}")

        return archive

    def generate_archive_number(self):
        """Benzersiz arşiv numarası oluştur"""
        prefix = "ARC"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}{timestamp}"

class BankIntegrationService:
    def __init__(self, bank_integration):
        self.integration = bank_integration
        self.api_base_url = self.get_bank_api_url()

    def get_bank_api_url(self):
        """Banka API URL'sini döndür"""
        bank_urls = {
            'GARANTI': 'https://api.garantibbva.com.tr',
            'ISBANK': 'https://api.isbank.com.tr',
            'AKBANK': 'https://api.akbank.com',
            'YAPIKREDI': 'https://api.yapikredi.com.tr',
            'ZIRAAT': 'https://api.ziraatbank.com.tr'
        }
        return bank_urls.get(self.integration.bank)

    def get_balance(self):
        """Hesap bakiyesini sorgula"""
        response = requests.get(
            f"{self.api_base_url}/accounts/{self.integration.account_number}/balance",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            self.integration.balance = data['balance']
            self.integration.last_sync = datetime.now()
            self.integration.save()
            return self.integration.balance
        else:
            raise Exception("Bakiye sorgulanamadı")

    def get_transactions(self, start_date, end_date):
        """Hesap hareketlerini sorgula"""
        response = requests.get(
            f"{self.api_base_url}/accounts/{self.integration.account_number}/transactions",
            headers=self.get_headers(),
            params={
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat()
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Hesap hareketleri alınamadı")

    def get_headers(self):
        """API istekleri için header'ları hazırla"""
        return {
            "Authorization": f"Bearer {self.integration.api_key}",
            "X-API-Secret": self.integration.api_secret,
            "Content-Type": "application/json"
        } 