import React from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '@utils/store';

export default function Minimap() {
  const { player, gameState } = useGameStore();
  const cities = gameState.cities || [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass rounded-lg p-3 w-48 h-48"
    >
      <div className="text-xs font-bold text-gray-400 mb-2">Mini Harita</div>
      
      <div className="relative w-full h-[calc(100%-20px)] bg-gradient-to-br from-blue-900/30 to-green-900/30 rounded-lg overflow-hidden">
        {/* Grid */}
        <svg className="absolute inset-0 w-full h-full opacity-20">
          <defs>
            <pattern id="minimap-grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <path
                d="M 20 0 L 0 0 0 20"
                fill="none"
                stroke="white"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#minimap-grid)" />
        </svg>

        {/* Cities */}
        {cities.slice(0, 5).map((city) => {
          const x = ((city.coordinates?.x || 0) + 50) / 100 * 100;
          const y = ((city.coordinates?.y || 0) + 50) / 100 * 100;
          
          return (
            <div
              key={city.id}
              className="absolute w-2 h-2 bg-game-accent rounded-full"
              style={{
                left: `${x}%`,
                top: `${y}%`,
                transform: 'translate(-50%, -50%)',
              }}
            />
          );
        })}

        {/* Player position */}
        <motion.div
          className="absolute w-3 h-3 bg-yellow-400 rounded-full border-2 border-white"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)',
          }}
          animate={{
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
          }}
        />

        {/* Compass */}
        <div className="absolute top-1 right-1 text-xs text-white font-bold">
          N
        </div>
      </div>
    </motion.div>
  );
}
