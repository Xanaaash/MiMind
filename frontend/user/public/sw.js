const CACHE_NAME = 'mimind-v1';
const CRISIS_CACHE = 'mimind-crisis-v1';

const CRISIS_RESOURCES = [
  '/safety',
  '/locales/zh-CN.json',
  '/locales/en-US.json',
];

const OFFLINE_PAGE = '/offline.html';

self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(CRISIS_CACHE).then((cache) =>
        cache.addAll([OFFLINE_PAGE, ...CRISIS_RESOURCES])
      ),
      self.skipWaiting(),
    ])
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== CACHE_NAME && k !== CRISIS_CACHE)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (request.method !== 'GET') return;

  if (CRISIS_RESOURCES.some((r) => url.pathname === r || url.pathname.endsWith(r))) {
    event.respondWith(networkFirstThenCache(request, CRISIS_CACHE));
    return;
  }

  if (url.pathname.startsWith('/api/')) return;

  if (request.destination === 'document') {
    event.respondWith(networkFirstWithFallback(request));
    return;
  }

  if (
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'font' ||
    request.destination === 'image'
  ) {
    event.respondWith(cacheFirstThenNetwork(request));
    return;
  }
});

async function networkFirstThenCache(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response('Offline', { status: 503 });
  }
}

async function cacheFirstThenNetwork(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirstWithFallback(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    const offline = await caches.match(OFFLINE_PAGE);
    if (offline) return offline;
    return new Response('Offline', { status: 503, headers: { 'Content-Type': 'text/html' } });
  }
}
