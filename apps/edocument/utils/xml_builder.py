# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from lxml import etree
from django.conf import settings

class XMLBuilder:
    """XML oluşturma işlemleri için yardımcı sınıf"""
    
    @classmethod
    def build_invoice_xml(cls, invoice_data):
        """E-Fatura XML içeriği oluşturur"""
        # XML şablonu
        template = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
    <cbc:ProfileID>{invoice_data.get('profile_id', 'TICARIFATURA')}</cbc:ProfileID>
    <cbc:ID>{invoice_data.get('invoice_number')}</cbc:ID>
    <cbc:UUID>{invoice_data.get('uuid', str(uuid.uuid4()))}</cbc:UUID>
    <cbc:IssueDate>{invoice_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))}</cbc:IssueDate>
    <cbc:IssueTime>{invoice_data.get('issue_time', datetime.now().strftime('%H:%M:%S'))}</cbc:IssueTime>
    <cbc:InvoiceTypeCode>{invoice_data.get('invoice_type_code', 'SATIS')}</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>{invoice_data.get('currency_code', 'TRY')}</cbc:DocumentCurrencyCode>
    <cbc:LineCountNumeric>{len(invoice_data.get('lines', []))}</cbc:LineCountNumeric>
    
    <!-- Satıcı Bilgileri -->
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cbc:WebsiteURI>{settings.COMPANY_WEBSITE}</cbc:WebsiteURI>
            <cac:PartyIdentification>
                <cbc:ID schemeID="VKN">{settings.COMPANY_VKN}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>{settings.COMPANY_NAME}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{invoice_data.get('seller_street')}</cbc:StreetName>
                <cbc:BuildingNumber>{invoice_data.get('seller_building_no')}</cbc:BuildingNumber>
                <cbc:CitySubdivisionName>{invoice_data.get('seller_district')}</cbc:CitySubdivisionName>
                <cbc:CityName>{invoice_data.get('seller_city')}</cbc:CityName>
                <cbc:PostalZone>{invoice_data.get('seller_postal_code')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:Name>Türkiye</cbc:Name>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cac:TaxScheme>
                    <cbc:Name>{invoice_data.get('seller_tax_office')}</cbc:Name>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:Contact>
                <cbc:Telephone>{invoice_data.get('seller_phone')}</cbc:Telephone>
                <cbc:ElectronicMail>{invoice_data.get('seller_email', settings.COMPANY_EMAIL)}</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:AccountingSupplierParty>
    
    <!-- Alıcı Bilgileri -->
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="VKN">{invoice_data.get('buyer_vkn')}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>{invoice_data.get('buyer_name')}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{invoice_data.get('buyer_street')}</cbc:StreetName>
                <cbc:BuildingNumber>{invoice_data.get('buyer_building_no')}</cbc:BuildingNumber>
                <cbc:CitySubdivisionName>{invoice_data.get('buyer_district')}</cbc:CitySubdivisionName>
                <cbc:CityName>{invoice_data.get('buyer_city')}</cbc:CityName>
                <cbc:PostalZone>{invoice_data.get('buyer_postal_code')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:Name>Türkiye</cbc:Name>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cac:TaxScheme>
                    <cbc:Name>{invoice_data.get('buyer_tax_office')}</cbc:Name>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingCustomerParty>
    
    <!-- Vergi Toplamları -->
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="{invoice_data.get('currency_code', 'TRY')}">{invoice_data.get('total_tax_amount', '0.00')}</cbc:TaxAmount>
        {cls._build_tax_subtotals_xml(invoice_data.get('tax_subtotals', []))}
    </cac:TaxTotal>
    
    <!-- Yasal Para Birimi Toplamları -->
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="{invoice_data.get('currency_code', 'TRY')}">{invoice_data.get('line_extension_amount', '0.00')}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="{invoice_data.get('currency_code', 'TRY')}">{invoice_data.get('tax_exclusive_amount', '0.00')}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="{invoice_data.get('currency_code', 'TRY')}">{invoice_data.get('tax_inclusive_amount', '0.00')}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="{invoice_data.get('currency_code', 'TRY')}">{invoice_data.get('payable_amount', '0.00')}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    
    <!-- Fatura Kalemleri -->
    {cls._build_invoice_lines_xml(invoice_data.get('lines', []))}
</Invoice>"""
        
        return template
    
    @classmethod
    def build_despatch_xml(cls, despatch_data):
        """E-İrsaliye XML içeriği oluşturur"""
        # XML şablonu
        template = f"""<?xml version="1.0" encoding="UTF-8"?>
<DespatchAdvice xmlns="urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
                xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>TR1.2</cbc:CustomizationID>
    <cbc:ProfileID>DESPATCHADVICE</cbc:ProfileID>
    <cbc:ID>{despatch_data.get('despatch_number')}</cbc:ID>
    <cbc:UUID>{despatch_data.get('uuid', str(uuid.uuid4()))}</cbc:UUID>
    <cbc:IssueDate>{despatch_data.get('issue_date', datetime.now().strftime('%Y-%m-%d'))}</cbc:IssueDate>
    <cbc:IssueTime>{despatch_data.get('issue_time', datetime.now().strftime('%H:%M:%S'))}</cbc:IssueTime>
    <cbc:DespatchAdviceTypeCode>{despatch_data.get('despatch_type_code', 'SEVK')}</cbc:DespatchAdviceTypeCode>
    <cbc:Note>{despatch_data.get('note', '')}</cbc:Note>
    <cbc:LineCountNumeric>{len(despatch_data.get('lines', []))}</cbc:LineCountNumeric>
    
    <!-- Sipariş Referansı (varsa) -->
    {cls._build_order_reference_xml(despatch_data.get('order_reference'))}
    
    <!-- Sevkiyat Referansı (varsa) -->
    {cls._build_despatch_line_reference_xml(despatch_data.get('despatch_line_reference'))}
    
    <!-- Satıcı Bilgileri -->
    <cac:SellerSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="VKN">{settings.COMPANY_VKN}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>{settings.COMPANY_NAME}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{despatch_data.get('seller_street')}</cbc:StreetName>
                <cbc:BuildingNumber>{despatch_data.get('seller_building_no')}</cbc:BuildingNumber>
                <cbc:CitySubdivisionName>{despatch_data.get('seller_district')}</cbc:CitySubdivisionName>
                <cbc:CityName>{despatch_data.get('seller_city')}</cbc:CityName>
                <cbc:PostalZone>{despatch_data.get('seller_postal_code')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:Name>Türkiye</cbc:Name>
                </cac:Country>
            </cac:PostalAddress>
        </cac:Party>
    </cac:SellerSupplierParty>
    
    <!-- Alıcı Bilgileri -->
    <cac:BuyerCustomerParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID="VKN">{despatch_data.get('buyer_vkn')}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>{despatch_data.get('buyer_name')}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>{despatch_data.get('buyer_street')}</cbc:StreetName>
                <cbc:BuildingNumber>{despatch_data.get('buyer_building_no')}</cbc:BuildingNumber>
                <cbc:CitySubdivisionName>{despatch_data.get('buyer_district')}</cbc:CitySubdivisionName>
                <cbc:CityName>{despatch_data.get('buyer_city')}</cbc:CityName>
                <cbc:PostalZone>{despatch_data.get('buyer_postal_code')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:Name>Türkiye</cbc:Name>
                </cac:Country>
            </cac:PostalAddress>
        </cac:Party>
    </cac:BuyerCustomerParty>
    
    <!-- Sevkiyat Bilgileri -->
    <cac:Shipment>
        <cbc:ID>{despatch_data.get('shipment_id', str(uuid.uuid4()))}</cbc:ID>
        <cbc:HandlingCode>{despatch_data.get('handling_code', '')}</cbc:HandlingCode>
        <cbc:Information>{despatch_data.get('shipment_info', '')}</cbc:Information>
        <cbc:GrossWeightMeasure unitCode="KGM">{despatch_data.get('gross_weight', '0')}</cbc:GrossWeightMeasure>
        <cbc:NetWeightMeasure unitCode="KGM">{despatch_data.get('net_weight', '0')}</cbc:NetWeightMeasure>
        <cbc:TotalTransportHandlingUnitQuantity>{despatch_data.get('total_packages', '1')}</cbc:TotalTransportHandlingUnitQuantity>
        
        <!-- Sevkiyat Adresi -->
        <cac:ShipmentLocation>
            <cbc:ID>{despatch_data.get('delivery_location_id')}</cbc:ID>
            <cac:Address>
                <cbc:StreetName>{despatch_data.get('delivery_street')}</cbc:StreetName>
                <cbc:BuildingNumber>{despatch_data.get('delivery_building_no')}</cbc:BuildingNumber>
                <cbc:CitySubdivisionName>{despatch_data.get('delivery_district')}</cbc:CitySubdivisionName>
                <cbc:CityName>{despatch_data.get('delivery_city')}</cbc:CityName>
                <cbc:PostalZone>{despatch_data.get('delivery_postal_code')}</cbc:PostalZone>
                <cac:Country>
                    <cbc:Name>Türkiye</cbc:Name>
                </cac:Country>
            </cac:Address>
        </cac:ShipmentLocation>
        
        <!-- Taşıma Bilgileri -->
        <cac:TransportHandlingUnit>
            <cbc:ID>{despatch_data.get('transport_unit_id')}</cbc:ID>
            <cbc:TransportHandlingUnitTypeCode>{despatch_data.get('transport_type_code', '')}</cbc:TransportHandlingUnitTypeCode>
            <cbc:TotalPackageQuantity>{despatch_data.get('total_packages', '1')}</cbc:TotalPackageQuantity>
        </cac:TransportHandlingUnit>
    </cac:Shipment>
    
    <!-- İrsaliye Kalemleri -->
    {cls._build_despatch_lines_xml(despatch_data.get('lines', []))}
</DespatchAdvice>"""
        
        return template
    
    @classmethod
    def _build_tax_subtotals_xml(cls, tax_subtotals):
        """Vergi alt toplamları XML'i oluşturur"""
        if not tax_subtotals:
            return ""
        
        xml_parts = []
        for tax in tax_subtotals:
            xml_parts.append(f"""        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="{tax.get('currency_code', 'TRY')}">{tax.get('taxable_amount', '0.00')}</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="{tax.get('currency_code', 'TRY')}">{tax.get('tax_amount', '0.00')}</cbc:TaxAmount>
            <cbc:Percent>{tax.get('percent', '0')}</cbc:Percent>
            <cac:TaxCategory>
                <cbc:ID>{tax.get('category_id', '')}</cbc:ID>
                <cbc:Name>{tax.get('category_name', '')}</cbc:Name>
                <cac:TaxScheme>
                    <cbc:ID>{tax.get('scheme_id', '')}</cbc:ID>
                    <cbc:Name>{tax.get('scheme_name', '')}</cbc:Name>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>""")
        
        return "\n".join(xml_parts)
    
    @classmethod
    def _build_invoice_lines_xml(cls, lines):
        """Fatura kalemleri XML'i oluşturur"""
        if not lines:
            return ""
        
        xml_parts = []
        for line in lines:
            xml_parts.append(f"""    <cac:InvoiceLine>
        <cbc:ID>{line.get('id', '')}</cbc:ID>
        <cbc:InvoicedQuantity unitCode="{line.get('unit_code', 'C62')}">{line.get('quantity', '0')}</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="{line.get('currency_code', 'TRY')}">{line.get('line_extension_amount', '0.00')}</cbc:LineExtensionAmount>
        <cac:Item>
            <cbc:Name>{line.get('item_name', '')}</cbc:Name>
            <cbc:Description>{line.get('item_description', '')}</cbc:Description>
            <cbc:ModelName>{line.get('item_model', '')}</cbc:ModelName>
            <cbc:BrandName>{line.get('item_brand', '')}</cbc:BrandName>
            <cbc:ManufacturerName>{line.get('item_manufacturer', '')}</cbc:ManufacturerName>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="{line.get('currency_code', 'TRY')}">{line.get('price_amount', '0.00')}</cbc:PriceAmount>
        </cac:Price>
        <cac:TaxTotal>
            <cbc:TaxAmount currencyID="{line.get('currency_code', 'TRY')}">{line.get('tax_amount', '0.00')}</cbc:TaxAmount>
            {cls._build_tax_subtotals_xml(line.get('tax_subtotals', []))}
        </cac:TaxTotal>
    </cac:InvoiceLine>""")
        
        return "\n".join(xml_parts)
    
    @classmethod
    def _build_order_reference_xml(cls, order_ref):
        """Sipariş referansı XML'i oluşturur"""
        if not order_ref:
            return ""
        
        return f"""    <cac:OrderReference>
        <cbc:ID>{order_ref.get('id', '')}</cbc:ID>
        <cbc:IssueDate>{order_ref.get('issue_date', '')}</cbc:IssueDate>
    </cac:OrderReference>"""
    
    @classmethod
    def _build_despatch_line_reference_xml(cls, despatch_ref):
        """Sevkiyat referansı XML'i oluşturur"""
        if not despatch_ref:
            return ""
        
        return f"""    <cac:DespatchLineReference>
        <cbc:LineID>{despatch_ref.get('line_id', '')}</cbc:LineID>
    </cac:DespatchLineReference>"""
    
    @classmethod
    def _build_despatch_lines_xml(cls, lines):
        """İrsaliye kalemleri XML'i oluşturur"""
        if not lines:
            return ""
        
        xml_parts = []
        for line in lines:
            xml_parts.append(f"""    <cac:DespatchLine>
        <cbc:ID>{line.get('id', '')}</cbc:ID>
        <cbc:DeliveredQuantity unitCode="{line.get('unit_code', 'C62')}">{line.get('quantity', '0')}</cbc:DeliveredQuantity>
        <cac:Item>
            <cbc:Name>{line.get('item_name', '')}</cbc:Name>
            <cbc:Description>{line.get('item_description', '')}</cbc:Description>
            <cbc:ModelName>{line.get('item_model', '')}</cbc:ModelName>
            <cbc:BrandName>{line.get('item_brand', '')}</cbc:BrandName>
            <cbc:ManufacturerName>{line.get('item_manufacturer', '')}</cbc:ManufacturerName>
        </cac:Item>
    </cac:DespatchLine>""")
        
        return "\n".join(xml_parts) 