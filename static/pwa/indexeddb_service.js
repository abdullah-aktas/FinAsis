/**
 * FinAsis IndexedDB Veri Servisi
 * Bu servis, çevrimdışı mod için veri yönetimini sağlar
 */

class IndexedDBService {
    constructor() {
        this.dbName = 'finasis_offline_db';
        this.dbVersion = 1;
        this.db = null;
        this.stores = {
            pendingRequests: 'pendingRequests',    // Bekleyen istekler
            formData: 'formData',                 // Form verileri
            userPrefs: 'userPreferences'          // Kullanıcı tercihleri
        };
    }

    /**
     * Veritabanını başlatır
     */
    async init() {
        if (this.db) return Promise.resolve(this.db);

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            // Veritabanı ilk kez oluşturulduğunda veya sürümü değiştirildiğinde
            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Bekleyen istekler deposu
                if (!db.objectStoreNames.contains(this.stores.pendingRequests)) {
                    const store = db.createObjectStore(this.stores.pendingRequests, { keyPath: 'id', autoIncrement: true });
                    store.createIndex('timestamp', 'timestamp', { unique: false });
                    store.createIndex('url', 'url', { unique: false });
                    store.createIndex('status', 'status', { unique: false });
                }

                // Form verileri deposu
                if (!db.objectStoreNames.contains(this.stores.formData)) {
                    const store = db.createObjectStore(this.stores.formData, { keyPath: 'id', autoIncrement: true });
                    store.createIndex('formId', 'formId', { unique: false });
                    store.createIndex('timestamp', 'timestamp', { unique: false });
                }

                // Kullanıcı tercihleri deposu
                if (!db.objectStoreNames.contains(this.stores.userPrefs)) {
                    const store = db.createObjectStore(this.stores.userPrefs, { keyPath: 'key' });
                }
            };

            // Veritabanı açıldığında
            request.onsuccess = (event) => {
                this.db = event.target.result;
                console.log('IndexedDB başarıyla açıldı');
                resolve(this.db);
            };

            // Hata durumunda
            request.onerror = (event) => {
                console.error('IndexedDB açılırken hata oluştu:', event.target.error);
                reject(event.target.error);
            };
        });
    }

    /**
     * Bekleyen API isteğini ekler
     * @param {Object} requestData - API isteğinin verileri
     */
    async addPendingRequest(requestData) {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.pendingRequests], 'readwrite');
            const store = transaction.objectStore(this.stores.pendingRequests);

            const request = store.add({
                url: requestData.url,
                method: requestData.method || 'POST',
                headers: requestData.headers || {},
                data: requestData.data,
                timestamp: new Date().getTime(),
                status: 'pending'
            });

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Bekleyen tüm API isteklerini getirir
     */
    async getPendingRequests() {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.pendingRequests], 'readonly');
            const store = transaction.objectStore(this.stores.pendingRequests);
            const index = store.index('status');
            const request = index.getAll('pending');

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Bekleyen bir API isteğini günceller
     * @param {number} id - İsteğin ID'si
     * @param {Object} updateData - Güncellenecek veri
     */
    async updatePendingRequest(id, updateData) {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.pendingRequests], 'readwrite');
            const store = transaction.objectStore(this.stores.pendingRequests);
            const request = store.get(id);

            request.onsuccess = () => {
                const data = request.result;
                if (!data) {
                    reject(new Error('İstek bulunamadı'));
                    return;
                }

                // Verileri güncelle
                Object.assign(data, updateData);
                data.lastUpdated = new Date().getTime();

                const updateRequest = store.put(data);
                updateRequest.onsuccess = () => resolve(updateRequest.result);
                updateRequest.onerror = () => reject(updateRequest.error);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Bekleyen bir API isteğini siler
     * @param {number} id - İsteğin ID'si
     */
    async deletePendingRequest(id) {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.pendingRequests], 'readwrite');
            const store = transaction.objectStore(this.stores.pendingRequests);
            const request = store.delete(id);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Form verilerini kaydeder
     * @param {string} formId - Form kimliği
     * @param {Object} formData - Form verileri
     */
    async saveFormData(formId, formData) {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.formData], 'readwrite');
            const store = transaction.objectStore(this.stores.formData);

            const request = store.add({
                formId,
                data: formData,
                timestamp: new Date().getTime()
            });

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Form verilerini getirir
     * @param {string} formId - Form kimliği
     */
    async getFormData(formId) {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.formData], 'readonly');
            const store = transaction.objectStore(this.stores.formData);
            const index = store.index('formId');
            const request = index.get(formId);

            request.onsuccess = () => resolve(request.result ? request.result.data : null);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Kullanıcı tercihlerini kaydeder
     * @param {string} key - Tercih anahtarı
     * @param {*} value - Tercih değeri
     */
    async setUserPreference(key, value) {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.userPrefs], 'readwrite');
            const store = transaction.objectStore(this.stores.userPrefs);

            const request = store.put({
                key,
                value,
                updatedAt: new Date().getTime()
            });

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Kullanıcı tercihini getirir
     * @param {string} key - Tercih anahtarı
     */
    async getUserPreference(key) {
        await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.stores.userPrefs], 'readonly');
            const store = transaction.objectStore(this.stores.userPrefs);
            const request = store.get(key);

            request.onsuccess = () => resolve(request.result ? request.result.value : null);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Tüm bekleyen istekleri senkronize etmeye çalışır
     */
    async syncAllPendingRequests() {
        const pendingRequests = await this.getPendingRequests();
        const results = [];

        for (const request of pendingRequests) {
            try {
                const response = await fetch(request.url, {
                    method: request.method,
                    headers: {
                        'Content-Type': 'application/json',
                        ...request.headers
                    },
                    body: JSON.stringify(request.data)
                });

                if (response.ok) {
                    await this.deletePendingRequest(request.id);
                    results.push({
                        id: request.id,
                        success: true,
                        response: await response.json()
                    });
                } else {
                    await this.updatePendingRequest(request.id, {
                        lastAttempt: new Date().getTime(),
                        lastError: `HTTP error: ${response.status}`
                    });
                    results.push({
                        id: request.id,
                        success: false,
                        error: `HTTP error: ${response.status}`
                    });
                }
            } catch (error) {
                await this.updatePendingRequest(request.id, {
                    lastAttempt: new Date().getTime(),
                    lastError: error.message
                });
                results.push({
                    id: request.id,
                    success: false,
                    error: error.message
                });
            }
        }

        return results;
    }
}

// Global değişken olarak ekle
window.indexedDBService = new IndexedDBService(); 