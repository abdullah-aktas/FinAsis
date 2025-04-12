const { contextBridge, ipcRenderer } = require('electron');

// IPC fonksiyonlarını web içeriğine açıyoruz
contextBridge.exposeInMainWorld('electron', {
  // Veri yönetimi
  saveData: (data) => ipcRenderer.invoke('save-data', data),
  loadData: (key) => ipcRenderer.invoke('load-data', key),
  
  // Oyun entegrasyonu
  startGame: () => ipcRenderer.invoke('start-game'),
  
  // Dosya sistemi işlemleri
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  
  // Uygulama bilgileri
  getAppVersion: () => process.env.npm_package_version,
  
  // Django API istekleri için CSRF token'ını alabilme
  getCsrfToken: () => {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  }
}); 