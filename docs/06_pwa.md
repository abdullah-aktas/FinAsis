# 6. PWA ve Çevrimdışı Kullanım

## 📌 Amaç
Bu dokümantasyon, FinAsis projesinin Progressive Web App (PWA) özelliklerini ve çevrimdışı kullanım yeteneklerini detaylandırmaktadır.

## ⚙️ Teknik Yapı

### 1. ServiceWorker Yapılandırması

#### 1.1. ServiceWorker Kaydı
```javascript
// service-worker.js
const CACHE_NAME = 'finasis-v1';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/app.js',
    '/static/images/logo.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
```

#### 1.2. ServiceWorker Aktivasyonu
```javascript
// app.js
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker başarıyla kaydedildi:', registration.scope);
            })
            .catch(error => {
                console.log('ServiceWorker kaydı başarısız:', error);
            });
    });
}
```

### 2. IndexedDB Senkronizasyonu

#### 2.1. Veritabanı Yapılandırması
```javascript
// db.js
const dbName = 'finasisDB';
const dbVersion = 1;

const initDB = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName, dbVersion);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            // Müşteri deposu
            if (!db.objectStoreNames.contains('customers')) {
                const customerStore = db.createObjectStore('customers', { keyPath: 'id' });
                customerStore.createIndex('email', 'email', { unique: true });
            }

            // Fatura deposu
            if (!db.objectStoreNames.contains('invoices')) {
                const invoiceStore = db.createObjectStore('invoices', { keyPath: 'id' });
                invoiceStore.createIndex('customerId', 'customerId', { unique: false });
                invoiceStore.createIndex('date', 'date', { unique: false });
            }
        };
    });
};
```

#### 2.2. Veri Senkronizasyonu
```javascript
// sync.js
class DataSync {
    constructor() {
        this.db = null;
        this.syncQueue = [];
    }

    async init() {
        this.db = await initDB();
    }

    async saveForSync(data) {
        const transaction = this.db.transaction(['syncQueue'], 'readwrite');
        const store = transaction.objectStore('syncQueue');
        await store.add({
            id: Date.now(),
            data: data,
            status: 'pending'
        });
    }

    async syncWithServer() {
        if (!navigator.onLine) return;

        const transaction = this.db.transaction(['syncQueue'], 'readwrite');
        const store = transaction.objectStore('syncQueue');
        const items = await store.getAll();

        for (const item of items) {
            try {
                await this.sendToServer(item.data);
                await store.delete(item.id);
            } catch (error) {
                console.error('Senkronizasyon hatası:', error);
            }
        }
    }

    async sendToServer(data) {
        const response = await fetch('/api/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Sunucu hatası');
        }
    }
}
```

### 3. Çevrimdışı Veri Yönetimi

#### 3.1. Veri Önbelleğe Alma
```javascript
// cache.js
class DataCache {
    constructor() {
        this.db = null;
    }

    async init() {
        this.db = await initDB();
    }

    async cacheData(storeName, data) {
        const transaction = this.db.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);

        if (Array.isArray(data)) {
            for (const item of data) {
                await store.put(item);
            }
        } else {
            await store.put(data);
        }
    }

    async getCachedData(storeName, query) {
        const transaction = this.db.transaction([storeName], 'readonly');
        const store = transaction.objectStore(storeName);
        
        if (query) {
            return await store.get(query);
        } else {
            return await store.getAll();
        }
    }
}
```

#### 3.2. Çevrimdışı Form Gönderimi
```javascript
// forms.js
class OfflineForm {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.dataSync = new DataSync();
    }

    init() {
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(this.form);
            const data = Object.fromEntries(formData.entries());

            if (navigator.onLine) {
                await this.submitForm(data);
            } else {
                await this.dataSync.saveForSync({
                    type: 'form',
                    formId: this.form.id,
                    data: data
                });
                this.showOfflineMessage();
            }
        });
    }

    async submitForm(data) {
        try {
            const response = await fetch(this.form.action, {
                method: this.form.method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Form gönderimi başarısız');
            }

            this.showSuccessMessage();
        } catch (error) {
            this.showErrorMessage(error);
        }
    }

    showOfflineMessage() {
        // Çevrimdışı mesajı göster
    }

    showSuccessMessage() {
        // Başarı mesajı göster
    }

    showErrorMessage(error) {
        // Hata mesajı göster
    }
}
```

