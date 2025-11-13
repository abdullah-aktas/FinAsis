# TradeSim - Ticaret Simülasyonu Oyunu

## 🎮 Genel Bakış

TradeSim, FinAsis platformunda entegre edilmiş, eğitici ve eğlenceli bir ticaret simülasyonu oyunudur. Kullanıcılar farklı şehirler arasında ürün alım-satımı yaparak kar elde eder ve ticaret becerilerini geliştirir.

## ✨ Özellikler

### 🎯 Oyun Mekanikleri
- **Şehirler Arası Ticaret**: 5+ farklı şehir arasında seyahat edin
- **Dinamik Pazar Sistemi**: Her şehirde farklı fiyatlarla ürün alım-satımı
- **Envanter Yönetimi**: 1000 kg kapasiteli envanter sistemi
- **Para Yönetimi**: Gerçekçi alım-satım ve seyahat maliyetleri
- **Zorluk Seviyeleri**: Farklı zorluk seçenekleri ile oynanabilirlik

### 🎨 Modern UI/UX
- **Mobile-First Responsive**: Tüm cihazlarda mükemmel çalışır
- **FinAsis Marka Renkleri**: `#0AAE94` ana renk ile tutarlı tasarım
- **Animasyonlu Geçişler**: Smooth fade ve slide animasyonları
- **Tam Ekran Modu**: ESC veya F tuşu ile oyun modunu değiştir
- **Real-time Bildirimler**: Toast mesajlar ile anlık geri bildirim

### 💾 Backend Entegrasyonu
- **Character-Based**: Her kullanıcının kendi karakteri ve envanteri
- **API-Driven**: RESTful API'ler ile backend iletişimi
- **Persistent Data**: Database'de saklanır, LocalStorage yedek
- **Real-time Updates**: Her işlem backend'e kaydedilir

## 🚀 Kurulum ve Test

### Gereksinimler
```bash
# Veritabanında şehir ve ürün seed data'sı olmalı
```

### Django Shell ile Test Data Oluşturma

```python
python manage.py shell

from src.apps.games.trade_sim.models import City, Product, CityMarket

# Şehirler oluştur
cities_data = [
    {'name': 'İstanbul', 'description': 'Büyük şehir', 'market_size': 1000, 'coordinates': {'x': 0, 'y': 0}},
    {'name': 'Ankara', 'description': 'Başkent', 'market_size': 850, 'coordinates': {'x': 100, 'y': 50}},
    {'name': 'İzmir', 'description': 'Ege incisi', 'market_size': 560, 'coordinates': {'x': -50, 'y': -30}},
    {'name': 'Bursa', 'description': 'Yeşil şehir', 'market_size': 240, 'coordinates': {'x': 20, 'y': 20}},
    {'name': 'Antalya', 'description': 'Turizm merkezi', 'market_size': 720, 'coordinates': {'x': -30, 'y': -50}},
]

for city_data in cities_data:
    City.objects.get_or_create(name=city_data['name'], defaults=city_data)

# Ürünler oluştur
products_data = [
    {'name': 'Buğday', 'description': 'Temel gıda ürünü', 'base_price': 28, 'unit': 'kg', 'category': 'gıda'},
    {'name': 'Elma', 'description': 'Taze meyve', 'base_price': 45, 'unit': 'kg', 'category': 'meyve'},
    {'name': 'Ekmek', 'description': 'Günlük ekmek', 'base_price': 12, 'unit': 'adet', 'category': 'gıda'},
    {'name': 'Peynir', 'description': 'Süt ürünü', 'base_price': 180, 'unit': 'kg', 'category': 'süt'},
    {'name': 'Kahve', 'description': 'Filtre kahve', 'base_price': 320, 'unit': 'kg', 'category': 'içecek'},
    {'name': 'Balık', 'description': 'Taze balık', 'base_price': 95, 'unit': 'kg', 'category': 'protein'},
]

for product_data in products_data:
    Product.objects.get_or_create(name=product_data['name'], defaults=product_data)

# Her şehir için pazar oluştur
import random
for city in City.objects.all():
    for product in Product.objects.all():
        price_variation = random.uniform(0.8, 1.2)  # %20 fiyat varyasyonu
        price = int(product.base_price * price_variation)
        supply = random.randint(100, 2000)
        demand = random.randint(50, 150)
        
        CityMarket.objects.get_or_create(
            city=city, 
            product=product,
            defaults={
                'price': price,
                'supply': supply,
                'demand': demand
            }
        )

print("✅ Test data oluşturuldu!")
```

### Character Başlangıç Parası

Yeni karakterler otomatik oluşturulur ancak başlangıç parası (`score`) varsayılan olarak 0'dır. Manuel olarak ayarlamak için:

```python
from src.apps.games.trade_sim.models import Character

# Tüm karakterlere 10000 başlangıç parası ver
Character.objects.all().update(score=10000)

# Veya belirli bir kullanıcı için
user = User.objects.get(username='test_user')
character = Character.objects.get(user=user)
character.score = 10000
character.save()
```

