# e-Fatura ile ilgili servis fonksiyonları burada tanımlanacak. 

import requests
from django.conf import settings
from ..models import Invoice
import logging

efatura_logger = logging.getLogger("efatura")

def generate_invoice_xml(invoice: Invoice):
    # Burada UBL-TR XML üretimi yapılmalı (örnek/mock)
    return f"<Invoice><ID>{invoice.invoice_number}</ID></Invoice>"

def send_invoice_to_gib(invoice: Invoice):
    xml_data = generate_invoice_xml(invoice)
    url = "https://efatura-test.efatura.gov.tr/api/sendInvoice"  # Örnek URL
    headers = {"Content-Type": "application/xml"}
    try:
        response = requests.post(url, data=xml_data.encode('utf-8'), headers=headers, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD))
        invoice.gib_status = 'sent' if response.status_code == 200 else 'error'
        invoice.gib_response = response.text
        invoice.save()
        efatura_logger.info(f"Fatura {invoice.pk} GİB'e gönderildi. Status: {response.status_code}, Yanıt: {response.text}")
        return response
    except Exception as e:
        efatura_logger.error(f"Fatura {invoice.pk} GİB gönderim hatası: {str(e)}")
        invoice.gib_status = 'error'
        invoice.gib_response = str(e)
        invoice.save()
        raise

def check_invoice_status(invoice: Invoice):
    url = f"https://efatura-test.efatura.gov.tr/api/invoiceStatus/{invoice.gib_uuid}"
    try:
        response = requests.get(url, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD))
        invoice.gib_status = response.json().get('status', 'unknown')
        invoice.gib_response = response.text
        invoice.save()
        efatura_logger.info(f"Fatura {invoice.pk} GİB durum sorgu. Status: {response.status_code}, Yanıt: {response.text}")
        return response
    except Exception as e:
        efatura_logger.error(f"Fatura {invoice.pk} GİB durum sorgu hatası: {str(e)}")
        invoice.gib_status = 'error'
        invoice.gib_response = str(e)
        invoice.save()
        raise

def cancel_invoice_on_gib(invoice: Invoice):
    url = f"https://efatura-test.efatura.gov.tr/api/cancelInvoice/{invoice.gib_uuid}"
    try:
        response = requests.post(url, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD))
        invoice.gib_status = 'cancelled' if response.status_code == 200 else 'error'
        invoice.gib_response = response.text
        invoice.save()
        efatura_logger.info(f"Fatura {invoice.pk} GİB iptal. Status: {response.status_code}, Yanıt: {response.text}")
        return response
    except Exception as e:
        efatura_logger.error(f"Fatura {invoice.pk} GİB iptal hatası: {str(e)}")
        invoice.gib_status = 'error'
        invoice.gib_response = str(e)
        invoice.save()
        raise 