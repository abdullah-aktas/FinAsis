# Sesli Komut Kılavuzu

Bu kılavuz, yerel STT (Vosk) ile ses → yazı dönüştürme ve asistanla etkileşimi açıklar.

## Demo Sayfası
- Adres: `/ai-assistant/voice/`
- Adımlar: Mikrofonu başlat → kaydı durdur → "Kaydı Gönder" → metin ve NLP sonucu görünür.

## API
- `POST /ai-assistant/api/voice/recognize/` → form-data `file=@sample.wav`
- Yanıt: `{ "text": "...", "result": { ... } }`

## Kurulum
- Vosk model yolu: `AI_STT_MODEL_PATH` veya `VOSK_MODEL_PATH`
- Format notu: Tarayıcılar çoğunlukla WebM/Opus üretir. Sunucu WAV bekliyorsa dönüştürme gerekir.

## Sorun Giderme
- Model yolu yok: Ortam değişkenini tanımlayın.
- Ses anlaşılmıyor: Gürültüsüz ortam ve daha net kayıt deneyin.
