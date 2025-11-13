import React, { useState } from 'react';
import VRPanel from './components/VRPanel';
import NFTPanel from './components/NFTPanel';
import NPCPanel from './components/NPCPanel';
import WorldPanel from './components/WorldPanel';
import './App.css';

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-blue-300 flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-6">FinQuest 3D Web & Mobil</h1>
      <div className="flex flex-wrap gap-6 justify-center">
        <VRPanel />
        <NFTPanel />
        <NPCPanel />
        <WorldPanel />
      </div>
      <footer className="mt-10 text-gray-500">Made with ❤️ by FinAsis Team</footer>
    </div>
  );
}
