# FinAsis Teknik Dokümantasyon

## 1. Sistem Mimarisi

FinAsis, modern bir web uygulaması olarak tasarlanmış olup, aşağıdaki bileşenlerden oluşmaktadır:

### 1.1. Backend

- **Django Framework (v5.0.2)**: Ana uygulama çerçevesi
- **Django REST Framework (v3.14.0)**: API geliştirme için
- **Django AllAuth (v65.7.0)**: Kimlik doğrulama ve kullanıcı yönetimi
- **Celery (v5.3.6)**: Asenkron görev yönetimi
- **Redis (v5.0.1)**: Önbellek ve mesaj kuyruğu
- **SQLite/PostgreSQL**: Veritabanı yönetimi

### 1.2. Frontend

- **HTML5/CSS3/JavaScript**: Temel web teknolojileri
- **Bootstrap 5**: Responsive tasarım çerçevesi
- **jQuery**: JavaScript kütüphanesi
- **Font Awesome**: İkon kütüphanesi

### 1.3. Özel Bileşenler

- **Ursina Engine (v6.1.2)**: 3D oyun geliştirme
- **Panda3D (v1.10.14)**: 3D grafik motoru
- **Web3.js (v6.15.1)**: Blockchain entegrasyonu
- **OpenAI (v1.12.0)**: AI Asistan entegrasyonu

### 1.4. Mobil ve Masaüstü

- **React Native**: Mobil uygulama (iOS ve Android)
- **Electron**: Masaüstü uygulaması (Windows, macOS, Linux)

## 2. Sistem Gereksinimleri

### 2.1. Sunucu Gereksinimleri

- **İşletim Sistemi**: Ubuntu 20.04 LTS veya daha yeni
- **RAM**: En az 8GB (önerilen 16GB)
- **CPU**: 4+ çekirdek
- **Depolama**: 50GB SSD
- **Bant Genişliği**: Ayda 1TB+

### 2.2. Geliştirme Ortamı

- **Python**: 3.10 veya daha yeni
- **Node.js**: 14.x veya daha yeni
- **npm/yarn**: Paket yönetimi için
- **Git**: Sürüm kontrolü için
- **Docker**: Container yönetimi için (opsiyonel)

### 2.3. Kullanıcı Gereksinimleri

#### Web

- Modern bir web tarayıcısı (Chrome, Firefox, Safari, Edge)
- JavaScript etkin
- Cookie desteği

#### Mobil

- iOS 14+ veya Android 9+
- 100MB boş alan
- İnternet bağlantısı

#### Masaüstü

- Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- 4GB RAM
- 500MB boş alan
- OpenGL 3.3+ desteği (oyunlar için)

## 3. Veritabanı Yapısı

### 3.1. Ana Tablolar

- **User**: Kullanıcı hesapları
- **Profile**: Kullanıcı profilleri
- **Course**: Eğitim kursları
- **Module**: Kurs modülleri
- **Lesson**: Modül dersleri
- **Quiz**: Sınavlar
- **Certificate**: Kullanıcı sertifikaları
- **VirtualCompany**: Sanal şirketler
- **Transaction**: Finansal işlemler
- **BlockchainTransaction**: Blockchain işlemleri
- **AIAssistantChat**: AI asistan sohbetleri
- **GameScore**: Oyun skorları

### 3.2. İlişkiler

Veritabanı şeması ER diyagramı olarak `docs/database/er_diagram.png` dosyasında bulunmaktadır.

## 4. API Dokümantasyonu

FinAsis API'si RESTful prensiplerine göre tasarlanmıştır ve JSON formatında veri alışverişi yapar.

### 4.1. Kimlik Doğrulama

Tüm API istekleri için JWT (JSON Web Token) kimlik doğrulaması gereklidir.

```
POST /api/auth/token/
{
    "username": "user@example.com",
    "password": "secure_password"
}

Response:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4.2. Kullanıcı Yönetimi

```
GET /api/users/profile/
POST /api/users/profile/
PUT /api/users/profile/
DELETE /api/users/profile/
```

### 4.3. Eğitim API

```
GET /api/education/courses/
GET /api/education/courses/{id}/
GET /api/education/modules/{id}/
GET /api/education/lessons/{id}/
POST /api/education/enroll/{course_id}/
```

### 4.4. Sanal Şirket API

```
GET /api/virtual-company/
POST /api/virtual-company/
GET /api/virtual-company/{id}/
PUT /api/virtual-company/{id}/
GET /api/virtual-company/{id}/finances/
POST /api/virtual-company/{id}/transaction/
```

### 4.5. Blockchain API

```
GET /api/blockchain/transactions/
POST /api/blockchain/transactions/
GET /api/blockchain/transactions/{id}/
GET /api/blockchain/wallet/
```

### 4.6. AI Asistan API

```
POST /api/ai-assistant/chat/
GET /api/ai-assistant/history/
DELETE /api/ai-assistant/history/{id}/
```

### 4.7. Oyun API

```
GET /api/games/
GET /api/games/{id}/
POST /api/games/{id}/score/
GET /api/games/leaderboard/{game_id}/
```

## 5. Ursina 3D Oyun Entegrasyonu

### 5.1. Kurulum ve Bağımlılıklar

```python
# Gerekli paketler
pip install ursina==6.1.2 panda3d==1.10.14 numpy==1.24.3 pillow==10.2.0
```

### 5.2. Oyun Mimarisi

FinancialTradingGame sınıfı, Ursina framework'ünü kullanarak 3D finansal ticaret simülasyonu oluşturur:

```python
class FinancialTradingGame(Ursina):
    def __init__(self):
        super().__init__()
        # Oyun değişkenleri
        self.player_money = 10000
        self.companies = []
        self.stock_prices = {}
        self.player_stocks = {}
        # ...
