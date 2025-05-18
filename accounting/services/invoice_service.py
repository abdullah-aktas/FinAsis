# -*- coding: utf-8 -*-
import os
import uuid
from datetime import datetime
from django.conf import settings # type: ignore

def _generate_lines_xml(self, invoice_lines):
    """Fatura kalemleri için XML oluşturur."""
    lines_xml = []
    for index, line in enumerate(invoice_lines, 1):
        line_xml = f"""
        <cbc:ID>{index}</cbc:ID>
        <cbc:InvoicedQuantity unitCode="C62">{line.quantity}</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="TRY">{line.subtotal}</cbc:LineExtensionAmount>
        <cac:Item>
            <cbc:Name>{line.description}</cbc:Name>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="TRY">{line.unit_price}</cbc:PriceAmount>
        </cac:Price>
        <cac:TaxTotal>
            <cbc:TaxAmount currencyID="TRY">{line.tax_amount}</cbc:TaxAmount>
            <cac:TaxSubtotal>
                <cbc:TaxableAmount currencyID="TRY">{line.subtotal}</cbc:TaxableAmount>
                <cbc:TaxAmount currencyID="TRY">{line.tax_amount}</cbc:TaxAmount>
                <cbc:Percent>18</cbc:Percent>
                <cac:TaxCategory>
                    <cac:TaxScheme>
                        <cbc:Name>KDV</cbc:Name>
                        <cbc:TaxTypeCode>0015</cbc:TaxTypeCode>
                    </cac:TaxScheme>
                </cac:TaxCategory>
            </cac:TaxSubtotal>
        </cac:TaxTotal>
        """
        lines_xml.append(line_xml)
    return "\n".join(lines_xml)

def create_e_archive_invoice(self, invoice_data):
    """E-arşiv faturası oluşturur."""
    try:
        # XML şablonunu oku
        template_path = os.path.join(settings.BASE_DIR, 'accounting', 'templates', 'xml', 'e_archive.xml')
        with open(template_path, 'r', encoding='utf-8') as file:
            template = file.read()

        # Fatura kalemleri için XML oluştur
        lines_xml = self._generate_lines_xml(invoice_data['lines'])

        # Şablonu doldur
        xml_content = template.format(
            invoice_number=invoice_data['invoice_number'],
            uuid=str(uuid.uuid4()),
            date=datetime.now().strftime('%Y%m%d'),
            time=datetime.now().strftime('%H%M%S'),
            company_name=invoice_data['company_name'],
            company_tax_number=invoice_data['company_tax_number'],
            company_address=invoice_data['company_address'],
            customer_name=invoice_data['customer_name'],
            customer_tax_number=invoice_data['customer_tax_number'],
            customer_address=invoice_data['customer_address'],
            total_amount=invoice_data['total_amount'],
            tax_amount=invoice_data['tax_amount'],
            grand_total=invoice_data['grand_total'],
            lines_xml=lines_xml
        )

        # XML dosyasını kaydet
        output_path = os.path.join(settings.BASE_DIR, 'accounting', 'output', f'e_archive_{invoice_data["invoice_number"]}.xml')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(xml_content)

        return {
            'success': True,
            'message': 'E-arşiv faturası başarıyla oluşturuldu',
            'file_path': output_path
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'E-arşiv faturası oluşturulurken hata oluştu: {str(e)}'
        } 