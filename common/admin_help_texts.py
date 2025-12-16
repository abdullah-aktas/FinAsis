# -*- coding: utf-8 -*-
"""
Admin Panel Yardım Metinleri
Her model için kullanım kılavuzu ve açıklamalar
"""

HELP_TEXTS = {
    # Accounts
    'accounts.customuser': {
        'username': 'Kullanıcı adı. Benzersiz olmalıdır. Sadece harf, rakam ve @/./+/-/_ karakterleri kullanılabilir.',
        'email': 'E-posta adresi. Benzersiz olmalıdır. Şifre sıfırlama ve bildirimler için kullanılır.',
        'is_staff': 'Admin paneline erişim yetkisi. True ise kullanıcı admin paneline giriş yapabilir.',
        'is_superuser': 'Tüm yetkilere sahip kullanıcı. True ise kullanıcı tüm işlemleri yapabilir.',
        'is_active': 'Kullanıcı aktif mi? False yapılırsa kullanıcı giriş yapamaz.',
        'company': 'Kullanıcının bağlı olduğu şirket. Şirket bilgilerine erişim için gereklidir.',
        'user_type': 'Kullanıcı tipi. KOBİ Sahibi, Muhasebeci, Finans Yöneticisi vb.',
    },
    'accounts.userrole': {
        'name': 'Rol adı. Örn: "Muhasebeci", "Finans Yöneticisi"',
        'hierarchy_level': 'Hiyerarşi seviyesi. 0 = En yüksek yetki. Sayı arttıkça yetki azalır.',
        'permissions': 'Rol yetkileri. Bu role sahip kullanıcılar bu yetkilere sahip olur.',
        'is_active': 'Rol aktif mi? Pasif roller kullanıcılara atanamaz.',
    },
    'accounts.achievement': {
        'name': 'Başarım adı. Kullanıcılara gösterilecek isim.',
        'code': 'Başarım kodu. Sistem içinde kullanılacak benzersiz kod.',
        'category': 'Başarım kategorisi. Oyun, Eğitim, Finans vb.',
        'points': 'Başarım puanı. Kullanıcı bu başarımı kazandığında alacağı puan.',
        'is_active': 'Başarım aktif mi? Pasif başarımlar kullanıcılara gösterilmez.',
    },
    'accounts.usersettings': {
        'theme': 'Kullanıcı arayüz teması. Açık, Koyu, Otomatik.',
        'language': 'Kullanıcı dil tercihi. tr-TR, en-US vb.',
        'timezone': 'Saat dilimi. Örn: Europe/Istanbul',
        'email_notifications': 'E-posta bildirimleri açık mı?',
        'two_factor_enabled': 'İki faktörlü kimlik doğrulama aktif mi?',
    },
    
    # Accounting
    'accounting.company': {
        'name': 'Şirket adı. Resmi şirket adı.',
        'tax_number': 'Vergi numarası. Benzersiz olmalıdır. GİB sisteminde kullanılır.',
        'trade_name': 'Ticari unvan. Ticaret sicilinde kayıtlı unvan.',
        'sector': 'Sektör. Şirketin faaliyet gösterdiği sektör.',
        'address': 'Şirket adresi. Fatura ve resmi belgelerde kullanılır.',
    },
    'accounting.invoice': {
        'invoice_number': 'Fatura numarası. Benzersiz olmalıdır. E-Fatura sisteminde kullanılır.',
        'invoice_date': 'Fatura tarihi. Faturanın düzenlendiği tarih.',
        'customer': 'Müşteri. Faturayı alan müşteri.',
        'total_amount': 'Toplam tutar. KDV dahil toplam tutar.',
        'status': 'Fatura durumu. Taslak, Gönderildi, Ödendi, İptal.',
    },
    'accounting.customer': {
        'name': 'Müşteri adı. Şirket veya kişi adı.',
        'tax_number': 'Vergi numarası. Tüzel kişiler için zorunludur.',
        'email': 'E-posta adresi. Fatura gönderimi için kullanılır.',
        'phone': 'Telefon numarası. İletişim için.',
    },
    
    # Finance
    'finance.transaction': {
        'account': 'İşlemin yapıldığı hesap. Nakit, Banka, Kredi vb.',
        'amount': 'İşlem tutarı. Pozitif değer.',
        'transaction_type': 'İşlem tipi. Gelir, Gider, Transfer.',
        'date': 'İşlem tarihi. İşlemin gerçekleştiği tarih.',
        'description': 'İşlem açıklaması. İşlemin detaylı açıklaması.',
    },
    'finance.account': {
        'name': 'Hesap adı. Örn: "Ana Kasa", "İş Bankası TL Hesabı"',
        'account_type': 'Hesap tipi. Nakit, Banka, Kredi, Yatırım vb.',
        'balance': 'Hesap bakiyesi. Otomatik hesaplanır, manuel değiştirmeyin.',
        'currency': 'Para birimi. TRY, USD, EUR vb.',
        'is_active': 'Hesap aktif mi? Pasif hesaplar işlemlerde görünmez.',
    },
    'finance.budget': {
        'name': 'Bütçe adı. Örn: "2025 Pazarlama Bütçesi"',
        'amount': 'Bütçe tutarı. Toplam bütçe miktarı.',
        'period': 'Bütçe dönemi. Aylık, Yıllık, Özel.',
        'start_date': 'Bütçe başlangıç tarihi.',
        'end_date': 'Bütçe bitiş tarihi.',
        'spent_amount': 'Harcanan tutar. Otomatik hesaplanır.',
    },
    
    # Games - TradeSim
    'trade_sim.tournament': {
        'name': 'Turnuva adı. Kullanıcılara gösterilecek isim.',
        'description': 'Turnuva açıklaması. Kurallar ve ödüller hakkında bilgi.',
        'start_time': 'Turnuva başlangıç zamanı. Tarih ve saat.',
        'end_time': 'Turnuva bitiş zamanı. Tarih ve saat.',
        'prize_pool': 'Ödül havuzu. JSON formatında. Örn: {"coins": 50000, "badge": "champion"}',
        'is_active': 'Turnuva aktif mi? Pasif turnuvalar görünmez.',
    },
    'trade_sim.character': {
        'user': 'Karakterin sahibi olan kullanıcı.',
        'name': 'Karakter adı. Oyunda görünecek isim.',
        'city': 'Karakterin bulunduğu şehir. Başlangıç şehri.',
        'score': 'Karakter skoru. Ticaret işlemlerinden kazanılan puan.',
        'level': 'Karakter seviyesi. XP biriktikçe artar.',
        'skills': 'Karakter becerileri. JSON formatında. Örn: {"ticaret": 5, "pazarlık": 3}',
    },
    'trade_sim.city': {
        'name': 'Şehir adı. Örn: "İstanbul", "Ankara"',
        'market_size': 'Pazar büyüklüğü. Şehrin ticaret potansiyeli.',
        'sectors': 'Şehir sektörleri. JSON formatında. Örn: ["gıda", "tekstil", "teknoloji"]',
        'neighbors': 'Komşu şehirler. Ticaret rotaları için.',
    },
    'trade_sim.product': {
        'name': 'Ürün adı. Örn: "Buğday", "Pamuk"',
        'category': 'Ürün kategorisi. tarım, gıda, tekstil vb.',
        'base_price': 'Temel fiyat. Ürünün standart fiyatı.',
        'unit': 'Birim. kg, adet, litre vb.',
    },
    
    # AI Assistant
    'ai_assistant.aimodel': {
        'name': 'Model adı. Örn: "RiskScoringModel", "ChatAssistantModel"',
        'model_type': 'Model tipi. financial, chat, prediction.',
        'version': 'Model versiyonu. Örn: "v1.0", "20250115"',
        'accuracy': 'Model doğruluk oranı. 0.0 - 1.0 arası.',
        'is_active': 'Model aktif mi? Sadece aktif modeller kullanılır.',
        'parameters': 'Model parametreleri. JSON formatında.',
    },
}

def get_help_text(app_label, model_name, field_name):
    """Model alanı için yardım metni döndürür"""
    key = f'{app_label}.{model_name}'
    return HELP_TEXTS.get(key, {}).get(field_name, '')

def get_model_help_text(app_label, model_name):
    """Model için tüm yardım metinlerini döndürür"""
    key = f'{app_label}.{model_name}'
    return HELP_TEXTS.get(key, {})

