import React from 'react';
const tiles = Array.from({ length: 30 }, (_, i) => ({ x: i % 6, y: Math.floor(i / 6), type: (i % 5 === 0 ? 'market' : 'house') }));
export default function WorldPanel() {
  return (
    <div className="bg-white rounded-lg shadow p-4 w-64">
      <h2 className="font-bold text-lg mb-2">Dünya Haritası</h2>
      <div className="grid grid-cols-6 gap-1 mb-2">
        {tiles.map((tile, i) => (
          <div key={i} className={`w-6 h-6 rounded ${tile.type === 'market' ? 'bg-yellow-400' : 'bg-gray-300'}`}></div>
        ))}
      </div>
      <div className="text-xs text-gray-500">Demo: Prosedürel harita ({tiles.length} tile)</div>
    </div>
  );
}
