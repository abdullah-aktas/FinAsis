# -*- coding: utf-8 -*-
import os
import subprocess
import tempfile
from django.conf import settings
from django.core.exceptions import ValidationError

class XMLSigner:
    """XML dijital imzalama işlemleri için yardımcı sınıf"""
    
    @classmethod
    def sign_xml(cls, xml_content, certificate_path=None, private_key_path=None):
        """XML içeriğini dijital olarak imzalar"""
        # Test ortamında mock imza kullan
        if os.getenv('EDOCUMENT_ENV', 'TEST') == 'TEST':
            return cls._mock_sign(xml_content)
        
        # Canlı ortamda gerçek imzalama
        if not certificate_path or not private_key_path:
            raise ValidationError("İmzalama için sertifika ve özel anahtar gerekli")
        
        try:
            # Geçici dosyalar oluştur
            with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp_xml:
                temp_xml.write(xml_content.encode())
                temp_xml_path = temp_xml.name
            
            with tempfile.NamedTemporaryFile(suffix='.xml.sig', delete=False) as temp_sig:
                temp_sig_path = temp_sig.name
            
            # OpenSSL ile imzalama
            cmd = [
                'openssl', 'smime', '-sign',
                '-in', temp_xml_path,
                '-out', temp_sig_path,
                '-signer', certificate_path,
                '-inkey', private_key_path,
                '-nodetach'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise ValidationError(f"İmzalama hatası: {result.stderr}")
            
            # İmzalı XML'i oku
            with open(temp_sig_path, 'rb') as f:
                signed_xml = f.read()
            
            # Geçici dosyaları temizle
            os.unlink(temp_xml_path)
            os.unlink(temp_sig_path)
            
            return signed_xml.decode()
            
        except Exception as e:
            raise ValidationError(f"İmzalama işlemi başarısız: {str(e)}")
    
    @classmethod
    def _mock_sign(cls, xml_content):
        """Test ortamı için mock imza oluşturur"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<MockSignature>
    <OriginalContent>{xml_content}</OriginalContent>
    <SignatureInfo>
        <SignatureValue>MOCK_SIGNATURE_FOR_TESTING</SignatureValue>
        <SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</SignatureAlgorithm>
        <SignedInfo>
            <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
            <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
        </SignedInfo>
    </SignatureInfo>
</MockSignature>""" 