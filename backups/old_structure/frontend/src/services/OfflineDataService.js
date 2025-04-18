class OfflineDataService {
  static DB_NAME = 'finasis-offline-db';
  static DB_VERSION = 1;

  static async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // İşlemler için store
        if (!db.objectStoreNames.contains('transactions')) {
          const transactionStore = db.createObjectStore('transactions', { keyPath: 'id' });
          transactionStore.createIndex('date', 'date', { unique: false });
          transactionStore.createIndex('syncStatus', 'syncStatus', { unique: false });
        }

        // Bütçeler için store
        if (!db.objectStoreNames.contains('budgets')) {
          const budgetStore = db.createObjectStore('budgets', { keyPath: 'id' });
          budgetStore.createIndex('month', 'month', { unique: true });
          budgetStore.createIndex('syncStatus', 'syncStatus', { unique: false });
        }
      };
    });
  }

  static async saveTransaction(transaction) {
    const db = await this.initDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['transactions'], 'readwrite');
      const store = transaction.objectStore('transactions');
      const request = store.put({
        ...transaction,
        syncStatus: 'pending',
        lastModified: new Date().toISOString()
      });

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  static async getPendingTransactions() {
    const db = await this.initDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['transactions'], 'readonly');
      const store = transaction.objectStore('transactions');
      const index = store.index('syncStatus');
      const request = index.getAll('pending');

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  static async markTransactionAsSynced(id) {
    const db = await this.initDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(['transactions'], 'readwrite');
      const store = transaction.objectStore('transactions');
      const request = store.get(id);

      request.onsuccess = () => {
        const data = request.result;
        data.syncStatus = 'synced';
        store.put(data);
        resolve();
      };
      request.onerror = () => reject(request.error);
    });
  }

  static async syncWithServer() {
    try {
      const pendingTransactions = await this.getPendingTransactions();
      
      for (const transaction of pendingTransactions) {
        try {
          const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(transaction)
          });

          if (response.ok) {
            await this.markTransactionAsSynced(transaction.id);
          }
        } catch (error) {
          console.error('Senkronizasyon hatası:', error);
        }
      }
    } catch (error) {
      console.error('Offline veri senkronizasyonu başarısız:', error);
    }
  }
}

export default OfflineDataService; 