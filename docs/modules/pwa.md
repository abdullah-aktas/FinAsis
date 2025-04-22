# FinAsis PWA ve Çevrimdışı Kullanım Modülü

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

FinAsis PWA (Progressive Web Application) modülü, kullanıcıların uygulamayı masaüstü ve mobil cihazlarda çevrimdışı olarak kullanabilmelerini sağlayan, modern web teknolojilerini kullanan bir çözümdür.

## 🎯 Özellikler

- Çevrimdışı çalışma desteği
- Masaüstü ve mobil uygulama deneyimi
- Push bildirimleri
- Yerel veri depolama
- Otomatik senkronizasyon
- Hızlı yükleme
- Güvenli bağlantı
- Cihaz entegrasyonu

## 🔧 Kurulum

### Gereksinimler
- Node.js 14+
- npm 6+
- Service Worker desteği
- HTTPS sertifikası

### Kurulum Adımları
1. Gerekli paketleri yükleyin:
```bash
npm install -g @finasis/pwa
```

2. PWA yapılandırmasını oluşturun:
```bash
finasis-pwa init
```

3. Service Worker'ı kaydedin:
```bash
finasis-pwa register
```

## 🛠️ Yapılandırma

### PWA Ayarları
```javascript
const pwaConfig = {
    name: "FinAsis",
    short_name: "FinAsis",
    start_url: "/",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#2196f3",
    icons: [
        {
            src: "/icons/icon-192x192.png",
            sizes: "192x192",
            type: "image/png"
        },
        {
            src: "/icons/icon-512x512.png",
            sizes: "512x512",
            type: "image/png"
        }
    ]
};
```

### Çevrimdışı Ayarlar
```javascript
const offlineConfig = {
    cacheName: "finasis-cache",
    maxAge: 86400,
    maxEntries: 50,
    strategy: "networkFirst"
};
```

## 📊 Kullanım

### Service Worker Kaydı
```javascript
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}
```

### Çevrimdışı Veri Yönetimi
```javascript
const offlineManager = new OfflineManager();

// Veri kaydetme
offlineManager.saveData('transactions', {
    id: 1,
    amount: 1000,
    date: new Date()
});

// Veri senkronizasyonu
offlineManager.syncData().then(() => {
    console.log('Veriler senkronize edildi');
});
```

### Push Bildirimleri
```javascript
const notificationManager = new NotificationManager();

// Bildirim izni iste
notificationManager.requestPermission().then(permission => {
    if (permission === 'granted') {
        // Bildirim gönder
        notificationManager.sendNotification({
            title: 'Yeni Fatura',
            body: 'Yeni bir fatura oluşturuldu',
            icon: '/icons/notification.png'
        });
    }
});
```

## 🔍 Örnek Kullanımlar

### Çevrimdışı Form Gönderimi
```javascript
const formManager = new FormManager();

formManager.submitForm({
    formId: 'invoice-form',
    data: formData,
    onSuccess: () => {
        console.log('Form başarıyla gönderildi');
    },
    onError: (error) => {
        console.error('Form gönderimi başarısız:', error);
    }
});
```

### Veri Senkronizasyonu
```javascript
const syncManager = new SyncManager();

// Manuel senkronizasyon
syncManager.manualSync().then(() => {
    console.log('Manuel senkronizasyon tamamlandı');
});

// Otomatik senkronizasyon
syncManager.autoSync({
    interval: 300000, // 5 dakika
    onSync: () => {
        console.log('Otomatik senkronizasyon tamamlandı');
    }
});
```

## 🧪 Test

### Test Ortamı
```bash
npm run test:pwa
```

### Test Kapsamı
- Service Worker
- Çevrimdışı işlevsellik
- Push bildirimleri
- Veri senkronizasyonu
- Performans testleri

## 📈 Performans

### Ölçümler
- Sayfa yükleme süresi: < 2 saniye
- Çevrimdışı başlatma süresi: < 1 saniye
- Veri senkronizasyon süresi: < 5 saniye
- Bellek kullanımı: < 100MB

### Optimizasyon
- Önbellekleme
- Veri sıkıştırma
- Lazy loading
- Code splitting

## 🔒 Güvenlik

### Veri Güvenliği
- Veri şifreleme
- Güvenli depolama
- Erişim kontrolü
- Veri yedekleme

### Uygulama Güvenliği
- HTTPS zorunluluğu
- Content Security Policy
- XSS koruması
- CSRF koruması

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
1. ESLint kurallarına uyun
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
- E-posta: pwa-support@finasis.com
- Slack: #pwa-support
- GitHub Issues

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Uptime: %99.9 