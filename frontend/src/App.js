import React, { useState, useEffect } from 'react';
import MainMenu from './components/MainMenu';
import PrimaryButton from './components/PrimaryButton';
import NotificationSnackbar from './components/NotificationSnackbar';

const pageTitles = {
  home: 'Ana Sayfa',
  ai: 'AI Asistanı',
  blockchain: 'Blockchain',
  education: 'Eğitim',
  games: 'Oyunlaştırma',
  profile: 'Kullanıcı Profili',
};

function App() {
  const [page, setPage] = useState('home');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    document.title = pageTitles[page] || 'FinAsis';
  }, [page]);

  const handleNavigate = (target) => {
    setPage(target);
    setSnackbar({ open: true, message: `${pageTitles[target] || target} sayfasına geçildi.`, severity: 'success' });
  };

  const renderPage = () => {
    switch (page) {
      case 'ai':
        return <div>AI Asistanı Sayfası <PrimaryButton aria-label="AI işlemi" onClick={() => setSnackbar({ open: true, message: 'AI Asistanı kullanıldı!', severity: 'info' })}>AI İşlemi</PrimaryButton></div>;
      case 'blockchain':
        return <div>Blockchain Modülü <PrimaryButton aria-label="Blockchain işlemi" onClick={() => setSnackbar({ open: true, message: 'Blockchain işlemi yapıldı!', severity: 'info' })}>Blockchain İşlemi</PrimaryButton></div>;
      case 'education':
        return <div>Eğitim Modülü <PrimaryButton aria-label="Eğitim işlemi" onClick={() => setSnackbar({ open: true, message: 'Eğitim modülü kullanıldı!', severity: 'info' })}>Eğitim İşlemi</PrimaryButton></div>;
      case 'games':
        return <div>Oyunlaştırma Modülü <PrimaryButton aria-label="Oyunlaştırma işlemi" onClick={() => setSnackbar({ open: true, message: 'Oyunlaştırma işlemi yapıldı!', severity: 'info' })}>Oyunlaştırma İşlemi</PrimaryButton></div>;
      case 'profile':
        return <div>Kullanıcı Profili <PrimaryButton aria-label="Profili güncelle" onClick={() => setSnackbar({ open: true, message: 'Profil güncellendi!', severity: 'info' })}>Profili Güncelle</PrimaryButton></div>;
      default:
        return <div>Ana Sayfa</div>;
    }
  };

  return (
    <div>
      <MainMenu onNavigate={handleNavigate} />
      <div style={{ padding: 24 }}>
        {page !== 'home' && <PrimaryButton aria-label="Ana sayfaya dön" onClick={() => handleNavigate('home')}>Ana Sayfa</PrimaryButton>}
        {renderPage()}
      </div>
      <NotificationSnackbar open={snackbar.open} onClose={() => setSnackbar({ ...snackbar, open: false })} message={snackbar.message} severity={snackbar.severity} />
    </div>
  );
}

export default App; 