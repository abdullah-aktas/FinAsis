const CACHE_NAME = 'finasis-v2';
const OFFLINE_URL = '/static/offline.html';

const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/css/responsive.css',
    '/static/js/main.js',
    '/static/manifest.json',
    OFFLINE_URL,
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

// Önbellek Stratejisi: Network First, Cache Fallback
const networkFirstStrategy = async (request) => {
    try {
        const networkResponse = await fetch(request);
        const cache = await caches.open(CACHE_NAME);
        cache.put(request, networkResponse.clone());
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        if (request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
        }
        throw error;
    }
};

// Önbellek Stratejisi: Cache First, Network Fallback
const cacheFirstStrategy = async (request) => {
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
        if (request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
        }
        throw error;
    }
};

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    const request = event.request;
    
    // API istekleri için Network First stratejisi
    if (request.url.includes('/api/')) {
        event.respondWith(networkFirstStrategy(request));
        return;
    }
    
    // Statik dosyalar için Cache First stratejisi
    if (request.url.includes('/static/')) {
        event.respondWith(cacheFirstStrategy(request));
        return;
    }
    
    // Diğer istekler için Network First stratejisi
    event.respondWith(networkFirstStrategy(request));
});

// Periyodik önbellek temizliği
self.addEventListener('periodicsync', event => {
    if (event.tag === 'cleanup-cache') {
        event.waitUntil(
            caches.open(CACHE_NAME).then(cache => {
                return cache.keys().then(requests => {
                    return Promise.all(
                        requests.map(request => {
                            return fetch(request).then(response => {
                                if (!response.ok) {
                                    return cache.delete(request);
                                }
                            }).catch(() => {
                                return cache.delete(request);
                            });
                        })
                    );
                });
            })
        );
    }
}); 