## 🔧 Kullanım Adımları

### 1. PWA Kurulumu

#### 1.1. Manifest Dosyası
```json
// manifest.json
{
    "name": "FinAsis",
    "short_name": "FinAsis",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#4a90e2",
    "icons": [
        {
            "src": "/static/images/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/images/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}
```

#### 1.2. HTML Entegrasyonu
```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#4a90e2">
    <link rel="apple-touch-icon" href="/static/images/icon-192x192.png">
    <title>FinAsis</title>
</head>
<body>
    <!-- Uygulama içeriği -->
    <script src="/static/js/app.js"></script>
</body>
</html>
```

### 2. Çevrimdışı Veri Yönetimi

#### 2.1. Veri Önbelleğe Alma
```javascript
// Veri önbelleğe alma
const dataCache = new DataCache();
await dataCache.init();

// Müşteri verilerini önbelleğe al
const customers = await fetch('/api/customers').then(r => r.json());
await dataCache.cacheData('customers', customers);

// Çevrimdışı veri okuma
const cachedCustomers = await dataCache.getCachedData('customers');
```

#### 2.2. Form Senkronizasyonu
```javascript
// Form senkronizasyonu
const invoiceForm = new OfflineForm('invoice-form');
invoiceForm.init();

// Çevrimdışı veri senkronizasyonu
const dataSync = new DataSync();
await dataSync.init();

// Çevrimiçi olduğunda senkronize et
window.addEventListener('online', () => {
    dataSync.syncWithServer();
});
```

## 🧪 Test Örnekleri

### 1. ServiceWorker Testi
```javascript
// service-worker.test.js
describe('ServiceWorker', () => {
    it('should cache resources', async () => {
        const cache = await caches.open('finasis-v1');
        const cachedUrls = await cache.keys();
        
        expect(cachedUrls.length).toBeGreaterThan(0);
        expect(cachedUrls.some(url => url.href.endsWith('main.css'))).toBe(true);
    });
});
```

### 2. IndexedDB Testi
```javascript
// db.test.js
describe('IndexedDB', () => {
    it('should store and retrieve data', async () => {
        const db = await initDB();
        const transaction = db.transaction(['customers'], 'readwrite');
        const store = transaction.objectStore('customers');
        
        const customer = { id: 1, name: 'Test Customer' };
        await store.put(customer);
        
        const retrieved = await store.get(1);
        expect(retrieved).toEqual(customer);
    });
});
```

## 📝 Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. ServiceWorker Güncelleme Sorunları
**Sorun**: ServiceWorker güncellemeleri uygulanmıyor
**Çözüm**:
- Cache versiyonunu artırın
- Eski cache'leri temizleyin
- ServiceWorker'ı yeniden yükleyin

### 2. IndexedDB Senkronizasyon Hataları
**Sorun**: Veri senkronizasyonu başarısız
**Çözüm**:
- Senkronizasyon kuyruğunu kontrol edin
- Ağ bağlantısını doğrulayın
- Hata yönetimini geliştirin

### 3. Çevrimdışı Form Gönderimi
**Sorun**: Form verileri kayboluyor
**Çözüm**:
- Verileri IndexedDB'de saklayın
- Senkronizasyon durumunu takip edin
- Kullanıcıya geri bildirim verin

## 📂 Dosya Yapısı ve Referanslar

```
finasis/
├── static/
│   ├── js/
│   │   ├── service-worker.js
│   │   ├── db.js
│   │   ├── sync.js
│   │   └── forms.js
│   ├── css/
│   │   └── main.css
│   └── images/
│       ├── icon-192x192.png
│       └── icon-512x512.png
├── templates/
│   └── base.html
└── manifest.json
```

## 🔍 Ek Kaynaklar

- [ServiceWorker API Dokümantasyonu](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [IndexedDB API Dokümantasyonu](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [PWA Dokümantasyonu](https://web.dev/progressive-web-apps/)
- [Workbox Dokümantasyonu](https://developers.google.com/web/tools/workbox) 