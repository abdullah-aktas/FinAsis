# Asistan ile Fiş Kesme Kılavuzu

Bu kılavuz, metin, ses veya belge üzerinden TDHP uyumlu fiş oluşturmayı adım adım açıklar.

## Web Arayüzü (Önerilir)
- Adres: `/ai-assistant/voucher/assistant/`
- Adımlar:
  1) Metin, ses veya belge sekmesini kullanarak önizleme oluşturun.
  2) Satırları kontrol edin (hesap, açıklama, borç/alacak).
  3) "Onayla ve Oluştur" ile deftere işleyin.

## API Uçları
- Metin → Önizleme: `POST /ai-assistant/api/voucher/from-text/`
  - Body: `{ "text": "02.10.2025 akaryakıt 1.250 TL, kasa çıkış, KDV %20" }`
- Ses → Önizleme: `POST /ai-assistant/api/voucher/from-voice/` form `file=@sample.wav`
- Belge → Önizleme: `POST /ai-assistant/api/voucher/from-document/` form `file=@fatura.jpg`
- Onay: `POST /ai-assistant/api/voucher/confirm/`
  - Body: `{ "mapped": { "date": "2025-10-02", "reference": "REF-001", "total": "1250.00", "lines": [{"account": "100", "description": "kasa çıkışı", "debit": "0", "credit": "1250"}, {"account": "760", "description": "akaryakıt", "debit": "1136.36", "credit": "0"}, {"account": "391", "description": "KDV %20", "debit": "113.64", "credit": "0"}] } }`

## İpuçları
- STT için `AI_STT_MODEL_PATH` veya `VOSK_MODEL_PATH` gereklidir.
- Hesap çözümü şirketin hesap planına göre yapılır; kodlar eşleşmezse uyarı gelir.
- Kuralları (AutoBookingRule) kullanarak tekrar eden belgeleri otomatikleştirebilirsiniz.