import os
import uuid
import requests
from datetime import datetime
from django.conf import settings
from lxml import etree
from .models import EDocument, EDocumentLog, EDespatchAdvice, EDespatchAdviceLog

class GIBService:
    def __init__(self):
        self.env = os.getenv('EDOCUMENT_ENV', 'TEST')
        self.api_key = os.getenv('EDOCUMENT_API_KEY')
        self.base_url = os.getenv('EDOCUMENT_API_URL')
        
        if self.env == 'TEST':
            self.base_url = 'https://earsivtest.efatura.gov.tr'
        else:
            self.base_url = 'https://earsiv.efatura.gov.tr'
    
    def generate_xml(self, document_data):
        """UBL-TR 1.2 formatında XML oluşturur"""
        try:
            # XML şablonu oluştur
            template = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
                     xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                     xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
                <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
                <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
                <cbc:ProfileID>{document_data['document_type']}</cbc:ProfileID>
                <cbc:ID>{document_data['invoice_number']}</cbc:ID>
                <cbc:UUID>{document_data['uuid']}</cbc:UUID>
                <cbc:IssueDate>{document_data['invoice_date']}</cbc:IssueDate>
                <!-- Diğer XML alanları buraya eklenecek -->
            </Invoice>
            """
            
            # XML doğrulama
            schema = etree.XMLSchema(etree.parse('path/to/ubl-tr-1.2.xsd'))
            parser = etree.XMLParser(schema=schema)
            etree.fromstring(template.encode(), parser)
            
            return template
        except Exception as e:
            raise ValueError(f"XML oluşturma hatası: {str(e)}")
    
    def sign_xml(self, xml_content):
        """XML'i dijital olarak imzalar"""
        try:
            # Test ortamında mock imza
            if self.env == 'TEST':
                return xml_content + "<!-- Mock Signature -->"
            
            # Canlı ortamda gerçek imzalama
            # TODO: Entegratör servisi ile imzalama entegrasyonu
            return xml_content
        except Exception as e:
            raise ValueError(f"İmzalama hatası: {str(e)}")
    
    def send_to_gib(self, document):
        """Belgeyi GİB'e gönderir"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/xml'
            }
            
            response = requests.post(
                f"{self.base_url}/api/invoice/send",
                data=document.signed_xml,
                headers=headers
            )
            
            if response.status_code == 200:
                document.status = 'SENT'
                document.sent_at = datetime.now()
                document.gib_response = response.json()
                document.save()
                
                EDocumentLog.objects.create(
                    document=document,
                    action='SEND',
                    status='SUCCESS',
                    message='Belge başarıyla gönderildi'
                )
            else:
                document.status = 'FAILED'
                document.gib_error_message = response.text
                document.save()
                
                EDocumentLog.objects.create(
                    document=document,
                    action='SEND',
                    status='FAILED',
                    message=f'Gönderim hatası: {response.text}'
                )
                
        except Exception as e:
            document.status = 'FAILED'
            document.gib_error_message = str(e)
            document.save()
            
            EDocumentLog.objects.create(
                document=document,
                action='SEND',
                status='FAILED',
                message=f'Sistem hatası: {str(e)}'
            )

class GIBDespatchService:
    def __init__(self):
        self.env = os.getenv('EDOCUMENT_ENV', 'TEST')
        self.api_key = os.getenv('EDOCUMENT_API_KEY')
        self.base_url = os.getenv('EDOCUMENT_API_URL')
        
        if self.env == 'TEST':
            self.base_url = 'https://earsivtest.efatura.gov.tr'
        else:
            self.base_url = 'https://earsiv.efatura.gov.tr'
    
    def generate_despatch_xml(self, despatch_data):
        """UBL-TR 1.2 DespatchAdvice formatında XML oluşturur"""
        try:
            # XML şablonu oluştur
            template = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
                          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
                <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
                <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
                <cbc:ProfileID>DESPATCHADVICE</cbc:ProfileID>
                <cbc:ID>{despatch_data['despatch_number']}</cbc:ID>
                <cbc:UUID>{despatch_data['uuid']}</cbc:UUID>
                <cbc:IssueDate>{despatch_data['despatch_date']}</cbc:IssueDate>
                <cbc:IssueTime>{despatch_data['despatch_date']}</cbc:IssueTime>
                <!-- Diğer XML alanları buraya eklenecek -->
            </DespatchAdvice>
            """
            
            # XML doğrulama
            schema = etree.XMLSchema(etree.parse('path/to/ubl-tr-despatch-1.2.xsd'))
            parser = etree.XMLParser(schema=schema)
            etree.fromstring(template.encode(), parser)
            
            return template
        except Exception as e:
            raise ValueError(f"XML oluşturma hatası: {str(e)}")
    
    def sign_despatch_xml(self, xml_content):
        """XML'i dijital olarak imzalar"""
        try:
            # Test ortamında mock imza
            if self.env == 'TEST':
                return xml_content + "<!-- Mock Signature -->"
            
            # Canlı ortamda gerçek imzalama
            # TODO: Entegratör servisi ile imzalama entegrasyonu
            return xml_content
        except Exception as e:
            raise ValueError(f"İmzalama hatası: {str(e)}")
    
    def send_to_gib(self, despatch):
        """İrsaliyeyi GİB'e gönderir"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/xml'
            }
            
            response = requests.post(
                f"{self.base_url}/api/despatch/send",
                data=despatch.signed_xml,
                headers=headers
            )
            
            if response.status_code == 200:
                despatch.status = 'SENT'
                despatch.sent_at = datetime.now()
                despatch.gib_response = response.json()
                despatch.save()
                
                EDespatchAdviceLog.objects.create(
                    despatch=despatch,
                    action='SEND',
                    status='SUCCESS',
                    message='İrsaliye başarıyla gönderildi'
                )
            else:
                despatch.status = 'FAILED'
                despatch.gib_error_message = response.text
                despatch.save()
                
                EDespatchAdviceLog.objects.create(
                    despatch=despatch,
                    action='SEND',
                    status='FAILED',
                    message=f'Gönderim hatası: {response.text}'
                )
                
        except Exception as e:
            despatch.status = 'FAILED'
            despatch.gib_error_message = str(e)
            despatch.save()
            
            EDespatchAdviceLog.objects.create(
                despatch=despatch,
                action='SEND',
                status='FAILED',
                message=f'Sistem hatası: {str(e)}'
            )
    
    def process_incoming_despatch(self, xml_content):
        """Gelen irsaliyeyi işler"""
        try:
            # XML doğrulama
            schema = etree.XMLSchema(etree.parse('path/to/ubl-tr-despatch-1.2.xsd'))
            parser = etree.XMLParser(schema=schema)
            etree.fromstring(xml_content.encode(), parser)
            
            # XML'den veri çıkarma
            tree = etree.fromstring(xml_content.encode())
            ns = {'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}
            
            despatch_data = {
                'despatch_number': tree.find('.//cbc:ID', ns).text,
                'uuid': tree.find('.//cbc:UUID', ns).text,
                'despatch_date': tree.find('.//cbc:IssueDate', ns).text,
                'sender_vkn': tree.find('.//cbc:VKN', ns).text,
                # Diğer alanlar buraya eklenecek
            }
            
            return despatch_data
            
        except Exception as e:
            raise ValueError(f"İrsaliye işleme hatası: {str(e)}")
    
    def accept_despatch(self, despatch):
        """İrsaliyeyi kabul eder"""
        try:
            despatch.status = 'ACCEPTED'
            despatch.save()
            
            EDespatchAdviceLog.objects.create(
                despatch=despatch,
                action='ACCEPT',
                status='SUCCESS',
                message='İrsaliye kabul edildi'
            )
            
            # TODO: Stok giriş hareketi oluştur
            if os.getenv('AUTO_STOCK_ENTRY', 'False').lower() == 'true':
                pass  # Stok giriş işlemleri
            
        except Exception as e:
            EDespatchAdviceLog.objects.create(
                despatch=despatch,
                action='ACCEPT',
                status='FAILED',
                message=f'Kabul işlemi hatası: {str(e)}'
            )
            raise
    
    def reject_despatch(self, despatch, reason):
        """İrsaliyeyi reddeder"""
        try:
            despatch.status = 'REJECTED'
            despatch.save()
            
            EDespatchAdviceLog.objects.create(
                despatch=despatch,
                action='REJECT',
                status='SUCCESS',
                message=f'İrsaliye reddedildi. Sebep: {reason}'
            )
            
        except Exception as e:
            EDespatchAdviceLog.objects.create(
                despatch=despatch,
                action='REJECT',
                status='FAILED',
                message=f'Red işlemi hatası: {str(e)}'
            )
            raise 