import React from 'react';
const npcs = [
  { name: 'NPC_1', city: 'Mardin' },
  { name: 'NPC_2', city: 'Izmir' },
  { name: 'NPC_3', city: 'Corum' },
];
const decisions = ['Al', 'Sat', 'Bekle'];
export default function NPCPanel() {
  return (
    <div className="bg-white rounded-lg shadow p-4 w-64">
      <h2 className="font-bold text-lg mb-2">AI NPC'ler</h2>
      <ul className="text-sm mb-2">
        {npcs.map((npc, i) => (
          <li key={npc.name}>{npc.name} ({npc.city}) - Karar: {decisions[i % decisions.length]}</li>
        ))}
      </ul>
      <div className="text-xs text-gray-500">Demo: Fiyat analizi ve ticaret kararı</div>
    </div>
  );
}
