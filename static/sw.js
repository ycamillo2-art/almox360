const CACHE_NAME = 'almox-v1.4.2';
const ASSETS = [
  '/',
  '/login/',
  '/cadastro/',
  '/movimentacao/',
  '/veiculos/',
  '/relatorios/',
  '/static/icon.png',
  '/static/manifest.json',
  'https://unpkg.com/dexie@latest/dist/dexie.js',
  'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',
  'https://code.jquery.com/jquery-3.5.1.min.js',
  'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',
  'https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js',
  'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Solo capturamos GET
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request).then(response => {
      // Se a resposta for OK, guardamos no cache e retornamos
      if (response.ok) {
        const resClone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));
      }
      return response;
    }).catch(() => {
      // Se falhar a rede (offline), buscamos no cache
      return caches.match(event.request).then(cachedResponse => {
        if (cachedResponse) return cachedResponse;
        
        // Se nem no cache tem, retornamos a página inicial (se for navegação)
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
      });
    })
  );
});
