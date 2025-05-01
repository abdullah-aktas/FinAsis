# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü

Bu modül, FinAsis uygulamasının muhasebe işlemleriyle ilgili tüm fonksiyonları içerir.
Hesap planı, muhasebe fişleri, finansal tablolar ve muhasebe raporlamasını yönetir.

Özellikler:
----------
- Hesap planı yönetimi
- Muhasebe fişi oluşturma ve onaylama
- Günlük kayıtlar (Yevmiye defteri)
- Büyük defter 
- Mizan
- Bilanço ve gelir tablosu
- Maliyet muhasebesi
- Vergi beyannameleri

Kullanım:
--------
Bu modül şu şekilde kullanılabilir:
    from finance.accounting import accounts, vouchers, reports
    
    # Hesap planı işlemleri
    accounts.get_account('120.01.001')
    
    # Muhasebe fişi oluşturma
    voucher = vouchers.create_voucher(date=today, type='TAHSILAT')
    vouchers.add_voucher_line(voucher, debit_account='100.01', credit_account='120.01.001', amount=1000)
    
    # Raporlar
    reports.generate_trial_balance(start_date, end_date)

İlişkili Modüller:
----------------
- finance.banking    : Banka işlemleri
- apps.company            : Şirket bilgileri
- finance.einvoice   : E-Fatura işlemleri

Teknik Notlar:
------------
1. Muhasebe modülü GAAP ve IFRS standartlarına uygun olarak tasarlanmıştır.
2. Tek düzen hesap planı kullanılmaktadır.
3. Para birimleri için kesinlikle Decimal kullanılmalıdır.
"""

default_app_config = 'finance.accounting.apps.AccountingConfig' 