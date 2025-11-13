import React from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '@utils/store';

export default function QuestPanel() {
  const { gameState, toggleUI } = useGameStore();
  const quests = gameState.activeQuests || [];

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 50 }}
      className="absolute right-4 top-1/2 -translate-y-1/2 w-96 pointer-events-auto"
    >
      <div className="glass rounded-2xl p-6 max-h-[70vh] overflow-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold gradient-text">
            📋 Görevler
          </h2>
          <button
            onClick={() => toggleUI('showQuests')}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        {quests.length > 0 ? (
          <div className="space-y-4">
            {quests.map((quest, index) => (
              <motion.div
                key={quest.id || index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-bold text-white text-lg">
                    {quest.title || quest.name}
                  </h3>
                  <span className="text-xs px-2 py-1 bg-game-accent/20 text-game-accent rounded-full">
                    {quest.type || 'main'}
                  </span>
                </div>
                
                <p className="text-sm text-gray-400 mb-3">
                  {quest.description}
                </p>

                {/* Progress bar */}
                {quest.progress && quest.requirements && (
                  <div className="mb-3">
                    {Object.entries(quest.requirements).map(([key, target]) => {
                      const current = quest.progress[key] || 0;
                      const percentage = (current / target) * 100;
                      
                      return (
                        <div key={key} className="mb-2">
                          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                            <span>{key}</span>
                            <span>{current} / {target}</span>
                          </div>
                          <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                            <motion.div
                              className="h-full bg-gradient-to-r from-game-accent to-game-purple"
                              initial={{ width: 0 }}
                              animate={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Rewards */}
                {quest.rewards && (
                  <div className="flex items-center space-x-3 text-sm">
                    <span className="text-gray-400">Ödüller:</span>
                    {quest.rewards.coins && (
                      <span className="text-yellow-400">
                        💰 {quest.rewards.coins}
                      </span>
                    )}
                    {quest.rewards.xp && (
                      <span className="text-blue-400">
                        ⭐ {quest.rewards.xp} XP
                      </span>
                    )}
                    {quest.rewards.badge && (
                      <span className="text-purple-400">
                        🏆 {quest.rewards.badge}
                      </span>
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📭</div>
            <p className="text-gray-400">Aktif görev yok</p>
            <p className="text-sm text-gray-500 mt-2">
              Şehirleri ziyaret ederek yeni görevler bulabilirsin!
            </p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
