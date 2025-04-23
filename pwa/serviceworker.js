const CACHE_NAME = 'finasis-v1';
const CACHE_VERSION = '1.0.0';
const CACHE_EXPIRATION = 60 * 60 * 24 * 7; // 7 gün

const urlsToCache = [
  '/',
  '/dashboard/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/charts.js',
  '/static/js/forms.js',
  '/manifest.json',
  '/static/images/logo.png',
  '/static/images/icons/icon-192x192.png',
  '/static/images/icons/icon-512x512.png',
  '/static/fonts/roboto-regular.woff2',
  '/static/fonts/roboto-bold.woff2'
];

// Önbellek stratejileri
const cacheStrategies = {
  networkFirst: async (request) => {
    try {
      const networkResponse = await fetch(request);
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    } catch (error) {
      const cachedResponse = await caches.match(request);
      return cachedResponse || new Response('Offline', { status: 503 });
    }
  },
  
  cacheFirst: async (request) => {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    try {
      const networkResponse = await fetch(request);
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    } catch (error) {
      return new Response('Offline', { status: 503 });
    }
  }
};

// Dosya işleme stratejileri
const fileHandlers = {
  pdf: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'pdf');
    
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      return response;
    } catch (error) {
      console.error('PDF yükleme hatası:', error);
      return new Response('PDF yükleme hatası', { status: 500 });
    }
  },
  
  excel: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', 'excel');
    
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      return response;
    } catch (error) {
      console.error('Excel yükleme hatası:', error);
      return new Response('Excel yükleme hatası', { status: 500 });
    }
  }
};

// Service Worker kurulumu
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// İstek işleme
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // API istekleri için network-first stratejisi
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(cacheStrategies.networkFirst(event.request));
    return;
  }
  
  // Statik dosyalar için cache-first stratejisi
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheStrategies.cacheFirst(event.request));
    return;
  }
  
  // Paylaşım istekleri
  if (url.pathname === '/share') {
    event.respondWith(handleShare(event.request));
    return;
  }
  
  // Dosya yükleme istekleri
  if (url.pathname === '/upload') {
    event.respondWith(handleFileUpload(event.request));
    return;
  }
  
  // Diğer istekler için network-first stratejisi
  event.respondWith(cacheStrategies.networkFirst(event.request));
});

// Paylaşım işleme
async function handleShare(request) {
  try {
    const formData = await request.formData();
    const title = formData.get('title');
    const text = formData.get('text');
    const url = formData.get('url');
    
    // Paylaşım verilerini API'ye gönder
    const response = await fetch('/api/share', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title, text, url })
    });
    
    return response;
  } catch (error) {
    console.error('Paylaşım hatası:', error);
    return new Response('Paylaşım hatası', { status: 500 });
  }
}

// Dosya yükleme işleme
async function handleFileUpload(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    
    if (!file) {
      return new Response('Dosya bulunamadı', { status: 400 });
    }
    
    // Dosya tipine göre işleme
    if (file.type === 'application/pdf') {
      return await fileHandlers.pdf(file);
    } else if (
      file.type === 'application/vnd.ms-excel' ||
      file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ) {
      return await fileHandlers.excel(file);
    } else {
      return new Response('Desteklenmeyen dosya tipi', { status: 400 });
    }
  } catch (error) {
    console.error('Dosya yükleme hatası:', error);
    return new Response('Dosya yükleme hatası', { status: 500 });
  }
}

// Eski önbellekleri temizleme
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Push bildirimleri
self.addEventListener('push', (event) => {
  const options = {
    body: event.data.text(),
    icon: '/static/images/icons/icon-192x192.png',
    badge: '/static/images/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Görüntüle',
        icon: '/static/images/icons/checkmark.png'
      },
      {
        action: 'close',
        title: 'Kapat',
        icon: '/static/images/icons/xmark.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('FinAsis Bildirimi', options)
  );
});

// Bildirim tıklama işlemi
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/notifications/')
    );
  }
}); 