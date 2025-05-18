# -*- coding: utf-8 -*-
import os
import uuid
import requests
import logging
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from lxml import etree
from .models import (
    EDocument, EDocumentLog, EDocumentItem,
    EDespatchAdvice, EDespatchAdviceLog, EDespatchAdviceItem
)

logger = logging.getLogger(__name__)

class BaseGIBService:
    """GİB servisleri için temel sınıf"""
    def __init__(self):
        self.env = os.getenv('EDOCUMENT_ENV', 'TEST')
        self.api_key = os.getenv('EDOCUMENT_API_KEY')
        self.base_url = os.getenv('EDOCUMENT_API_URL')
        
        if self.env == 'TEST':
            self.base_url = 'https://earsivtest.efatura.gov.tr'
        else:
            self.base_url = 'https://earsiv.efatura.gov.tr'
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/xml'
        })
    
    def _validate_xml(self, xml_content, schema_path):
        """XML doğrulama"""
        try:
            schema = etree.XMLSchema(etree.parse(schema_path))
            parser = etree.XMLParser(schema=schema)
            etree.fromstring(xml_content.encode(), parser)
            return True
        except Exception as e:
            logger.error(f"XML doğrulama hatası: {str(e)}")
            raise ValidationError(f"XML doğrulama hatası: {str(e)}")
    
    def _create_log(self, document, action, status, level='INFO', message='', details=None):
        """Log kaydı oluşturma"""
        log_model = EDocumentLog if isinstance(document, EDocument) else EDespatchAdviceLog
        log_model.objects.create(
            document=document,
            action=action,
            status=status,
            level=level,
            message=message,
            details=details
        )

