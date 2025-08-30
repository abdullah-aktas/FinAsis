import requests
from django.conf import settings
from ..models import EDefter
import logging

defter_logger = logging.getLogger("edefter")

def generate_yevmiye_defter(company, year, month):
    # Yevmiye defteri için UBL-TR XML üretimi (örnek/mock)
    return f"<YevmiyeDefteri><Yil>{year}</Yil><Ay>{month}</Ay></YevmiyeDefteri>"

def send_edefter_to_gib(edefter: EDefter):
    xml_data = edefter.xml_file.read()
    base_url = getattr(settings, 'GIB_EDEFTER_BASE_URL', 'https://edefter-test.edefter.gov.tr/api')
    url = f"{base_url}/sendDefter"
    headers = {"Content-Type": "application/xml"}
    try:
        response = requests.post(url, data=xml_data, headers=headers, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD))
        edefter.status = 'sent' if response.status_code == 200 else 'error'
        edefter.save()
        defter_logger.info(f"e-Defter {edefter.pk} GİB'e gönderildi. Status: {response.status_code}, Yanıt: {response.text}")
        return response
    except Exception as e:
        defter_logger.error(f"e-Defter {edefter.pk} GİB gönderim hatası: {str(e)}")
        edefter.status = 'error'
        edefter.save()
        raise

def get_edefter_berat(edefter: EDefter):
    base_url = getattr(settings, 'GIB_EDEFTER_BASE_URL', 'https://edefter-test.edefter.gov.tr/api')
    url = f"{base_url}/getBerat/{edefter.id}"
    try:
        response = requests.get(url, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD))
        if response.status_code == 200:
            edefter.berat_file.save(f"berat_{edefter.id}.xml", response.content)
            edefter.status = 'berat_alindi'
            edefter.save()
            defter_logger.info(f"e-Defter {edefter.pk} berat alındı. Status: {response.status_code}")
        else:
            defter_logger.warning(f"e-Defter {edefter.pk} berat alınamadı. Status: {response.status_code}, Yanıt: {response.text}")
        return response
    except Exception as e:
        defter_logger.error(f"e-Defter {edefter.pk} berat alma hatası: {str(e)}")
        edefter.status = 'error'
        edefter.save()
        raise 