// Service Worker for Progressive Web App
// Implements cache-first strategy with background sync for offline functionality

const CACHE_NAME = 'todo-app-v1';
const API_CACHE_NAME = 'todo-app-api-v1';
const OFFLINE_URL = '/offline.html';

// Static assets to pre-cache on install (T078, FR-024)
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/manifest.json',
  '/favicon.ico',
  // PWA icons for standalone mode
  '/icons/icon-72x72.png',
  '/icons/icon-96x96.png',
  '/icons/icon-128x128.png',
  '/icons/icon-144x144.png',
  '/icons/icon-152x152.png',
  '/icons/icon-192x192.png',
  '/icons/icon-384x384.png',
  '/icons/icon-512x512.png',
];

// Cache-first strategy: Try cache first, fall back to network
const cacheFirst = async (request) => {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    // Cache successful responses
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    // If offline and no cache, return offline page for navigation requests
    if (request.destination === 'document') {
      return cache.match(OFFLINE_URL);
    }
    throw error;
  }
};

// Network-first strategy for API calls (with cache fallback)
const networkFirst = async (request) => {
  const cache = await caches.open(API_CACHE_NAME);

  try {
    const response = await fetch(request);
    // Cache successful API responses
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    // Fall back to cache if offline
    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }
    throw error;
  }
};

// Install event: Pre-cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Pre-caching static assets');
      return cache.addAll(STATIC_ASSETS);
    }).then(() => {
      // Activate immediately without waiting for old service worker to finish
      return self.skipWaiting();
    })
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Take control of all pages immediately
      return self.clients.claim();
    })
  );
});

// Fetch event: Implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // API requests: network-first with cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Static assets: cache-first
  event.respondWith(cacheFirst(request));
});

// Background Sync: Queue offline changes and sync when online
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync triggered:', event.tag);

  if (event.tag === 'sync-tasks') {
    event.waitUntil(syncTasks());
  } else if (event.tag === 'sync-task-updates') {
    event.waitUntil(syncTaskUpdates());
  }
});

// Sync queued task creations
async function syncTasks() {
  try {
    // Get queued tasks from IndexedDB
    const db = await openDB();
    const tx = db.transaction('pending-tasks', 'readonly');
    const store = tx.objectStore('pending-tasks');
    const pendingTasks = await store.getAll();

    // Send each task to the server
    for (const task of pendingTasks) {
      try {
        const response = await fetch('/api/tasks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(task.data),
        });

        if (response.ok) {
          // Remove from queue after successful sync
          const deleteTx = db.transaction('pending-tasks', 'readwrite');
          const deleteStore = deleteTx.objectStore('pending-tasks');
          await deleteStore.delete(task.id);

          console.log('[Service Worker] Synced task:', task.id);
        }
      } catch (error) {
        console.error('[Service Worker] Failed to sync task:', task.id, error);
      }
    }

    // Notify all clients that sync is complete
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        data: { count: pendingTasks.length }
      });
    });
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error);
    throw error;
  }
}

// Sync queued task updates
async function syncTaskUpdates() {
  try {
    const db = await openDB();
    const tx = db.transaction('pending-updates', 'readonly');
    const store = tx.objectStore('pending-updates');
    const pendingUpdates = await store.getAll();

    for (const update of pendingUpdates) {
      try {
        const response = await fetch(`/api/tasks/${update.taskId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(update.data),
        });

        if (response.ok) {
          const deleteTx = db.transaction('pending-updates', 'readwrite');
          const deleteStore = deleteTx.objectStore('pending-updates');
          await deleteStore.delete(update.id);

          console.log('[Service Worker] Synced update:', update.id);
        }
      } catch (error) {
        console.error('[Service Worker] Failed to sync update:', update.id, error);
      }
    }

    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        data: { count: pendingUpdates.length }
      });
    });
  } catch (error) {
    console.error('[Service Worker] Update sync failed:', error);
    throw error;
  }
}

// Open IndexedDB for storing offline changes
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('todo-app-offline', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create object stores for pending changes
      if (!db.objectStoreNames.contains('pending-tasks')) {
        db.createObjectStore('pending-tasks', { keyPath: 'id', autoIncrement: true });
      }

      if (!db.objectStoreNames.contains('pending-updates')) {
        db.createObjectStore('pending-updates', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Message handler for communication with clients
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message received:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
});
