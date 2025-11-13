# Kanıta Dayalı Soru-Cevap (Grounded QA) Kılavuzu

Bu kılavuz, dış/yerel kaynakları bilgi tabanına (KB) ekleyip yalnızca alıntı içeren yanıtlar almanızı sağlar.

## İndeks Dosyası
- Varsayılan: `media/ai_kb/index.json`
- Değiştirmek için: `AI_KB_INDEX_PATH`

## Kaynak Ekleme
- URL'den ingest: `POST /ai-assistant/api/kb/ingest-urls/` body: `{ "urls": ["https://www.gib.gov.tr/"] }`
- İç doküman ingest: `POST /ai-assistant/api/kb/ingest-internal/`

## Soru Sor
- `POST /ai-assistant/api/qa/grounded/` body: `{ "query": "e-fatura nedir?" }`
- Yanıt: Sadece indeksten alıntılar ve `citations` listesi

## Güvenlik
- İçerik redaksiyonu: muhtemel hassas kalıplar `[REDACTED]` ile maskeleme
- robots.txt ve hız limiti gerçek ortamda dikkate alınmalıdır
