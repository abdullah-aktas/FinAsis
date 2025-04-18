# -*- coding: utf-8 -*-
"""
FinAsis Finans Modülleri

Bu paket, FinAsis uygulamasının finans işlemleriyle ilgili tüm modüllerini içerir.
Muhasebe, bankacılık, çek yönetimi ve e-fatura gibi finansal işlemleri kapsar.

Alt Modüller:
------------
/accounting   - Muhasebe işlemleri, hesap planı, finansal tablolar
/banking      - Banka entegrasyonları, banka hesapları ve işlemleri
/checks       - Çek/senet takibi ve yönetimi
/einvoice     - E-Fatura/E-Arşiv entegrasyonu ve yönetimi

Kullanım:
--------
Bu modüller doğrudan import edilebilir:
    from apps.finance.accounting import ledger
    from apps.finance.banking import transactions
    from apps.finance.einvoice import generate_invoice

İlişkili Modüller:
----------------
- apps.core          : Temel sistem fonksiyonları
- apps.company       : Şirket bilgileri (finans işlemleri için gerekli)
- apps.integration   : Dış sistem entegrasyonları

Teknik Notlar:
------------
1. Her finans işlemi için audit trail kaydı oluşturulur.
2. Para birimleri için Decimal kullanılır, float kullanılmaz.
3. Tüm finansal işlemler transactional (atomik) olmalıdır.
"""

# Django yapılandırmasını basitleştirmek için paket 
# yapısını auto-discovery mekanizmasıyla uyumlu hale getiriyoruz.
default_app_config = 'apps.finance.FinanceConfig' 