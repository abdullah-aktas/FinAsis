"""
Sabit değerler
"""

# Para birimleri
CURRENCIES = [
    ('TRY', 'Türk Lirası'),
    ('USD', 'Amerikan Doları'),
    ('EUR', 'Euro'),
    ('GBP', 'İngiliz Sterlini'),
]

# Fatura türleri
INVOICE_TYPES = [
    ('SALE', 'Satış Faturası'),
    ('PURCHASE', 'Alış Faturası'),
    ('REFUND', 'İade Faturası'),
]

# Ödeme yöntemleri
PAYMENT_METHODS = [
    ('CASH', 'Nakit'),
    ('CREDIT_CARD', 'Kredi Kartı'),
    ('BANK_TRANSFER', 'Banka Transferi'),
    ('CHECK', 'Çek'),
]

# Müşteri türleri
CUSTOMER_TYPES = [
    ('INDIVIDUAL', 'Bireysel'),
    ('CORPORATE', 'Kurumsal'),
]

# Belge türleri
DOCUMENT_TYPES = [
    ('INVOICE', 'Fatura'),
    ('RECEIPT', 'Fiş'),
    ('CONTRACT', 'Sözleşme'),
    ('REPORT', 'Rapor'),
]

# Kullanıcı rolleri
USER_ROLES = [
    ('ADMIN', 'Yönetici'),
    ('MANAGER', 'Müdür'),
    ('ACCOUNTANT', 'Muhasebeci'),
    ('USER', 'Kullanıcı'),
]

# İşlem durumları
TRANSACTION_STATUS = [
    ('PENDING', 'Beklemede'),
    ('COMPLETED', 'Tamamlandı'),
    ('CANCELLED', 'İptal Edildi'),
    ('FAILED', 'Başarısız'),
]

# Bildirim türleri
NOTIFICATION_TYPES = [
    ('SYSTEM', 'Sistem'),
    ('INVOICE', 'Fatura'),
    ('PAYMENT', 'Ödeme'),
    ('REPORT', 'Rapor'),
]

# Dosya türleri
FILE_TYPES = [
    ('PDF', 'PDF'),
    ('EXCEL', 'Excel'),
    ('WORD', 'Word'),
    ('IMAGE', 'Resim'),
] 