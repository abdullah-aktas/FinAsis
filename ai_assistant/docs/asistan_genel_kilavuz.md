# FinAsis Yapay Zeka Asistanı – Genel Kullanım Kılavuzu

Bu kılavuz, FinAsis Yapay Zeka Asistanı'nın sunduğu temel yetenekleri (soru-cevap, öneriler, fiş kesimi, sesli komut, bilgi tabanı) hızlıca kullanmanız için hazırlanmıştır.

## Özellikler
- Doğal dille soru-cevap (yerel NLP)
- Öneriler: portföy, yatırım, risk ve KOBİ işletme sağlığı odaklı içgörüler
- Fiş kesimi: metin, ses veya belgeden TDHP uyumlu fiş önizleme ve onay
- Sesli komut: Tarayıcıdan kayıt + yerel STT (Vosk)
- Kanıta dayalı Soru-Cevap (Grounded QA): İndekslenmiş kaynaklardan alıntı ile yanıt

## Hızlı Başlangıç
- Web arayüzü:
  - Sesli komut demosu: `/ai-assistant/voice/`
  - Asistan ile fiş kesimi: `/ai-assistant/voucher/assistant/`
- API uçları:
  - NLP sor: `POST /ai-assistant/api/ask/` body: `{ "question": "..." }`
  - Sesten NLP: `POST /ai-assistant/api/voice/recognize/` form `file=@sample.wav`
  - Fiş: metin/ses/belge → `.../voucher/from-text|from-voice|from-document/`
  - Fiş onayı: `.../voucher/confirm/`
  - KB URL ingest: `POST .../kb/ingest-urls/` body: `{ urls: ["..."] }`
  - KB iç doküman ingest: `POST .../kb/ingest-internal/`

## İzinler ve Güvenlik
- Tüm uçlar kimlik doğrulaması gerektirir (aksine belirtilmedikçe).
- STT model yolu: `AI_STT_MODEL_PATH` veya `VOSK_MODEL_PATH`
- Bilgi tabanı dosyası: `AI_KB_INDEX_PATH` (varsayılan `media/ai_kb/index.json`)

## Sorun Giderme
- STT hatası: model yolu boş → ortam değişkeni ayarlayın.
- OCR doğruluğu düşük: görüntü kalitesini iyileştirin.
- KB yanıtı boş: önce kaynakları indekse ekleyin.
