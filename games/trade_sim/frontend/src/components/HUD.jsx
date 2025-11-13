import React from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '@utils/store';

export default function HUD() {
  const { player, networkState } = useGameStore();

  return (
    <div className="absolute top-4 right-4 space-y-3 pointer-events-auto">
      {/* Player stats */}
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        className="glass rounded-lg p-4 min-w-[200px]"
      >
        {/* Coins */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-yellow-400">💰</span>
          <span className="font-bold text-white">
            {player.coins?.toLocaleString() || 0}
          </span>
        </div>

        {/* Gems */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-purple-400">💎</span>
          <span className="font-bold text-white">
            {player.gems || 0}
          </span>
        </div>

        {/* Score */}
        <div className="flex items-center justify-between">
          <span className="text-blue-400">⭐</span>
          <span className="font-bold text-white">
            {player.score?.toLocaleString() || 0}
          </span>
        </div>
      </motion.div>

      {/* Level and XP */}
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
        className="glass rounded-lg p-4"
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">Seviye</span>
          <span className="font-bold text-white text-lg">
            {player.level || 1}
          </span>
        </div>
        
        {/* XP Bar */}
        <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-game-accent to-game-purple"
            initial={{ width: 0 }}
            animate={{ width: '65%' }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
        <div className="text-xs text-gray-400 mt-1 text-right">
          650 / 1000 XP
        </div>
      </motion.div>

      {/* Character needs */}
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-lg p-4"
      >
        {/* Energy */}
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-400">⚡ Enerji</span>
            <span className="text-xs text-white font-bold">
              {player.needs?.energy || 100}%
            </span>
          </div>
          <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500"
              style={{ width: `${player.needs?.energy || 100}%` }}
            />
          </div>
        </div>

        {/* Happiness */}
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-400">😊 Mutluluk</span>
            <span className="text-xs text-white font-bold">
              {player.needs?.happiness || 100}%
            </span>
          </div>
          <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-yellow-500"
              style={{ width: `${player.needs?.happiness || 100}%` }}
            />
          </div>
        </div>

        {/* Hunger */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-400">🍖 Açlık</span>
            <span className="text-xs text-white font-bold">
              {player.needs?.hunger || 100}%
            </span>
          </div>
          <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-orange-500"
              style={{ width: `${player.needs?.hunger || 100}%` }}
            />
          </div>
        </div>
      </motion.div>

      {/* Network status */}
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
        className="glass rounded-lg p-3"
      >
        <div className="flex items-center space-x-2">
          <span
            className={`w-2 h-2 rounded-full ${
              networkState.connected ? 'bg-green-500' : 'bg-red-500'
            } animate-pulse`}
          />
          <span className="text-xs text-gray-400">
            {networkState.connected ? 'Çevrimiçi' : 'Bağlantı yok'}
          </span>
        </div>
        {networkState.connected && (
          <div className="text-xs text-gray-500 mt-1">
            {networkState.latency}ms • {networkState.playersOnline} oyuncu
          </div>
        )}
      </motion.div>
    </div>
  );
}
