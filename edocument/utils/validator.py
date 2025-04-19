import os
from lxml import etree
from django.conf import settings
from django.core.exceptions import ValidationError

class XMLValidator:
    """XML doğrulama işlemleri için yardımcı sınıf"""
    
    SCHEMA_DIR = os.path.join(settings.BASE_DIR, 'edocument', 'schemas', 'ubltr_1.2')
    
    @classmethod
    def validate_invoice_xml(cls, xml_content):
        """E-Fatura XML içeriğini doğrular"""
        try:
            schema_path = os.path.join(cls.SCHEMA_DIR, 'Invoice.xsd')
            schema = etree.XMLSchema(etree.parse(schema_path))
            parser = etree.XMLParser(schema=schema)
            etree.fromstring(xml_content.encode(), parser)
            return True
        except etree.DocumentInvalid as e:
            error_message = cls._format_validation_error(e)
            raise ValidationError(f"E-Fatura XML doğrulama hatası: {error_message}")
    
    @classmethod
    def validate_despatch_xml(cls, xml_content):
        """E-İrsaliye XML içeriğini doğrular"""
        try:
            schema_path = os.path.join(cls.SCHEMA_DIR, 'DespatchAdvice.xsd')
            schema = etree.XMLSchema(etree.parse(schema_path))
            parser = etree.XMLParser(schema=schema)
            etree.fromstring(xml_content.encode(), parser)
            return True
        except etree.DocumentInvalid as e:
            error_message = cls._format_validation_error(e)
            raise ValidationError(f"E-İrsaliye XML doğrulama hatası: {error_message}")
    
    @classmethod
    def _format_validation_error(cls, error):
        """XML doğrulama hatalarını kullanıcı dostu formata dönüştürür"""
        error_lines = str(error).split('\n')
        formatted_errors = []
        
        for line in error_lines:
            if 'Element' in line and 'is not expected' in line:
                element = line.split("'")[1]
                formatted_errors.append(f"Beklenmeyen öğe: {element}")
            elif 'Missing required element' in line:
                element = line.split("'")[1]
                formatted_errors.append(f"Eksik zorunlu öğe: {element}")
            elif 'Element' in line and 'is not allowed' in line:
                element = line.split("'")[1]
                formatted_errors.append(f"İzin verilmeyen öğe: {element}")
            elif 'Element' in line and 'is not a valid value' in line:
                element = line.split("'")[1]
                formatted_errors.append(f"Geçersiz değer: {element}")
        
        return "\n".join(formatted_errors) if formatted_errors else str(error) 