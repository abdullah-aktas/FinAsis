import React from 'react';

// Örnek props: { explanation: { features: [{name: 'Gelir', value: 5000, importance: 0.42}, ...], summary: 'En çok etki eden faktör: Gelir' } }
const ExplainabilityBox = ({ explanation }) => {
  if (!explanation || !explanation.features || !explanation.features.length) return null;
  return (
    <div style={{background:'#f8f9fa', borderLeft:'5px solid #1abc9c', borderRadius:8, padding:18, margin:'24px 0', maxWidth:600, marginLeft:'auto', marginRight:'auto'}}>
      <h4 style={{marginBottom:12}}>Model Açıklaması (Explainability)</h4>
      <ul style={{listStyle:'none', padding:0, margin:0}}>
        {explanation.features.map((f, i) => (
          <li key={f.name} style={{marginBottom:6, display:'flex', alignItems:'center'}}>
            <span style={{fontWeight:'bold', minWidth:120}}>{f.name}:</span>
            <span style={{marginLeft:8}}>{f.value}</span>
            <span style={{marginLeft:16, color:'#36a2eb', fontWeight:'bold'}}>Etki: {Math.round(f.importance*100)}%</span>
          </li>
        ))}
      </ul>
      {explanation.summary && <div style={{marginTop:12, color:'#333'}}><b>Özet:</b> {explanation.summary}</div>}
    </div>
  );
};

export default ExplainabilityBox; 