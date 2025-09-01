"""
Ortak ve şablon servis fonksiyonları (döviz, finansal skor, AI, gamification, blockchain, banka, e-fatura, beyanname).
Gerçek entegrasyonlar için ilgili modüllere taşınabilir.
"""

def fetch_exchange_rates(base_currency="TRY"):
    """Güncel döviz kurlarını çeker (stub). Yerel cache/ayar üzerinden döner."""
    # Basit sabit oranlar; gerçek entegrasyonda TCMB veya banka API'leri kullanılır
    rates = {
        "TRY": 1.0,
        "USD": 32.0,
        "EUR": 34.5,
        "GBP": 40.0,
    }
    return {k: v / rates.get(base_currency, 1.0) for k, v in rates.items()}

def calculate_financial_score(company):
    """Şirketin finansal skorunu hesaplar (şablon)."""
    pass

def suggest_accounting_entry(company, context):
    """Basit kural: açıklamada 'satış' geçerse 600/391 alacak ve 100/102 borç önerir."""
    text = (context or {}).get('description', '').lower()
    amount = (context or {}).get('amount', 0)
    if 'satış' in text or 'satis' in text:
        return [
            {"side": "D", "account_code": "100", "amount": amount},
            {"side": "C", "account_code": "600", "amount": amount / 1.2},
            {"side": "C", "account_code": "391", "amount": amount - (amount / 1.2)},
        ]
    return []

def analyze_financial_data(company, data):
    """Finansal verileri analiz eder ve öneriler sunar (şablon)."""
    pass

def award_badge(user, badge_type):
    """Kullanıcıya belirli bir rozet verir (şablon)."""
    pass

def increase_user_level(user):
    """Kullanıcının seviyesini artırır (şablon)."""
    pass

def hash_record(record):
    """Verilen kaydı hash'ler (şablon)."""
    pass

def verify_record_on_blockchain(record):
    """Kaydın blokzincirde doğruluğunu kontrol eder (şablon)."""
    pass

def fetch_bank_transactions(account):
    """Verilen banka hesabı için banka hareketlerini çeker (şablon)."""
    pass

def send_payment_to_bank(account, amount):
    """Banka hesabına ödeme gönderir (şablon)."""
    pass

def send_efatura(invoice):
    """Verilen faturayı e-Fatura sistemine gönderir (şablon)."""
    pass

def get_efatura_status(invoice):
    """Faturanın e-Fatura sistemindeki durumunu sorgular (şablon)."""
    pass

def suggest_kdv_declaration(company):
    """Şirket için KDV beyannamesi önerisi üretir (şablon)."""
    pass

def suggest_muhtasar_declaration(company):
    """Şirket için Muhtasar beyannamesi önerisi üretir (şablon)."""
    pass 