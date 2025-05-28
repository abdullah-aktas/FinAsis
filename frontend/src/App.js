import React from 'react';
import logo from './logo.svg';
import './App.css';
import ModelPerformanceDashboard from './ModelPerformanceDashboard';
import MapView from './components/MapView';
import QrScanner from './components/QrScanner';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h2>FinAsis Model Performans Dashboard</h2>
        <ModelPerformanceDashboard />
      </header>
      <main style={{ padding: '2rem' }}>
        <h2>Şehirler ve Pazarlar Haritası</h2>
        <MapView />
        <hr style={{ margin: '2rem 0' }} />
        <QrScanner />
      </main>
    </div>
  );
}

export default App;
