import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Service worker'ı kaydet
serviceWorker.register({
  onSuccess: () => console.log('Service Worker başarıyla kaydedildi'),
  onUpdate: () => console.log('Yeni Service Worker mevcut'),
  onOffline: () => console.log('Uygulama çevrimdışı modda çalışıyor')
}); 