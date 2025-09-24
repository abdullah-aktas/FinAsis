# TradeSim Uygulama Rehberi

Bu rehber, TradeSim oyununun MVP sürümünü tamamlamanız için adım adım bir plan sunar. Amaç: gerçek zamanlıya yakın fiyat akışıyla (önce basit anlık/polling), temel emir yerleştirme, anında eşleşme, pozisyon takibi ve PnL hesapları.

## 1) Mimari ve Veri Modeli

Önerilen modeller (`src/apps/games/game_app/models.py`):

- Order
  - user (FK, opsiyonel: anonim/demo için null olabilir)
  - symbol (Char)
  - side (choices: BUY/SELL)
  - qty (Decimal/Integer)
  - price (Decimal, market emri için null bırakılabilir)
  - status (NEW, FILLED, CANCELED)
  - created_at

- Trade
  - user (FK)
  - symbol (Char)
  - side (BUY/SELL)
  - qty (Decimal/Integer)
  - price (Decimal)
  - executed_at
  - order (FK -> Order)

- Position
  - user (FK)
  - symbol (Char)
  - qty (Decimal/Integer)
  - avg_price (Decimal)
  - updated_at

- Portfolio (opsiyonel)
  - user (FK)
  - cash (Decimal)
  - last_equity (cached)

Notlar:
- MVP için margin ya da kaldıraç yok. Nakit kısıtını isterseniz `Portfolio.cash` ile kontrol edebilirsiniz.
- Market emirleri mevcut son fiyattan anında doluyor.

## 2) Fiyat Akışı (Mock)

İlk aşamada periyodik fiyat üretimi yeterli:
- `services/prices.py` içinde basit bir fiyat üretici yazın (ör. random walk; başlangıç 100.00, her tick ±0.1–0.5).
- REST polling: `GET /games/game_app/api/prices/?symbol=ABC&n=50` son N tick döndürsün.
- İleride Django Channels ile `ws://.../tradesim/` üstünden push yapılabilir.

## 3) URL’ler ve Görünümler

`src/apps/games/game_app/urls.py` (zaten `tradesim/` var). Şu API uçlarını ekleyin:

- `POST /games/game_app/api/orders/` → Emir oluşturma
- `GET /games/game_app/api/state/` → Kullanıcı oyuna ait durum (positions, open orders, recent trades, cash)
- `GET /games/game_app/api/prices/` → Fiyatlar (symbol bazlı, son N tick)

Örnek DRF View'lar (öneri):

- PlaceOrderAPIView (POST)
  - Payload: `{ symbol, side, qty, type=market|limit, price? }`
  - İşleyiş (MVP):
    - Market ise: son fiyattan fill et → Trade yarat, Position güncelle, Order.FILLED
    - Limit ise: şimdilik "hemen eşleşti" varsayabilirsiniz veya basit kural (örn. last_price <= limit_buy fiyatı ise fill)
  - Dönüş: güncel `state` ya da `order` detayları

- GameStateAPIView (GET)
  - Döndürsün: positions, open_orders, recent_trades, cash, total_equity, unrealized_pnl (symbol bazında)

- PricesAPIView (GET)
  - Param: symbol, n
  - Döndürsün: `[ { t, price }, ... ]`

## 4) Eşleşme ve PnL Kuralları (MVP)

- Fill (Market): son fiyat = `last_price(symbol)`
- Pozisyon güncelleme:
  - BUY: `new_avg = (old_qty*old_avg + buy_qty*price) / (old_qty + buy_qty)`
  - SELL: realized PnL = `(sell_price - avg_price) * sell_qty`, qty azaltılır.
- Unrealized PnL = `(last_price - avg_price) * open_qty`
- Total Equity = `cash + Σ(open_qty * last_price)`

## 5) Arayüz (Template + JS)

- `tradesim.html` (mevcut sayfaya ek ya da yenileme):
  - Sol panel: Chart.js grafiği (son fiyatlar), sembol seçimi (ABC/XYZ).
  - Sağ panel: Emir paneli (BUY/SELL toggle, qty input, market/limit, price input), Submit ile `POST /api/orders/`.
  - Alt bölüm: Positions tablosu (symbol, qty, avg, last, UPNL), Trades tablosu (time, side, price, qty).

- JS tarafı:
  - Her 1–2 sn’de bir `GET /api/prices/` ve `GET /api/state/` çek.
  - Chart.js datasını güncelle; UPNL/Equity değerlerini renklendir (pozitif/negatif).

## 6) Basit Güvenlik ve Sınırlar

- Demo modunda anonim kullanıcıyı session id ile eşleştirebilirsiniz (gerçek kullanıcı değilse).
- Rate limit (basit): istek başına min 200–500ms gecikme, çok hızlı POST’u engellemek için.

## 7) Test Senaryoları

- `GET tradesim/` 200 döner, sayfa ana bileşenleri içerir ("Buy", "Sell" butonları gibi).
- `POST /api/orders/` bir market BUY → Position.qty artar; Trade oluşur; Order.FILLED.
- `POST /api/orders/` market SELL → qty düşer; realized PnL hesaplanır.
- `GET /api/state/` positions, trades ve pnlleri döndürür; hesaplar beklenen değerde.
- Prices endpoint JSON şeması tutarlı; N=50 ile 50 nokta döner.

## 8) Adım Adım Yol Haritası

1) Modelleri ve migrations oluşturun; admin’e ekleyin (hızlı kontrol için).
2) Mock fiyat servisini yazın ve Prices endpointini bağlayın.
3) Emir yerleştirme (market) ve anında fill + pozisyon güncelleme.
4) Game state endpointini bağlayın; UPNL ve equity hesaplarını doğrulayın.
5) Template + Chart.js + fetch ile polling; tablo ve PnL renkleri.
6) (Opsiyonel) Limit emirleri, kısmi eşleşme, WebSocket canlı akış.
7) (Opsiyonel) Leaderboard ve günlük/haftalık skor panosu.

## 9) Ek İpuçları

- Para birimi ve hassasiyet için Decimal kullanın; `quantize` ile 2 ondalık.
- Zaman damgaları için timezone-aware `now()` kullanın.
- Semboller sabit liste olabilir (ABC, XYZ) ya da konfigden gelebilir.

---
Bu MVP tamamlandığında, kullanıcılar temel al/sat işlemleri yapabilir, pozisyonlarını ve PnL’lerini canlı takip edebilir. Sonrasında limit emirleri, stop’lar, canlı yayın (WS) ve leaderboards ile zenginleştirebilirsiniz.
