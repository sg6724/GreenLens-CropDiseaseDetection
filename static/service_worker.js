// Simple service worker for GreenLens PWA
const CACHE_NAME = 'greenlens-v1';
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/js/app.js'
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
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});