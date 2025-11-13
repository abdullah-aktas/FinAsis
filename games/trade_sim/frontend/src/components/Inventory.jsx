import React from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '@utils/store';

export default function Inventory() {
  const { player, toggleUI } = useGameStore();
  const inventory = player.inventory || [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="absolute inset-0 flex items-center justify-center pointer-events-auto"
      onClick={() => toggleUI('showInventory')}
    >
      <motion.div
        className="glass rounded-2xl p-6 w-full max-w-4xl max-h-[80vh] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold gradient-text">
            🎒 Envanter
          </h2>
          <button
            onClick={() => toggleUI('showInventory')}
            className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        {/* Inventory grid */}
        <div className="grid grid-cols-4 md:grid-cols-6 gap-3">
          {inventory.length > 0 ? (
            inventory.map((item, index) => (
              <motion.div
                key={index}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="card cursor-pointer aspect-square flex flex-col items-center justify-center p-3"
              >
                <div className="text-3xl mb-2">{item.icon || '📦'}</div>
                <div className="text-xs text-center text-white font-semibold">
                  {item.name}
                </div>
                {item.quantity > 1 && (
                  <div className="absolute top-2 right-2 bg-game-accent text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {item.quantity}
                  </div>
                )}
              </motion.div>
            ))
          ) : (
            // Empty slots
            Array.from({ length: 24 }).map((_, index) => (
              <div
                key={index}
                className="aspect-square bg-white/5 rounded-lg border border-white/10"
              />
            ))
          )}
        </div>

        {/* Inventory stats */}
        <div className="mt-6 flex items-center justify-between text-sm text-gray-400">
          <span>{inventory.length} / 100 eşya</span>
          <span>Toplam değer: {inventory.reduce((sum, item) => sum + (item.value || 0), 0).toLocaleString()} 💰</span>
        </div>
      </motion.div>
    </motion.div>
  );
}
