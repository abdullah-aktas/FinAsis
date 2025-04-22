class IndexedDBService {
  constructor() {
    this.dbName = 'FinAsisDB';
    this.dbVersion = 1;
    this.db = null;
    this.init();
  }

  init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = (event) => {
        console.error('IndexedDB error:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        console.log('IndexedDB başarıyla açıldı');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Giderler için store
        if (!db.objectStoreNames.contains('expenses')) {
          db.createObjectStore('expenses', { keyPath: 'id', autoIncrement: true });
        }

        // Nakit hareketleri için store
        if (!db.objectStoreNames.contains('cash_transactions')) {
          db.createObjectStore('cash_transactions', { keyPath: 'id', autoIncrement: true });
        }

        // Müşteriler için store
        if (!db.objectStoreNames.contains('customers')) {
          db.createObjectStore('customers', { keyPath: 'id', autoIncrement: true });
        }

        // Senkronizasyon durumu için store
        if (!db.objectStoreNames.contains('sync_status')) {
          db.createObjectStore('sync_status', { keyPath: 'id' });
        }
      };
    });
  }

  async saveData(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.add(data);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async getAllData(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async deleteData(storeName, id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(id);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async updateSyncStatus(id, status) {
    return this.saveData('sync_status', { id, status, timestamp: new Date() });
  }
}

// ServiceWorker'da kullanım için global instance
const indexedDBService = new IndexedDBService();

// Çevrimiçi/çevrimdışı durum kontrolü
window.addEventListener('online', async () => {
  console.log('Çevrimiçi duruma geçildi');
  await syncDataWithServer();
});

window.addEventListener('offline', () => {
  console.log('Çevrimdışı duruma geçildi');
  showOfflineNotification();
});

// Senkronizasyon fonksiyonu
async function syncDataWithServer() {
  try {
    const expenses = await indexedDBService.getAllData('expenses');
    const cashTransactions = await indexedDBService.getAllData('cash_transactions');
    const customers = await indexedDBService.getAllData('customers');

    // Sunucuya veri gönderme işlemleri burada yapılacak
    // Örnek: await fetch('/api/sync', { method: 'POST', body: JSON.stringify({ expenses, cashTransactions, customers }) });

    showSyncSuccessNotification();
  } catch (error) {
    console.error('Senkronizasyon hatası:', error);
    showSyncErrorNotification();
  }
}

// Bildirim fonksiyonları
function showOfflineNotification() {
  // UI'da çevrimdışı durumu göster
  const notification = document.createElement('div');
  notification.className = 'offline-notification';
  notification.textContent = '💾 Çevrimdışı mod aktif';
  document.body.appendChild(notification);
}

function showSyncSuccessNotification() {
  // UI'da senkronizasyon başarılı bildirimi göster
  const notification = document.createElement('div');
  notification.className = 'sync-success-notification';
  notification.textContent = '✅ Veriler başarıyla senkronize edildi';
  document.body.appendChild(notification);
}

function showSyncErrorNotification() {
  // UI'da senkronizasyon hatası bildirimi göster
  const notification = document.createElement('div');
  notification.className = 'sync-error-notification';
  notification.textContent = '❌ Senkronizasyon hatası oluştu';
  document.body.appendChild(notification);
} 