# FinAsis Games Modülü

Games modülü; finansal okuryazarlık, ticaret simülasyonu ve oyunlaştırma bileşenlerini içerir. Django uygulaması olarak çalışır, kanal (WebSocket) desteği ve çeşitli mini servisler barındırır.

## Dizin Yapısı

- `games/urls.py`: Modül URL yönlendirmeleri
  - `'' → views.index` (oyun listesi)
  - `'<int:game_id>/` → `views.detail`
  - `accounting/`, `trading/`, `investing/`, `social/`, `collection/`, `achievements/`, `inventory/`, `tax/`, `learning/`, `market/`
  - `trade-sim/` alt uygulaması ve `game_app/` alt modülü URL’leri
- `games/views.py`: Sayfa görünümleri (liste, detay ve konu başlıkları)
- `games/templates/games/`: Şablonlar (ör. `index.html`, `detail.html`, `home.html`)
- `games/game_engine.py`: Çekirdek oyun motoru/mekanikler
- `games/economy.py`, `financials.py`, `accounting.py`: Ekonomi/finans kuralları ve oyun içi işlemler
- `games/analytics.py`: Oyun içi analitikler
- `games/store.py`: Oyun içi mağaza/ödül sistemi
- `games/social.py`: Sosyal etkileşimler
- `games/achievements.py`: Başarımlar/rozetler
- `games/quests.py`: Görevler/senaryolar
- `games/notifications.py`: Bildirim altyapısı
- `games/security.py`: Güvenlik/kural kontrolleri
- `games/inventory.py`: Envanter yönetimi
- `games/learning.py`: Öğrenme/öğretici bileşenler
- `games/tasks.py`: Zamanlanmış işler (Celery/async senaryoları için)
- `games/routing.py`: Channels (WebSocket) routing
- `games/api/`: API uçları ve yardımcıları
- `games/forms.py`, `games/models.py`, `games/admin.py`, `games/tests/`: Django standartları
- `games/trade_sim/`: Ticaret simülasyonu alt-uygulaması
- `games/game_app/`: Oyun alt modülü (ek ekranlar/akışlar)

## Kurulum ve Çalıştırma

1) Bağımlılıklar (proje kökünde):
```
pip install -r requirements.txt
```

2) Veritabanı migrasyonları:
```
python manage.py migrate
```

3) Geliştirme sunucusu:
```
python manage.py runserver
```

Channels (WebSocket) kullanımı için ASGI yapılandırması projede hazırdır; üretimde ASGI sunucusu (daphne/uvicorn) tercih edin.

## URL’ler (özet)

- `GET /games/` → Oyun listesi (`games:index`)
- `GET /games/<id>/` → Oyun detay (`games:game_detail`)
- Konu sayfaları: `/games/accounting`, `/games/trading`, `/games/investing`, `/games/social`, `/games/collection`, `/games/achievements`, `/games/inventory`, `/games/tax`, `/games/learning`, `/games/market`
- Alt uygulamalar: `/games/trade-sim/`, `/games/game_app/`

Not: Bazı konu sayfaları için şablonlar yerelde yoksa `templates/games/` altında oluşturulmalıdır (örn. `accounting.html`, `trading.html`).

## Geliştirme Notları

- `app_name = 'games'` kullanılır; ters URL çözümlerinde `games:<name>` biçimini tercih edin.
- Şablon yolu kuralı: `templates/games/<sayfa>.html`.
- Statik dosyalar: `templates/games/static/` altındaki `css/js` dizinleri (proje STATICFILES ayarlarına tabidir).
- Oyun motoru ve simülasyon mantığı `game_engine.py` ve `trade_sim/` altında katmanlıdır; domain kurallarını ilgili modüllerde tutun (SRP).

## Test ve Kalite

- Testler: `python manage.py test` veya `pytest`
- Lint: `flake8`, format: `black` (varsa)

## Katkı

- Yeni ekran eklerken `urls.py → views.py → templates/` akışını izleyin.
- Oyun içi kuralları ayrı modüllerde (economy/financials/accounting) tutarak bağımlılıkları düşük seviyede tutun.