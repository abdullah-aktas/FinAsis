import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

const API_URL = '/ai-assistant/ai-models/';

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleString();
}

const ModelPerformanceDashboard = () => {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(API_URL, { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setModels(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Veri alınamadı: ' + err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div style={{color:'red'}}>{error}</div>;
  if (!models.length) return <div>Model kaydı bulunamadı.</div>;

  // Doğruluk trendi için verileri hazırla
  const sorted = [...models].sort((a, b) => new Date(a.last_trained) - new Date(b.last_trained));
  const chartData = {
    labels: sorted.map(m => formatDate(m.last_trained)),
    datasets: [
      {
        label: 'Doğruluk Oranı',
        data: sorted.map(m => m.accuracy),
        fill: false,
        borderColor: '#36a2eb',
        tension: 0.2,
      },
    ],
  };

  return (
    <div style={{background:'#fff', borderRadius:8, padding:24, maxWidth:900, margin:'32px auto', boxShadow:'0 2px 8px #eee'}}>
      <h3>Model Performans Trendleri</h3>
      <Line data={chartData} options={{responsive:true, plugins:{legend:{display:true, position:'top'}}}} />
      <h4 style={{marginTop:32}}>Model Versiyon Geçmişi</h4>
      <div style={{overflowX:'auto'}}>
        <table style={{width:'100%', borderCollapse:'collapse', marginTop:12}}>
          <thead>
            <tr style={{background:'#f5f5f5'}}>
              <th>Model Adı</th>
              <th>Tip</th>
              <th>Versiyon</th>
              <th>Doğruluk</th>
              <th>Eğitim Tarihi</th>
              <th>Parametreler</th>
            </tr>
          </thead>
          <tbody>
            {models.map(m => (
              <tr key={m.id}>
                <td>{m.name}</td>
                <td>{m.model_type}</td>
                <td>{m.version}</td>
                <td>{m.accuracy ? m.accuracy.toFixed(4) : '-'}</td>
                <td>{formatDate(m.last_trained)}</td>
                <td><pre style={{fontSize:12, maxWidth:300, whiteSpace:'pre-wrap'}}>{JSON.stringify(m.parameters, null, 2)}</pre></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ModelPerformanceDashboard; 