class GIBInvoiceService(BaseGIBService):
    """E-Fatura servisi"""
    def __init__(self):
        super().__init__()
        self.schema_path = os.path.join(settings.BASE_DIR, 'schemas', 'ubl-tr-1.2.xsd')
    
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
                <cbc:DueDate>{document_data['due_date']}</cbc:DueDate>
                <cbc:DocumentCurrencyCode>{document_data['currency']}</cbc:DocumentCurrencyCode>
                <cbc:LineCountNumeric>{len(document_data['items'])}</cbc:LineCountNumeric>
                
                <!-- Gönderici bilgileri -->
                <cac:AccountingSupplierParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID schemeID="VKN">{document_data['sender_vkn']}</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PartyName>
                            <cbc:Name>{document_data['sender_name']}</cbc:Name>
                        </cac:PartyName>
                    </cac:Party>
                </cac:AccountingSupplierParty>
                
                <!-- Alıcı bilgileri -->
                <cac:AccountingCustomerParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID schemeID="VKN">{document_data['receiver_vkn']}</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PartyName>
                            <cbc:Name>{document_data['receiver_name']}</cbc:Name>
                        </cac:PartyName>
                    </cac:Party>
                </cac:AccountingCustomerParty>
                
                <!-- Fatura kalemleri -->
                {self._generate_invoice_lines(document_data['items'])}
                
                <!-- Toplam tutarlar -->
                <cac:LegalMonetaryTotal>
                    <cbc:LineExtensionAmount>{document_data['total_amount']}</cbc:LineExtensionAmount>
                    <cbc:TaxExclusiveAmount>{document_data['total_amount'] - document_data['total_tax']}</cbc:TaxExclusiveAmount>
                    <cbc:TaxInclusiveAmount>{document_data['total_amount']}</cbc:TaxInclusiveAmount>
                    <cbc:AllowanceTotalAmount>{document_data['total_discount']}</cbc:AllowanceTotalAmount>
                    <cbc:PayableAmount>{document_data['total_amount']}</cbc:PayableAmount>
                </cac:LegalMonetaryTotal>
            </Invoice>
            """
            
            # XML doğrulama
            self._validate_xml(template, self.schema_path)
            
            return template
        except Exception as e:
            logger.error(f"XML oluşturma hatası: {str(e)}")
            raise ValidationError(f"XML oluşturma hatası: {str(e)}")
    
    def _generate_invoice_lines(self, items):
        """Fatura kalemlerini XML formatına dönüştürür"""
        lines = []
        for item in items:
            line = f"""
            <cac:InvoiceLine>
                <cbc:ID>{item['line_number']}</cbc:ID>
                <cbc:InvoicedQuantity unitCode="{item['unit']}">{item['quantity']}</cbc:InvoicedQuantity>
                <cbc:LineExtensionAmount>{item['total_amount']}</cbc:LineExtensionAmount>
                <cac:Item>
                    <cbc:Name>{item['product_name']}</cbc:Name>
                    <cac:SellersItemIdentification>
                        <cbc:ID>{item['product_code']}</cbc:ID>
                    </cac:SellersItemIdentification>
                </cac:Item>
                <cac:Price>
                    <cbc:PriceAmount>{item['unit_price']}</cbc:PriceAmount>
                </cac:Price>
                <cac:TaxTotal>
                    <cbc:TaxAmount>{item['tax_amount']}</cbc:TaxAmount>
                    <cac:TaxSubtotal>
                        <cbc:TaxableAmount>{item['total_amount'] - item['tax_amount']}</cbc:TaxableAmount>
                        <cbc:TaxAmount>{item['tax_amount']}</cbc:TaxAmount>
                        <cac:TaxCategory>
                            <cbc:Percent>{item['tax_rate']}</cbc:Percent>
                            <cac:TaxScheme>
                                <cbc:Name>KDV</cbc:Name>
                                <cbc:TaxTypeCode>0015</cbc:TaxTypeCode>
                            </cac:TaxScheme>
                        </cac:TaxCategory>
                    </cac:TaxSubtotal>
                </cac:TaxTotal>
            </cac:InvoiceLine>
            """
            lines.append(line)
        return ''.join(lines)
    
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
            logger.error(f"İmzalama hatası: {str(e)}")
            raise ValidationError(f"İmzalama hatası: {str(e)}")
    
    def send_to_gib(self, document):
        """Belgeyi GİB'e gönderir"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/invoice/send",
                data=document.signed_xml
            )
            
            if response.status_code == 200:
                document.status = 'SENT'
                document.sent_at = datetime.now()
                document.gib_response = response.json()
                document.save()
                
                self._create_log(
                    document=document,
                    action='SEND',
                    status='SUCCESS',
                    message='Belge başarıyla gönderildi',
                    details=response.json()
                )
            else:
                document.status = 'FAILED'
                document.gib_error_message = response.text
                document.save()
                
                self._create_log(
                    document=document,
                    action='SEND',
                    status='FAILED',
                    level='ERROR',
                    message=f'Gönderim hatası: {response.text}',
                    details={'status_code': response.status_code, 'response': response.text}
                )
                
        except Exception as e:
            document.status = 'FAILED'
            document.gib_error_message = str(e)
            document.save()
            
            self._create_log(
                document=document,
                action='SEND',
                status='FAILED',
                level='ERROR',
                message=f'Sistem hatası: {str(e)}',
                details={'error': str(e)}
            )
    
    def cancel_invoice(self, document, reason):
        """Faturayı iptal eder"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/invoice/cancel",
                json={
                    'uuid': str(document.uuid),
                    'reason': reason
                }
            )
            
            if response.status_code == 200:
                document.status = 'CANCELLED'
                document.save()
                
                self._create_log(
                    document=document,
                    action='CANCEL',
                    status='SUCCESS',
                    message=f'Belge iptal edildi: {reason}',
                    details=response.json()
                )
            else:
                self._create_log(
                    document=document,
                    action='CANCEL',
                    status='FAILED',
                    level='ERROR',
                    message=f'İptal hatası: {response.text}',
                    details={'status_code': response.status_code, 'response': response.text}
                )
                
        except Exception as e:
            self._create_log(
                document=document,
                action='CANCEL',
                status='FAILED',
                level='ERROR',
                message=f'Sistem hatası: {str(e)}',
                details={'error': str(e)}
            )

class GIBDespatchService(BaseGIBService):
    """E-İrsaliye servisi"""
    def __init__(self):
        super().__init__()
        self.schema_path = os.path.join(settings.BASE_DIR, 'schemas', 'ubl-tr-despatch-1.2.xsd')
    
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
                <cbc:DespatchAdviceTypeCode>SEVK</cbc:DespatchAdviceTypeCode>
                
                <!-- Gönderici bilgileri -->
                <cac:DespatchSupplierParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID schemeID="VKN">{despatch_data['sender_vkn']}</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PartyName>
                            <cbc:Name>{despatch_data['sender_name']}</cbc:Name>
                        </cac:PartyName>
                    </cac:Party>
                </cac:DespatchSupplierParty>
                
                <!-- Alıcı bilgileri -->
                <cac:DeliveryCustomerParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID schemeID="VKN">{despatch_data['receiver_vkn']}</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PartyName>
                            <cbc:Name>{despatch_data['receiver_name']}</cbc:Name>
                        </cac:PartyName>
                    </cac:Party>
                </cac:DeliveryCustomerParty>
                
                <!-- Taşıma bilgileri -->
                <cac:Shipment>
                    <cbc:ID>{despatch_data['despatch_number']}</cbc:ID>
                    <cbc:HandlingCode>{despatch_data['transport_type']}</cbc:HandlingCode>
                    <cac:TransportHandlingUnit>
                        <cbc:TransportHandlingUnitTypeCode>PLT</cbc:TransportHandlingUnitTypeCode>
                        <cbc:ID>{despatch_data['vehicle_plate']}</cbc:ID>
                    </cac:TransportHandlingUnit>
                    <cac:TransportMeans>
                        <cbc:RegistrationNationalityID>TR</cbc:RegistrationNationalityID>
                        <cbc:RegistrationNationality>TR</cbc:RegistrationNationality>
                        <cac:DriverPerson>
                            <cbc:ID>{despatch_data['driver_tckn']}</cbc:ID>
                            <cbc:Name>{despatch_data['driver_name']}</cbc:Name>
                        </cac:DriverPerson>
                    </cac:TransportMeans>
                </cac:Shipment>
                
                <!-- İrsaliye kalemleri -->
                {self._generate_despatch_lines(despatch_data['items'])}
            </DespatchAdvice>
            """
            
            # XML doğrulama
            self._validate_xml(template, self.schema_path)
            
            return template
        except Exception as e:
            logger.error(f"XML oluşturma hatası: {str(e)}")
            raise ValidationError(f"XML oluşturma hatası: {str(e)}")
    
    def _generate_despatch_lines(self, items):
        """İrsaliye kalemlerini XML formatına dönüştürür"""
        lines = []
        for item in items:
            line = f"""
            <cac:DespatchLine>
                <cbc:ID>{item['line_number']}</cbc:ID>
                <cbc:DeliveredQuantity unitCode="{item['unit']}">{item['quantity']}</cbc:DeliveredQuantity>
                <cac:Item>
                    <cbc:Name>{item['product_name']}</cbc:Name>
                    <cac:SellersItemIdentification>
                        <cbc:ID>{item['product_code']}</cbc:ID>
                    </cac:SellersItemIdentification>
                </cac:Item>
            </cac:DespatchLine>
            """
            lines.append(line)
        return ''.join(lines)
    
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
            logger.error(f"İmzalama hatası: {str(e)}")
            raise ValidationError(f"İmzalama hatası: {str(e)}")
    
    def send_to_gib(self, despatch):
        """İrsaliyeyi GİB'e gönderir"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/despatch/send",
                data=despatch.signed_xml
            )
            
            if response.status_code == 200:
                despatch.status = 'SENT'
                despatch.sent_at = datetime.now()
                despatch.gib_response = response.json()
                despatch.save()
                
                self._create_log(
                    document=despatch,
                    action='SEND',
                    status='SUCCESS',
                    message='İrsaliye başarıyla gönderildi',
                    details=response.json()
                )
            else:
                despatch.status = 'FAILED'
                despatch.gib_error_message = response.text
                despatch.save()
                
                self._create_log(
                    document=despatch,
                    action='SEND',
                    status='FAILED',
                    level='ERROR',
                    message=f'Gönderim hatası: {response.text}',
                    details={'status_code': response.status_code, 'response': response.text}
                )
                
        except Exception as e:
            despatch.status = 'FAILED'
            despatch.gib_error_message = str(e)
            despatch.save()
            
            self._create_log(
                document=despatch,
                action='SEND',
                status='FAILED',
                level='ERROR',
                message=f'Sistem hatası: {str(e)}',
                details={'error': str(e)}
            )
    
    def process_incoming_despatch(self, xml_content):
        """Gelen irsaliyeyi işler"""
        try:
            # XML doğrulama
            self._validate_xml(xml_content, self.schema_path)
            
            # XML'den veri çıkarma
            tree = etree.fromstring(xml_content.encode())
            ns = {'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}
            
            despatch_data = {
                'despatch_number': tree.find('.//cbc:ID', ns).text,
                'uuid': tree.find('.//cbc:UUID', ns).text,
                'despatch_date': tree.find('.//cbc:IssueDate', ns).text,
                'sender_vkn': tree.find('.//cbc:VKN', ns).text,
                'sender_name': tree.find('.//cbc:Name', ns).text,
                'transport_type': tree.find('.//cbc:HandlingCode', ns).text,
                'vehicle_plate': tree.find('.//cbc:ID', ns).text,
                'driver_name': tree.find('.//cbc:Name', ns).text,
                'driver_tckn': tree.find('.//cbc:ID', ns).text,
            }
            
            return despatch_data
            
        except Exception as e:
            logger.error(f"İrsaliye işleme hatası: {str(e)}")
            raise ValidationError(f"İrsaliye işleme hatası: {str(e)}")
    
    def accept_despatch(self, despatch):
        """İrsaliyeyi kabul eder"""
        try:
            despatch.status = 'ACCEPTED'
            despatch.save()
            
            self._create_log(
                document=despatch,
                action='ACCEPT',
                status='SUCCESS',
                message='İrsaliye kabul edildi'
            )
            
            # İrsaliye kalemlerini güncelle
            for item in despatch.items.all():
                item.accepted_quantity = item.quantity
                item.save()
                
        except Exception as e:
            self._create_log(
                document=despatch,
                action='ACCEPT',
                status='FAILED',
                level='ERROR',
                message=f'Sistem hatası: {str(e)}',
                details={'error': str(e)}
            )
    
    def reject_despatch(self, despatch, reason):
        """İrsaliyeyi reddeder"""
        try:
            despatch.status = 'REJECTED'
            despatch.save()
            
            self._create_log(
                document=despatch,
                action='REJECT',
                status='SUCCESS',
                message=f'İrsaliye reddedildi: {reason}'
            )
            
            # İrsaliye kalemlerini güncelle
            for item in despatch.items.all():
                item.rejected_quantity = item.quantity
                item.save()
                
        except Exception as e:
            self._create_log(
                document=despatch,
                action='REJECT',
                status='FAILED',
                level='ERROR',
                message=f'Sistem hatası: {str(e)}',
                details={'error': str(e)}
            )
    
    def partially_accept_despatch(self, despatch, accepted_items):
        """İrsaliyeyi kısmen kabul eder"""
        try:
            despatch.status = 'PARTIALLY_ACCEPTED'
            despatch.save()
            
            self._create_log(
                document=despatch,
                action='PARTIAL_ACCEPT',
                status='SUCCESS',
                message='İrsaliye kısmen kabul edildi',
                details={'accepted_items': accepted_items}
            )
            
            # İrsaliye kalemlerini güncelle
            for item in despatch.items.all():
                if item.line_number in accepted_items:
                    item.accepted_quantity = item.quantity
                else:
                    item.rejected_quantity = item.quantity
                item.save()
                
        except Exception as e:
            self._create_log(
                document=despatch,
                action='PARTIAL_ACCEPT',
                status='FAILED',
                level='ERROR',
                message=f'Sistem hatası: {str(e)}',
                details={'error': str(e)}
            ) 