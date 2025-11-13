const CACHE_NAME = 'finasis-cache-v2';
const ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/css/brand.css',
  '/static/css/main.css',
  '/static/css/modern-ui.css',
  '/static/css/theme.css',
  '/static/css/a11y.css',
  '/static/js/main.js',
  '/static/js/register-sw.js',
  '/static/js/pwa-install-prompt.js',
  '/static/common/finasis_logo-192.png',
  '/static/common/finasis_logo-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name.startsWith('finasis-cache-') && name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});