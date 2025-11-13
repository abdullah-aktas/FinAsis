import React from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '@utils/store';

export default function MapPanel() {
  const { gameState, toggleUI } = useGameStore();
  const cities = gameState.cities || [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="absolute inset-0 flex items-center justify-center pointer-events-auto p-4"
      onClick={() => toggleUI('showMap')}
    >
      <motion.div
        className="glass rounded-2xl w-full max-w-6xl h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className="text-3xl font-bold gradient-text">
            🗺️ Dünya Haritası
          </h2>
          <button
            onClick={() => toggleUI('showMap')}
            className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        <div className="relative w-full h-[calc(100%-80px)] bg-gradient-to-br from-blue-900/20 to-green-900/20">
          {/* Map grid */}
          <svg className="absolute inset-0 w-full h-full">
            <defs>
              <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                <path
                  d="M 50 0 L 0 0 0 50"
                  fill="none"
                  stroke="rgba(255,255,255,0.05)"
                  strokeWidth="1"
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>

          {/* Cities */}
          {cities.map((city, index) => {
            const x = ((city.coordinates?.x || 0) + 50) * 10;
            const y = ((city.coordinates?.y || 0) + 50) * 10;

            return (
              <motion.div
                key={city.id}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="absolute cursor-pointer group"
                style={{
                  left: `${x}px`,
                  top: `${y}px`,
                  transform: 'translate(-50%, -50%)',
                }}
              >
                {/* City marker */}
                <motion.div
                  whileHover={{ scale: 1.2 }}
                  className="w-12 h-12 bg-gradient-to-br from-game-accent to-game-purple rounded-full flex items-center justify-center text-2xl shadow-lg"
                >
                  🏙️
                </motion.div>

                {/* City name tooltip */}
                <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  <div className="glass px-3 py-2 rounded-lg">
                    <div className="font-bold text-white text-sm">
                      {city.name}
                    </div>
                    <div className="text-xs text-gray-400">
                      {city.sectors?.join(', ')}
                    </div>
                  </div>
                </div>

                {/* Pulse animation */}
                <motion.div
                  className="absolute inset-0 bg-game-accent rounded-full"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 0, 0.5],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                  }}
                />
              </motion.div>
            );
          })}

          {/* Legend */}
          <div className="absolute bottom-4 left-4 glass rounded-lg p-4">
            <div className="text-sm font-bold text-white mb-2">Açıklama</div>
            <div className="space-y-2 text-xs text-gray-400">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-game-accent rounded-full" />
                <span>Şehir</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-yellow-500 rounded-full" />
                <span>Bulunduğun konum</span>
              </div>
            </div>
          </div>

          {/* Zoom controls */}
          <div className="absolute bottom-4 right-4 flex flex-col space-y-2">
            <button className="w-10 h-10 glass rounded-lg flex items-center justify-center hover:bg-white/20 transition-colors">
              +
            </button>
            <button className="w-10 h-10 glass rounded-lg flex items-center justify-center hover:bg-white/20 transition-colors">
              −
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
