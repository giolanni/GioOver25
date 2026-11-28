const CACHE = 'gioover-pwa-v10';
const APP_SHELL = ['./','index.html','styles.css','app.js','manifest.webmanifest','icons/gioover-ov25-192.png','icons/gioover-ov25-512.png','icons/gioover-ov25-apple-180.png'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(APP_SHELL))));
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('message', event => { if (event.data?.type === 'SKIP_WAITING') self.skipWaiting(); });
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/data/current.json')) return event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(response => { const copy=response.clone(); caches.open(CACHE).then(cache => cache.put(event.request,copy)); return response; })));
});
