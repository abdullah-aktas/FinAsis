// FinAsis PWA Service Worker

const CACHE_NAME = 'finasis-app-v1';
const OFFLINE_URL = '/offline/';
const CACHED_URLS = [
    '/',
    '/offline/',
    '/static/css/styles.css',
    '/static/js/app.js',
    '/static/img/logo.png',
    '/static/img/favicon.png',
    '/static/pwa/manifest.json',
    '/static/pwa/indexeddb_service.js',
    '/static/images/icons/icon-192x192.png',
    '/static/images/icons/icon-512x512.png',
];

// SW Kurulumu - temel URL'leri önbelleğe al
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Önbellek açıldı');
                return cache.addAll(CACHED_URLS);
            })
            .then(() => {
                return self.skipWaiting();
            })
    );
});

// SW Etkinleştirme - eski önbellekleri temizle
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Eski önbellek siliniyor:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker aktif edildi');
            return self.clients.claim();
        })
    );
});

// Fetch olayını yönet - ağ önce, sonra önbellek stratejisi
self.addEventListener('fetch', (event) => {
    // Yalnızca GET isteklerini yönet
    if (event.request.method !== 'GET') return;
    
    // API isteklerini önbelleğe alma
    if (event.request.url.includes('/api/') || 
        event.request.url.includes('/admin/') ||
        event.request.headers.get('Accept').includes('application/json')) {
        return;
    }
    
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Geçerli bir yanıt alındıysa, önbelleğe ekle
                if (response && response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseClone);
                        });
                }
                return response;
            })
            .catch(() => {
                // Ağ hatası durumunda önbellekten yanıt almayı dene
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        // Önbellekte varsa döndür
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        
                        // HTML içeriği istenmişse ve önbellekte yoksa, çevrimdışı sayfasını döndür
                        if (event.request.headers.get('Accept').includes('text/html')) {
                            return caches.match(OFFLINE_URL);
                        }
                        
                        // İmaj ve diğer kaynaklar için 404 döndür
                        return new Response('Resource not found', {
                            status: 404,
                            headers: {'Content-Type': 'text/plain'}
                        });
                    });
            })
    );
});

// Push bildirimi alma
self.addEventListener('push', (event) => {
    if (!event.data) return;
    
    try {
        const data = event.data.json();
        const options = {
            body: data.body || 'Yeni bildirim',
            icon: data.icon || '/static/images/icons/icon-192x192.png',
            badge: data.badge || '/static/images/icons/badge-72x72.png',
            data: {
                url: data.url || '/'
            },
            actions: data.actions || [],
            vibrate: [100, 50, 100]
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title || 'FinAsis Bildirimi', options)
        );
    } catch (error) {
        console.error('Push bildirimi işlenirken hata:', error);
    }
});

// Bildirime tıklama
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    if (event.action) {
        // Özel eylem gerçekleştir
        console.log('Bildirim eylemi:', event.action);
    }
    
    const urlToOpen = event.notification.data && event.notification.data.url 
        ? event.notification.data.url 
        : '/';
    
    event.waitUntil(
        clients.matchAll({type: 'window'})
            .then((windowClients) => {
                // Açık bir sekmede URL zaten açıksa onu etkinleştir
                for (let client of windowClients) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Yoksa yeni sekme aç
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// Arka plan senkronizasyonu
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-data') {
        event.waitUntil(
            // IndexedDB'den bekleyen verileri al ve senkronize et
            syncOfflineData()
        );
    }
});

// Çevrimdışı verileri senkronize etme
function syncOfflineData() {
    return new Promise((resolve, reject) => {
        // Bu örnekte API URL'yi ayarla - gerçek URL'yi kullanın
        const apiUrl = '/api/sync/';
        
        // IndexedDB'den bekleyen verileri al
        return getOfflineData()
            .then((offlineData) => {
                if (!offlineData || offlineData.length === 0) {
                    console.log('Senkronize edilecek veri yok');
                    return resolve();
                }
                
                // Sunucuya veri gönder
                return fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ data: offlineData })
                })
                .then((response) => {
                    if (response.ok) {
                        // Başarılı senkronizasyon, verileri temizle
                        return clearOfflineData().then(() => resolve());
                    } else {
                        console.error('Senkronizasyon hatası:', response.statusText);
                        return reject(new Error('Senkronizasyon başarısız'));
                    }
                });
            })
            .catch((error) => {
                console.error('Veri senkronizasyonu sırasında hata:', error);
                reject(error);
            });
    });
}

// IndexedDB'den bekleyen verileri al
function getOfflineData() {
    // Bu işlev, PWA için IndexedDB'den çevrimdışı verileri almalıdır
    // Gerçek uygulamada kendi IndexedDB yönetimi uygulanmalıdır
    return Promise.resolve([]);
}

// Senkronize edilen verileri temizle
function clearOfflineData() {
    // Bu işlev, senkronize edilen verileri IndexedDB'den temizlemelidir
    return Promise.resolve();
}

// CSRF token alma
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 