```

### 5.3. Django Entegrasyonu

Oyun, Django view üzerinden başlatılır ve sonuçlar veritabanında saklanır:

```python
def trade_trail_3d(request):
    from ursina_game.game import run_game
    import threading
    
    # Oyunu ayrı bir thread'de başlat
    game_thread = threading.Thread(target=run_game)
    game_thread.daemon = True
    game_thread.start()
    
    # ...
```

### 5.4. Veri Akışı

1. Kullanıcı oyunu başlatır
2. Oyun verileri yüklenir
3. Kullanıcı etkileşimleri işlenir
4. Oyun sonuçları veritabanına kaydedilir

## 6. Mobil Uygulama

### 6.1. React Native Yapısı

```
FinasisMobile/
├── android/
├── ios/
├── src/
│   ├── components/
│   ├── screens/
│   ├── navigation/
│   ├── services/
│   ├── store/
│   └── utils/
├── App.js
└── package.json
```

### 6.2. API Entegrasyonu

React Native uygulaması, web uygulaması ile aynı API'yi kullanır:

```javascript
// API servisi örneği
const apiService = {
  login: async (username, password) => {
    try {
      const response = await fetch(`${API_URL}/auth/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      return await response.json();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  // ...
};
```

### 6.3. Derleme ve Dağıtım

#### Android

```bash
cd FinasisMobile
npx react-native bundle --platform android --dev false --entry-file index.js --bundle-output android/app/src/main/assets/index.android.bundle
cd android
./gradlew assembleRelease
```

#### iOS

```bash
cd FinasisMobile
npx react-native bundle --platform ios --dev false --entry-file index.js --bundle-output ios/bundle
cd ios
xcodebuild -workspace FinAsis.xcworkspace -scheme FinAsis -configuration Release
```

## 7. Masaüstü Uygulaması

### 7.1. Electron Yapısı

```
FinasisDesktop/
├── src/
│   ├── main.js
│   ├── renderer.js
│   ├── components/
│   ├── services/
│   └── utils/
├── build/
├── package.json
└── forge.config.js
```

### 7.2. Web Paketi Entegrasyonu

Electron uygulaması, Django web uygulamasını çevreleme (wrapping) yöntemiyle kullanır:

```javascript
// main.js
const { app, BrowserWindow } = require('electron');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Django uygulamasının URL'si
  mainWindow.loadURL('http://localhost:8000');
}

app.whenReady().then(createWindow);
```

### 7.3. Yerel API Erişimi

Electron, yerel sistem kaynaklarına erişim sağlar:

```javascript
// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  startGame: () => ipcRenderer.invoke('start-game'),
  saveData: (data) => ipcRenderer.invoke('save-data', data),
  openFile: () => ipcRenderer.invoke('open-file-dialog'),
  // ...
});
```

### 7.4. Paketleme ve Dağıtım

```bash
cd FinasisDesktop
npm run make
```

Bu komut, Windows (.exe), macOS (.dmg) ve Linux (.AppImage) için yükleme paketleri oluşturur.

## 8. Güvenlik Önlemleri

### 8.1. Web Güvenliği

- HTTPS zorunlu
- CSRF koruma
- XSS koruma
- SQL enjeksiyon koruması
- Rate limiting
- İçerik Güvenliği Politikası (CSP)

### 8.2. API Güvenliği

- JWT kimlik doğrulama
- API anahtarı doğrulama
- Yetkilendirme kontrolleri
- Request validasyonu

### 8.3. Veri Güvenliği

- Şifrelerin bcrypt ile hashlenmiş olarak saklanması
- Hassas verilerin şifrelenmesi
- Düzenli yedekleme
- GDPR uyumluluğu

## 9. Test Stratejisi

### 9.1. Birim Testleri

```bash
python manage.py test
```

### 9.2. Entegrasyon Testleri

```bash
pytest
```

### 9.3. E2E Testleri

```bash
npm run cypress
```

### 9.4. Performans Testleri

```bash
locust -f locustfile.py
```

## 10. Dağıtım (Deployment)

### 10.1. Docker ile Dağıtım

```bash
docker-compose up -d
```

### 10.2. Manuel Dağıtım

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Statik dosyaları topla
python manage.py collectstatic

# Veritabanı migrasyonlarını uygula
python manage.py migrate

# Gunicorn ile çalıştır
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### 10.3. CI/CD Pipeline

GitHub Actions kullanılarak otomatik test ve dağıtım süreci oluşturulmuştur.

## 11. Sorun Giderme ve Hata Ayıklama

### 11.1. Loglama

Uygulamanın logları şu konumlarda bulunur:

- Web: `/logs/web.log`
- Celery: `/logs/celery.log`
- Nginx: `/var/log/nginx/access.log` ve `/var/log/nginx/error.log`

### 11.2. Genel Sorunlar ve Çözümleri

- **500 Sunucu Hatası**: Logları kontrol edin, genellikle bir istisna hatası vardır.
- **Statik Dosyalar Yüklenmiyor**: `collectstatic` komutunun doğru çalıştığından emin olun.
- **Celery Görevleri Çalışmıyor**: Redis bağlantısını ve Celery worker durumunu kontrol edin.
- **Oyun Performans Sorunları**: GPU sürücülerinin güncel olduğundan emin olun.

---

Bu dokümantasyon FinAsis platformunun teknik ayrıntılarını içermektedir. Güncellemeler için lütfen GitHub repository'sini takip edin. Sorunlar veya katkıda bulunmak için GitHub Issues kullanabilirsiniz. 