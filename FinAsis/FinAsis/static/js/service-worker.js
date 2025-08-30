const CACHE_NAME = 'finasis-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/css/theme.css',
  '/static/js/main.js',
  '/static/common/finasis_logo-192.png',
  '/static/common/finasis_logo-512.png'
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