## 🎯 URL Yapısı

```
/games/trade-sim/start/          # Zorluk seçimi ve oyun başlatma
/games/trade-sim/play/           # Ana oyun ekranı
/games/trade-sim/leaderboard/    # Liderlik tablosu
/games/trade-sim/stats/          # İstatistikler
```

### API Endpoints

```
POST /games/trade-sim/market-trade/    # Alım-satım işlemi
POST /games/trade-sim/change-city/      # Şehir değiştirme
GET  /games/trade-sim/cities/           # Şehir listesi
GET  /games/trade-sim/products/         # Ürün listesi
GET  /games/trade-sim/city-markets/{id}/  # Şehir pazarı
```

## 🎮 Oynanış

1. **Oyunu Başlatma**
   - `/games/trade-sim/start/` adresinden zorluk seviyesi seçin
   - Oyun otomatik olarak başlar

2. **Ticaret Yapma**
   - Pazar sekmesinden ürün seçin
   - "Al" veya "Sat" butonuna tıklayın
   - Miktar girin ve onaylayın
   - Paranız ve envanteriniz güncellenir

3. **Şehir Değiştirme**
   - Sol panelden başka bir şehir seçin
   - Seyahat maliyetini onaylayın
   - Yeni şehrin pazarı yüklenir

4. **Oyunu Kaydetme**
   - Oyun otomatik kaydedilir (backend + localStorage)
   - Manuel kayıt: "💾 Kaydet" butonu

## 📱 Mobil Kullanım

- **Responsive Grid**: Mobilde tek sütun, tablet'te iki, desktop'ta üç sütun
- **Bottom Action Bar**: Mobilde altta sabit aksiyon çubuğu
- **Touch Optimized**: Tüm butonlar touch-friendly
- **Swipe Cities**: Şehirler yatay kaydırma ile gezinilebilir
- **Modal Envanter**: Mobilde envanter modal olarak açılır

## 🎨 Tasarım Sistemi

### Renkler (FinAsis Brand)
```css
--fin-primary: #0AAE94       /* Ana marka rengi */
--fin-primary-dark: #007a5e  /* Hover durumları */
--fin-secondary: #009873     /* İkincil renk */
--fin-success: #10b981       /* Başarı mesajları */
--fin-danger: #ef4444        /* Hata mesajları */
--fin-warning: #f59e0b       /* Uyarı mesajları */
```

### Breakpoints
```css
@media (max-width: 768px)   /* Mobile */
@media (min-width: 768px)   /* Tablet */
@media (min-width: 1024px)  /* Desktop */
@media (min-width: 1200px)  /* Large Desktop */
```

## 🔧 Teknik Detaylar

### Frontend Stack
- **Vanilla JavaScript**: Dependency yok, hızlı ve hafif
- **ES6+ Features**: async/await, arrow functions, destructuring
- **Fetch API**: Modern HTTP istekleri
- **LocalStorage**: Yedek kayıt sistemi

### Backend Stack
- **Django REST Framework**: API endpoints
- **JSON Fields**: Esnek veri yapısı (inventory, choices)
- **Foreign Keys**: Character → User, City ilişkileri
- **Signals**: Otomatik character oluşturma

### Veri Akışı
```
User Action → JavaScript → API Call → Django View → Database
                                           ↓
                                    Response JSON
                                           ↓
                            Update Frontend State → UI Refresh
```

## 🐛 Sorun Giderme

### Oyun başlamıyor
- Session var mı kontrol edin: `request.session.get('tradesim_game_session')`
- Character var mı kontrol edin: `Character.objects.filter(user=request.user)`
- Başlangıç parası: `character.score >= 100`

### Şehirler görünmüyor
- Database'de şehir var mı: `City.objects.all()`
- API yanıt veriyor mu: `/games/trade-sim/cities/`

### Ürünler görünmüyor
- CityMarket kayıtları var mı kontrol edin
- API yanıtını test edin: `/games/trade-sim/city-markets/1/`

### Alım-satım çalışmıyor
- Console'da hata var mı kontrol edin (F12)
- CSRF token doğru mu: Network tab → Headers
- Character'da yeterli para var mı

## 📈 Gelecek Geliştirmeler

- [ ] Achievement sistemi
- [ ] Multiplayer turnuvalar
- [ ] AI rakipler
- [ ] Özel events (pazar krizleri, fırsatlar)
- [ ] Grafik ve chartlar
- [ ] Ses efektleri
- [ ] PWA support
- [ ] Leaderboard filtreleme

## 🤝 Katkıda Bulunma

TradeSim, FinAsis platformunun bir parçasıdır. Geliştirmeler için:

1. Feature branch oluşturun
2. Değişikliklerinizi yapın
3. Test edin (mobil dahil!)
4. Pull request açın

## 📄 Lisans

FinAsis © 2025 - Tüm hakları saklıdır.

---

**Not**: Bu oyun, eğitim amaçlı bir simülasyondur. Gerçek finansal tavsiye değildir.
