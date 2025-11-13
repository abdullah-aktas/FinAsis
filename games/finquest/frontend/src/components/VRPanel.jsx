import React, { useState } from 'react';
export default function VRPanel() {
  const [enabled, setEnabled] = useState(false);
  return (
    <div className="bg-white rounded-lg shadow p-4 w-64">
      <h2 className="font-bold text-lg mb-2">VR Modu</h2>
      <button
        className={`px-4 py-2 rounded font-bold ${enabled ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
        onClick={() => setEnabled(e => !e)}
      >
        {enabled ? 'VR Açık' : 'VR Aç'}
      </button>
      <div className="mt-2 text-sm text-gray-600">Durum: {enabled ? 'Açık' : 'Kapalı'}</div>
    </div>
  );
}
