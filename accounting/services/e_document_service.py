# -*- coding: utf-8 -*-
import os
import json
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.files.base import ContentFile
from ..models import EDocument, EDocumentSettings, Invoice
import uuid

logger = logging.getLogger(__name__)

class EDocumentService:
    """
    E-belge entegrasyonu için servis sınıfı.
    Bu sınıf, dış sistemlerle (GİB, entegratörler vb.) iletişim kurar ve 
    e-belge işlemlerini gerçekleştirir.
    """
    
    def __init__(self):
        self.settings = EDocumentSettings.objects.filter(is_active=True).first()
        if not self.settings:
            raise ValueError("Aktif e-belge ayarları bulunamadı")
        self.headers = self._get_auth_headers()
    
    def _get_auth_headers(self):
        """Entegrasyon tipine göre kimlik doğrulama başlıklarını oluşturur"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.settings.integration_type == 'GIB':
            headers['Authorization'] = f"Bearer {self.settings.api_key}"
        elif self.settings.integration_type in ['EFATURA', 'EFINANS', 'TEFATURA']:
            headers['X-API-Key'] = self.settings.api_key
            if self.settings.username and self.settings.password:
                headers['X-Username'] = self.settings.username
                headers['X-Password'] = self.settings.password
        elif self.settings.integration_type == 'CUSTOM':
            # Özel entegrasyon için başlıkları ayarlardan al
            custom_headers = json.loads(self.settings.api_key or '{}')
            headers.update(custom_headers)
        
        return headers
    
    def _make_request(self, method, endpoint, data=None, files=None):
        """API isteği yapar"""
        try:
            url = f"{self.settings.service_url.rstrip('/')}/{endpoint.lstrip('/')}"
            headers = self._get_auth_headers()
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Desteklenmeyen HTTP metodu: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API isteği başarısız: {str(e)}")
            raise
    
    def create_e_invoice(self, invoice):
        """E-fatura oluşturur"""
        try:
            # XML oluştur
            xml_content = self._generate_invoice_xml(invoice)
            
            # E-belge kaydı oluştur
            edoc = EDocument.objects.create(
                invoice=invoice,
                document_type='EINVOICE',
                status='DRAFT',
                target_vkn_tckn=invoice.customer.tax_number,
                target_name=invoice.customer.name,
                xml_content=xml_content
            )
            
            # XML dosyasını kaydet
            edoc.save_xml(xml_content)
            
            # Otomatik gönderim aktifse gönder
            if self.settings.auto_send:
                self.send_document(edoc)
                
            return edoc
            
        except Exception as e:
            logger.error(f"E-fatura oluşturma hatası: {str(e)}")
            raise
    
    def create_e_archive_invoice(self, invoice):
        """E-arşiv fatura oluşturur"""
        try:
            # XML oluştur
            xml_content = self._generate_archive_xml(invoice)
            
            # E-belge kaydı oluştur
            edoc = EDocument.objects.create(
                invoice=invoice,
                document_type='EARCHIVE',
                status='DRAFT',
                target_vkn_tckn=invoice.customer.tax_number,
                target_name=invoice.customer.name,
                xml_content=xml_content
            )
            
            # XML dosyasını kaydet
            edoc.save_xml(xml_content)
            
            # Otomatik gönderim aktifse gönder
            if self.settings.auto_send:
                self.send_document(edoc)
                
            return edoc
            
        except Exception as e:
            logger.error(f"E-arşiv fatura oluşturma hatası: {str(e)}")
            raise
    
    def send_document(self, edoc):
        """E-belgeyi gönderir"""
        try:
            # XML dosyasını hazırla
            files = {
                'xml': ('invoice.xml', edoc.xml_content.encode('utf-8'), 'application/xml')
            }
            
            # API'ye gönder
            response = self._make_request('POST', '/send', files=files)
            
            # Durumu güncelle
            edoc.status = 'SENT'
            edoc.document_number = response.get('document_number')
            edoc.external_id = response.get('external_id')
            edoc.sent_at = datetime.now()
            edoc.save()
            
            # PDF'i indir ve kaydet
            if 'pdf_url' in response:
                pdf_content = requests.get(response['pdf_url']).content
                edoc.save_pdf(pdf_content)
                
            return edoc
            
        except Exception as e:
            logger.error(f"E-belge gönderme hatası: {str(e)}")
            edoc.status = 'ERROR'
            edoc.error_message = str(e)
            edoc.save()
            raise
    
    def check_document_status(self, edoc):
        """E-belge durumunu kontrol eder"""
        try:
            response = self._make_request('GET', f'/status/{edoc.external_id}')
            
            edoc.status = response.get('status', edoc.status)
            edoc.status_message = response.get('message')
            
            if response.get('status') == 'ACCEPTED':
                edoc.accepted_at = datetime.now()
                
            edoc.save()
            return edoc
            
        except Exception as e:
            logger.error(f"E-belge durum kontrolü hatası: {str(e)}")
            raise
    
    def download_document_pdf(self, edoc):
        """E-belge PDF'ini indirir"""
        try:
            response = self._make_request('GET', f'/download/{edoc.external_id}')
            
            if 'pdf_url' in response:
                pdf_content = requests.get(response['pdf_url']).content
                edoc.save_pdf(pdf_content)
                return edoc.pdf_file
                
            return None
            
        except Exception as e:
            logger.error(f"E-belge PDF indirme hatası: {str(e)}")
            raise
    
    def cancel_document(self, edoc, reason=None):
        """E-belgeyi iptal eder"""
        try:
            data = {'reason': reason} if reason else {}
            response = self._make_request('POST', f'/cancel/{edoc.external_id}', data=data)
            
            edoc.status = 'CANCELED'
            edoc.status_message = response.get('message')
            edoc.save()
            
            return edoc
            
        except Exception as e:
            logger.error(f"E-belge iptal hatası: {str(e)}")
            raise
    
    def _generate_invoice_xml(self, invoice):
        """E-fatura XML'i oluşturur"""
        try:
            # XML şablonunu yükle
            template = self._load_xml_template('e_invoice')
            
            # Şirket bilgilerini al
            company = {
                'name': self.settings.company_name,
                'vkn_tckn': self.settings.vkn_tckn,
                'tax_office': self.settings.tax_office,
                'address': self.settings.address,
                'phone': self.settings.phone,
                'email': self.settings.email
            }
            
            # Müşteri bilgilerini al
            customer = {
                'name': invoice.customer.name,
                'vkn_tckn': invoice.customer.tax_number,
                'tax_office': invoice.customer.tax_office,
                'address': invoice.customer.address,
                'phone': invoice.customer.phone,
                'email': invoice.customer.email
            }
            
            # Fatura kalemlerini oluştur
            lines = []
            for line in invoice.lines.all():
                lines.append({
                    'name': line.product.name,
                    'quantity': float(line.quantity),
                    'unit': line.unit,
                    'unit_price': float(line.unit_price),
                    'tax_rate': float(line.tax_rate),
                    'tax_amount': float(line.tax_amount),
                    'total': float(line.total),
                    'description': line.description
                })
            
            # Fatura toplamlarını hesapla
            totals = {
                'subtotal': float(invoice.subtotal),
                'tax_total': float(invoice.tax_total),
                'total': float(invoice.total)
            }
            
            # XML içeriğini oluştur
            xml_content = template.format(
                uuid=str(uuid.uuid4()),
                date=invoice.date.strftime('%Y%m%d'),
                time=invoice.date.strftime('%H%M%S'),
                invoice_number=invoice.number,
                company_name=company['name'],
                company_vkn=company['vkn_tckn'],
                company_tax_office=company['tax_office'],
                company_address=company['address'],
                company_phone=company['phone'],
                company_email=company['email'],
                customer_name=customer['name'],
                customer_vkn=customer['vkn_tckn'],
                customer_tax_office=customer['tax_office'],
                customer_address=customer['address'],
                customer_phone=customer['phone'],
                customer_email=customer['email'],
                lines=self._generate_lines_xml(lines),
                subtotal=totals['subtotal'],
                tax_total=totals['tax_total'],
                total=totals['total']
            )
            
            return xml_content
            
        except Exception as e:
            logger.error(f"E-fatura XML oluşturma hatası: {str(e)}")
            raise
            
    def _generate_archive_xml(self, invoice):
        """E-arşiv fatura XML'i oluşturur"""
        try:
            # XML şablonunu yükle
            template = self._load_xml_template('e_archive')
            
            # Şirket bilgilerini al
            company = {
                'name': self.settings.company_name,
                'vkn_tckn': self.settings.vkn_tckn,
                'tax_office': self.settings.tax_office,
                'address': self.settings.address,
                'phone': self.settings.phone,
                'email': self.settings.email
            }
            
            # Müşteri bilgilerini al
            customer = {
                'name': invoice.customer.name,
                'vkn_tckn': invoice.customer.tax_number,
                'tax_office': invoice.customer.tax_office,
                'address': invoice.customer.address,
                'phone': invoice.customer.phone,
                'email': invoice.customer.email
            }
            
            # Fatura kalemlerini oluştur
            lines = []
            for line in invoice.lines.all():
                lines.append({
                    'name': line.product.name,
                    'quantity': float(line.quantity),
                    'unit': line.unit,
                    'unit_price': float(line.unit_price),
                    'tax_rate': float(line.tax_rate),
                    'tax_amount': float(line.tax_amount),
                    'total': float(line.total),
                    'description': line.description
                })
            
            # Fatura toplamlarını hesapla
            totals = {
                'subtotal': float(invoice.subtotal),
                'tax_total': float(invoice.tax_total),
                'total': float(invoice.total)
            }
            
            # XML içeriğini oluştur
            xml_content = template.format(
                uuid=str(uuid.uuid4()),
                date=invoice.date.strftime('%Y%m%d'),
                time=invoice.date.strftime('%H%M%S'),
                invoice_number=invoice.number,
                company_name=company['name'],
                company_vkn=company['vkn_tckn'],
                company_tax_office=company['tax_office'],
                company_address=company['address'],
                company_phone=company['phone'],
                company_email=company['email'],
                customer_name=customer['name'],
                customer_vkn=customer['vkn_tckn'],
                customer_tax_office=customer['tax_office'],
                customer_address=customer['address'],
                customer_phone=customer['phone'],
                customer_email=customer['email'],
                lines=self._generate_lines_xml(lines),
                subtotal=totals['subtotal'],
                tax_total=totals['tax_total'],
                total=totals['total']
            )
            
            return xml_content
            
        except Exception as e:
            logger.error(f"E-arşiv fatura XML oluşturma hatası: {str(e)}")
            raise
            
    def _generate_lines_xml(self, lines):
        """Fatura kalemleri için XML oluşturur"""
        xml_lines = []
        for line in lines:
            xml_lines.append(f"""
                <InvoiceLine>
                    <Name>{line['name']}</Name>
                    <Quantity>{line['quantity']}</Quantity>
                    <Unit>{line['unit']}</Unit>
                    <UnitPrice>{line['unit_price']}</UnitPrice>
                    <TaxRate>{line['tax_rate']}</TaxRate>
                    <TaxAmount>{line['tax_amount']}</TaxAmount>
                    <Total>{line['total']}</Total>
                    <Description>{line['description']}</Description>
                </InvoiceLine>
            """)
        return ''.join(xml_lines)
        
    def _load_xml_template(self, template_name):
        """XML şablonunu yükler"""
        try:
            template_path = os.path.join(settings.BASE_DIR, 'accounting', 'templates', 'xml', f'{template_name}.xml')
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"XML şablonu yükleme hatası: {str(e)}")
            raise
    
    def send_document_to_service(self, e_document):
        """E-Belgeyi harici e-belge servisine gönderir"""
        url = f"{self.api_url}/send"
        
        data = {
            'documentType': e_document.document_type,
            'documentNumber': e_document.document_number,
            'documentUUID': str(e_document.uuid),
            'content': e_document.xml_content,
            'targetVknTckn': e_document.target_vkn_tckn,
            'targetName': e_document.target_name,
            'companyVkn': self.company_vkn,
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def download_document_pdf(self, e_document):
        """E-Belge PDF dosyasını indirir"""
        # Eğer PDF zaten varsa doğrudan dosya yolunu döndür
        if e_document.pdf_file:
            return {'success': True, 'pdf_path': e_document.pdf_file.path}
        
        # Servis üzerinden PDF indirme
        url = f"{self.api_url}/pdf/{str(e_document.uuid)}"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            # PDF içeriğini kaydet
            pdf_content = ContentFile(response.content)
            filename = f"{e_document.document_number}.pdf"
            e_document.pdf_file.save(filename, pdf_content)
            
            return {'success': True, 'pdf_path': e_document.pdf_file.path}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
            
    def create_e_archive_invoice(self, invoice):
        """E-Arşiv fatura oluşturur"""
        # XML oluştur
        xml_content = self.generate_invoice_xml(invoice)
        
        # Yeni E-Belge oluştur
        document_number = f"EA-{invoice.invoice_number}"
        e_document = EDocument.objects.create(
            invoice=invoice,
            document_type='ARCHIVE_INVOICE',
            document_number=document_number,
            xml_content=xml_content,
            status='PENDING',
            target_vkn_tckn=invoice.account.tax_id,
            target_name=invoice.account.name
        )
        
        # E-Arşiv Fatura servisine gönder
        try:
            response = self.send_document_to_service(e_document)
            if response.get('success'):
                e_document.status = 'ACCEPTED'  # E-Arşiv faturaları genelde hemen kabul edilir
                e_document.sent_at = timezone.now()
                e_document.accepted_at = timezone.now()
                e_document.status_message = 'E-Arşiv fatura başarıyla oluşturuldu'
                
                # Servis tarafından dönen PDF dosyasını kaydet
                if response.get('pdf_url'):
                    pdf_response = requests.get(response.get('pdf_url'))
                    if pdf_response.status_code == 200:
                        from django.core.files.base import ContentFile
                        pdf_content = ContentFile(pdf_response.content)
                        e_document.pdf_file.save(f"{e_document.document_number}.pdf", pdf_content)
            else:
                e_document.status = 'ERROR'
                e_document.status_message = response.get('error', 'Bilinmeyen bir hata oluştu')
        except Exception as e:
            e_document.status = 'ERROR'
            e_document.status_message = str(e)
        
        e_document.save()
        return e_document 