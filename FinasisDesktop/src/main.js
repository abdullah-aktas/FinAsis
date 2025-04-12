const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const url = require('url');
const axios = require('axios');
const log = require('electron-log');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

// Uygulama ayarları
const store = new Store();
const API_URL = 'http://127.0.0.1:8000';
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// Loglama ayarları
log.transports.file.level = 'info';
log.info('Uygulama başlatılıyor...');

// Ana pencere referansı
let mainWindow;
let splashWindow;

// Splash ekranını göster
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 300,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.center();
}

// Ana pencereyi oluştur
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  // Django uygulamasının URL'sini yükle
  // Geliştirme modunda ise local Django sunucusunu, 
  // üretim modunda ise entegre Django sunucusunu kullan
  if (isDev) {
    mainWindow.loadURL(API_URL);
    
    // Geliştirme modunda DevTools'u aç
    mainWindow.webContents.openDevTools();
  } else {
    // Üretim modunda, uygulama içine entegre Flask/Django sunucusunu başlat
    // Bu özellik FinAsis v2'de eklenecektir
    mainWindow.loadURL(API_URL);
  }

  // Pencere hazır olduğunda göster ve splash ekranını kapat
  mainWindow.once('ready-to-show', () => {
    setTimeout(() => {
      if (splashWindow) {
        splashWindow.close();
      }
      mainWindow.show();
    }, 2000); // 2 saniye gecikme ile göster
  });

  // Uygulama kapatıldığında
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Menü oluştur
  const template = [
    {
      label: 'Dosya',
      submenu: [
        {
          label: 'Ana Sayfa',
          click: () => {
            mainWindow.loadURL(API_URL);
          }
        },
        { type: 'separator' },
        {
          label: 'Ayarlar',
          click: () => {
            openSettingsWindow();
          }
        },
        { type: 'separator' },
        {
          label: 'Çıkış',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Düzenle',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'delete' },
        { type: 'separator' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'Görüntüle',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { role: 'resetZoom' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Modüller',
      submenu: [
        {
          label: 'Eğitim',
          click: () => {
            mainWindow.loadURL(`${API_URL}/education/`);
          }
        },
        {
          label: 'Sanal Şirket',
          click: () => {
            mainWindow.loadURL(`${API_URL}/virtual-company/`);
          }
        },
        {
          label: 'AI Asistan',
          click: () => {
            mainWindow.loadURL(`${API_URL}/ai-assistant/`);
          }
        },
        {
          label: 'Blockchain',
          click: () => {
            mainWindow.loadURL(`${API_URL}/blockchain/`);
          }
        },
        {
          label: 'Oyunlar',
          click: () => {
            mainWindow.loadURL(`${API_URL}/game/`);
          }
        }
      ]
    },
    {
      label: 'Yardım',
      submenu: [
        {
          label: 'Hakkında',
          click: () => {
            openAboutWindow();
          }
        },
        {
          label: 'Dokümantasyon',
          click: () => {
            mainWindow.loadURL(`${API_URL}/documents/user-guide/`);
          }
        },
        { type: 'separator' },
        {
          label: 'Güncellemeleri Kontrol Et',
          click: () => {
            autoUpdater.checkForUpdatesAndNotify();
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Ayarlar penceresini aç
function openSettingsWindow() {
  const settingsWindow = new BrowserWindow({
    width: 600,
    height: 400,
    parent: mainWindow,
    modal: true,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  settingsWindow.loadFile(path.join(__dirname, 'settings.html'));
  settingsWindow.once('ready-to-show', () => {
    settingsWindow.show();
  });
}

// Hakkında penceresini aç
function openAboutWindow() {
  const aboutWindow = new BrowserWindow({
    width: 400,
    height: 300,
    parent: mainWindow,
    modal: true,
    show: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  aboutWindow.loadFile(path.join(__dirname, 'about.html'));
  aboutWindow.once('ready-to-show', () => {
    aboutWindow.show();
  });
}

// IPC olaylarını dinle (renderer process'ten gelen mesajlar)
ipcMain.handle('save-data', async (event, data) => {
  try {
    store.set(data.key, data.value);
    return { success: true, message: 'Veri başarıyla kaydedildi.' };
  } catch (error) {
    log.error('Veri kaydetme hatası:', error);
    return { success: false, message: error.message };
  }
});

ipcMain.handle('load-data', async (event, key) => {
  try {
    const value = store.get(key);
    return { success: true, data: value };
  } catch (error) {
    log.error('Veri yükleme hatası:', error);
    return { success: false, message: error.message };
  }
});

ipcMain.handle('start-game', async (event) => {
  try {
    // Oyunu başlatmak için Django API'sine istek gönder
    const response = await axios.post(`${API_URL}/api/games/launch/`, {
      gameType: 'trade_trail_3d'
    });
    return { success: true, data: response.data };
  } catch (error) {
    log.error('Oyun başlatma hatası:', error);
    return { success: false, message: error.message };
  }
});

ipcMain.handle('open-file-dialog', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Excel Dosyaları', extensions: ['xlsx', 'xls'] },
      { name: 'Tüm Dosyalar', extensions: ['*'] }
    ]
  });
  
  if (result.canceled) {
    return { success: false, message: 'İşlem iptal edildi.' };
  }
  
  return { success: true, filePath: result.filePaths[0] };
});

// Uygulamayı başlat
app.whenReady().then(() => {
  createSplashWindow();
  setTimeout(createMainWindow, 1000);
  
  // macOS'ta app.on('activate') olayı
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
  
  // Otomatik güncelleme kontrolü
  if (!isDev) {
    autoUpdater.checkForUpdatesAndNotify();
  }
});

// Tüm pencereler kapatıldığında uygulamayı kapat
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Otomatik güncelleme olayları
autoUpdater.on('update-available', (info) => {
  log.info('Güncelleme mevcut:', info);
  dialog.showMessageBox({
    type: 'info',
    title: 'Güncelleme Mevcut',
    message: `Yeni bir sürüm (${info.version}) mevcut. İndiriliyor...`,
    buttons: ['Tamam']
  });
});

autoUpdater.on('update-downloaded', (info) => {
  log.info('Güncelleme indirildi:', info);
  dialog.showMessageBox({
    type: 'info',
    title: 'Güncelleme Hazır',
    message: 'Güncelleme indirildi. Şimdi yüklemek istiyor musunuz?',
    buttons: ['Şimdi Yükle', 'Daha Sonra'],
    defaultId: 0
  }).then((result) => {
    if (result.response === 0) {
      autoUpdater.quitAndInstall();
    }
  });
});

// Hata yönetimi
process.on('uncaughtException', (error) => {
  log.error('Yakalanmayan hata:', error);
  dialog.showErrorBox(
    'Bir hata oluştu',
    `Beklenmeyen bir hata oluştu: ${error.message}`
  );
}); 