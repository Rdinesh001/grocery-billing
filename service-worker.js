const CACHE_NAME = "siva-grocery-v1";

const urlsToCache = [
  "/login",
  "/signup",
  "/home",
  "/bill",
  "/static/manifest.json"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});