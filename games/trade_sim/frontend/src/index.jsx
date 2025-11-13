import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Loading progress simulation
const loadingProgress = document.getElementById('loading-progress');
const loadingText = document.getElementById('loading-text');

let progress = 0;
const interval = setInterval(() => {
  progress += Math.random() * 15;
  if (progress >= 100) {
    progress = 100;
    clearInterval(interval);
    setTimeout(() => {
      document.getElementById('loading-screen').classList.add('hidden');
    }, 500);
  }
  loadingProgress.style.width = `${progress}%`;
  loadingText.textContent = progress < 100 ? 'Oyun yükleniyor...' : 'Hazır!';
}, 200);

// Mount React app
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
