import React, { useState } from 'react';
import QrReader from 'react-qr-reader';
import axios from 'axios';

const QrScanner = () => {
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [scanning, setScanning] = useState(true);

  const handleScan = (data) => {
    if (data && scanning) {
      setScanning(false);
      // QR kodu backend'e gönder
      axios.post('/api/qr-reward/', { code: data })
        .then(res => {
          setResult(res.data.message || JSON.stringify(res.data));
        })
        .catch(err => {
          setError('QR kod geçersiz veya ödül bulunamadı.');
        });
    }
  };

  const handleError = (err) => {
    setError('Kamera hatası: ' + err);
  };

  const resetScanner = () => {
    setResult('');
    setError('');
    setScanning(true);
  };

  return (
    <div className="card" style={{ maxWidth: 400, margin: '0 auto' }}>
      <h3>QR Kod ile Görev/Ödül Topla</h3>
      {scanning && (
        <QrReader
          delay={300}
          onError={handleError}
          onScan={handleScan}
          style={{ width: '100%', borderRadius: 12, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}
        />
      )}
      {result && (
        <div style={{ marginTop: 16 }}>
          <p style={{ color: '#059669', fontWeight: 500, fontSize: 16 }}><b>Sonuç:</b> {result}</p>
          <button onClick={resetScanner}>Tekrar Tara</button>
        </div>
      )}
      {error && (
        <div style={{ color: '#dc2626', marginTop: 16 }}>
          <p>{error}</p>
          <button onClick={resetScanner}>Tekrar Dene</button>
        </div>
      )}
    </div>
  );
};

export default QrScanner; 