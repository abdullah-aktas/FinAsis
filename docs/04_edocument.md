# 4. E-Fatura / E-İrsaliye / E-Defter

## 📌 Amaç
Bu dokümantasyon, FinAsis projesinin e-belge sistemlerini (e-fatura, e-irsaliye, e-defter) ve GİB entegrasyonlarını detaylandırmaktadır.

## ⚙️ Teknik Yapı

### 1. UBL-TR 1.2 Şema Yapısı

#### 1.1. XML Şema Doğrulama
```python
from lxml import etree
import os

def validate_ubl_xml(xml_path, schema_path):
    schema_doc = etree.parse(schema_path)
    schema = etree.XMLSchema(schema_doc)
    
    xml_doc = etree.parse(xml_path)
    return schema.validate(xml_doc)
```

#### 1.2. XML Oluşturma
```python
def create_invoice_xml(invoice_data):
    template = """
    <?xml version="1.0" encoding="UTF-8"?>
    <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
             xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
             xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
        <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
        <cbc:ProfileID>EARSIVFATURA</cbc:ProfileID>
        <cbc:ID>{invoice_id}</cbc:ID>
        <cbc:UUID>{uuid}</cbc:UUID>
        <cbc:IssueDate>{issue_date}</cbc:IssueDate>
        <cbc:IssueTime>{issue_time}</cbc:IssueTime>
        <cbc:InvoiceTypeCode>{invoice_type}</cbc:InvoiceTypeCode>
        <cbc:DocumentCurrencyCode>TRY</cbc:DocumentCurrencyCode>
        <cbc:LineCountNumeric>{line_count}</cbc:LineCountNumeric>
    </Invoice>
    """
    return template.format(**invoice_data)
```

### 2. Dijital İmzalama

#### 2.1. XAdES İmzalama
```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

def sign_xml(xml_content, private_key_path):
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    
    signature = private_key.sign(
        xml_content.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    return signature
```

### 3. GİB Entegrasyonu

#### 3.1. GİB API İstemcisi
```python
import requests
from datetime import datetime

class GIBClient:
    def __init__(self, username, password, test_mode=True):
        self.base_url = "https://earsivportaltest.efatura.gov.tr" if test_mode else "https://earsivportal.efatura.gov.tr"
        self.username = username
        self.password = password
        self.token = None
    
    def authenticate(self):
        response = requests.post(
            f"{self.base_url}/earsiv-services/assos-login",
            json={
                "assoscmd": "anologin",
                "rtype": "json",
                "userid": self.username,
                "sifre": self.password,
                "sifre2": self.password,
                "parola": "1"
            }
        )
        self.token = response.json()["token"]
        return self.token
    
    def send_invoice(self, xml_content):
        if not self.token:
            self.authenticate()
        
        response = requests.post(
            f"{self.base_url}/earsiv-services/dispatch",
            json={
                "cmd": "EARSIV_PORTAL_TELEFON",
                "callid": datetime.now().strftime("%Y%m%d%H%M%S"),
                "pageName": "RG_BASITFATURA",
                "token": self.token,
                "parametre": xml_content
            }
        )
        return response.json()
```

## 🔧 Kullanım Adımları

### 1. E-Fatura Oluşturma

#### 1.1. Fatura Verilerini Hazırlama
```python
invoice_data = {
    "invoice_id": "FT2023000000001",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "issue_date": "2023-04-19",
    "issue_time": "14:30:00",
    "invoice_type": "SATIS",
    "line_count": "1"
}

# XML oluşturma
xml_content = create_invoice_xml(invoice_data)

# XML doğrulama
is_valid = validate_ubl_xml(xml_content, "schemas/UBL-TR_1.2.xsd")
```

#### 1.2. Dijital İmzalama ve Gönderim
```python
# XML imzalama
signature = sign_xml(xml_content, "keys/private_key.pem")

# GİB'e gönderme
gib_client = GIBClient(username="test_user", password="test_pass", test_mode=True)
response = gib_client.send_invoice(xml_content)
```

### 2. E-İrsaliye İşlemleri

#### 2.1. İrsaliye Oluşturma
```python
def create_dispatch_note(dispatch_data):
    template = """
    <?xml version="1.0" encoding="UTF-8"?>
    <DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
                    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
        <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
        <cbc:ID>{dispatch_id}</cbc:ID>
        <cbc:UUID>{uuid}</cbc:UUID>
        <cbc:IssueDate>{issue_date}</cbc:IssueDate>
        <cbc:IssueTime>{issue_time}</cbc:IssueTime>
    </DespatchAdvice>
    """
    return template.format(**dispatch_data)
```

## 🧪 Test Örnekleri

### 1. XML Doğrulama Testi
```python
def test_xml_validation():
    # Test XML oluşturma
    test_xml = create_invoice_xml({
        "invoice_id": "TEST001",
        "uuid": "test-uuid",
        "issue_date": "2023-04-19",
        "issue_time": "12:00:00",
        "invoice_type": "SATIS",
        "line_count": "1"
    })
    
    # Doğrulama
    is_valid = validate_ubl_xml(test_xml, "schemas/UBL-TR_1.2.xsd")
    assert is_valid
```

### 2. GİB Entegrasyon Testi
```python
def test_gib_integration():
    client = GIBClient(username="test", password="test", test_mode=True)
    
    # Kimlik doğrulama testi
    token = client.authenticate()
    assert token is not None
    
    # Fatura gönderme testi
    response = client.send_invoice("<test>xml</test>")
    assert "status" in response
```

## 📝 Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. XML Şema Doğrulama Hataları
**Sorun**: XML şema doğrulama hataları
**Çözüm**:
- UBL-TR 1.2 şemasını güncelleyin
- Zorunlu alanları kontrol edin
- XML namespace'lerini doğrulayın

### 2. Dijital İmza Hataları
**Sorun**: İmza doğrulama hataları
**Çözüm**:
- Sertifika geçerlilik süresini kontrol edin
- İmza algoritmasını doğrulayın
- Sertifika zincirini kontrol edin

### 3. GİB API Hataları
**Sorun**: API bağlantı hataları
**Çözüm**:
- API kimlik bilgilerini kontrol edin
- Test/Prod ortam ayarlarını doğrulayın
- Ağ bağlantısını kontrol edin

## 📂 Dosya Yapısı ve Referanslar

```
finasis/
├── apps/
│   └── edocument/
│       ├── schemas/
│       │   ├── UBL-TR_1.2.xsd
│       │   └── validation.py
│       ├── services/
│       │   ├── gib_client.py
│       │   └── signature.py
│       └── templates/
│           ├── invoice.xml
│           └── dispatch.xml
└── config/
    └── certificates/
        ├── private_key.pem
        └── public_key.pem
```

## 🔍 Ek Kaynaklar

- [UBL-TR 1.2 Şema Dokümantasyonu](https://www.efatura.gov.tr/tr/teknik-dokumanlar)
- [GİB E-Arşiv Portal API Dokümantasyonu](https://earsivportaltest.efatura.gov.tr/earstest/earsiv-services)
- [XAdES İmzalama Dokümantasyonu](https://www.w3.org/TR/XAdES/) 