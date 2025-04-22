# FinAsis AI Asistan Modülü

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

FinAsis AI Asistan, kullanıcılara finansal işlemlerinde yardımcı olan, doğal dil işleme yeteneklerine sahip yapay zeka destekli bir modüldür. Bu modül, kullanıcıların finansal verilerini analiz eder, öneriler sunar ve finansal kararlarında yardımcı olur.

## 🎯 Özellikler

- Doğal dil ile finansal analiz
- Otomatik fatura kategorizasyonu
- Finansal tahminler ve öngörüler
- Kişiselleştirilmiş finansal öneriler
- Çoklu dil desteği
- Sesli komut desteği

## 🔧 Kurulum

### Gereksinimler
- Python 3.9+
- TensorFlow 2.8+
- spaCy 3.2+
- Transformers 4.15+
- CUDA destekli GPU (önerilen)

### Kurulum Adımları
1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements/ai_requirements.txt
```

2. Dil modellerini indirin:
```bash
python -m spacy download tr_core_news_lg
python -m spacy download en_core_web_lg
```

3. AI servisini başlatın:
```bash
python manage.py run_ai_service
```

## 🛠️ Yapılandırma

### API Anahtarları
```python
AI_API_KEY = "your-api-key"
AI_MODEL_PATH = "models/financial_analysis"
AI_LANGUAGE = "tr"  # veya "en"
```

### Model Parametreleri
```python
AI_CONFIG = {
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.5
}
```

## 📊 Kullanım

### Temel Komutlar
```python
from finasis.ai import AIAssistant

# Asistan örneği oluştur
assistant = AIAssistant()

# Finansal analiz yap
analysis = assistant.analyze_finances(user_id=1)

# Öneri al
suggestions = assistant.get_suggestions(user_id=1)

# Tahmin yap
forecast = assistant.forecast_finances(user_id=1, period="monthly")
```

### API Endpoints
- `POST /api/ai/analyze` - Finansal analiz
- `POST /api/ai/suggest` - Öneriler
- `POST /api/ai/forecast` - Tahminler
- `POST /api/ai/chat` - Sohbet

## 🔍 Örnek Kullanımlar

### Finansal Analiz
```python
response = assistant.analyze_finances(
    user_id=1,
    period="last_month",
    categories=["income", "expenses"]
)
```

### Öneri Sistemi
```python
suggestions = assistant.get_suggestions(
    user_id=1,
    context="savings",
    limit=5
)
```

### Tahmin Sistemi
```python
forecast = assistant.forecast_finances(
    user_id=1,
    period="next_quarter",
    confidence=0.95
)
```

## 🧪 Test

### Test Ortamı
```bash
python manage.py test ai.tests
```

### Test Kapsamı
- Doğal dil işleme
- Finansal analiz
- Tahmin modelleri
- Öneri sistemi
- API entegrasyonları

## 📈 Performans

### Ölçümler
- Yanıt süresi: < 2 saniye
- Doğruluk oranı: > 95%
- Model boyutu: < 500MB
- Bellek kullanımı: < 2GB

### Optimizasyon
- Model sıkıştırma
- Önbellekleme
- Paralel işleme
- GPU hızlandırma

## 🔒 Güvenlik

### Veri Güvenliği
- Veri şifreleme
- Anonimleştirme
- Erişim kontrolü
- Denetim kayıtları

### API Güvenliği
- API anahtarı doğrulama
- Rate limiting
- IP kısıtlamaları
- SSL/TLS

## 📚 Dokümantasyon

### API Dokümantasyonu
- [API Referansı](api.md)
- [Örnek Kodlar](examples.md)
- [Hata Kodları](errors.md)

### Kullanıcı Kılavuzu
- [Başlangıç Kılavuzu](getting_started.md)
- [Gelişmiş Özellikler](advanced_features.md)
- [SSS](faq.md)

## 🤝 Katkıda Bulunma

### Geliştirme Kuralları
1. PEP 8 standartlarına uyun
2. Birim testleri yazın
3. Dokümantasyonu güncelleyin
4. Pull request açın

### Kod İnceleme Süreci
1. Kod incelemesi
2. Test sonuçları
3. Performans değerlendirmesi
4. Onay ve birleştirme

## 📞 Destek

### İletişim
- E-posta: ai-support@finasis.com
- Slack: #ai-support
- GitHub Issues

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Uptime: %99.9 