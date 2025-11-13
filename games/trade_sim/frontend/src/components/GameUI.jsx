import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '@utils/store';
import { AudioManager } from '@utils/AudioManager';
import HUD from './HUD';
import Inventory from './Inventory';
import QuestPanel from './QuestPanel';
import ChatPanel from './ChatPanel';
import MapPanel from './MapPanel';
import SettingsPanel from './SettingsPanel';
import Minimap from './Minimap';
import NotificationPanel from './NotificationPanel';
import TouchControls from './TouchControls';

export default function GameUI() {
  const { player, uiState, toggleUI } = useGameStore();
  const [showMenu, setShowMenu] = useState(false);

  const handleMenuToggle = () => {
    AudioManager.getInstance().playSound('click');
    setShowMenu(!showMenu);
  };

  return (
    <div className="fixed inset-0 pointer-events-none">
      {/* Top HUD */}
      <HUD />

      {/* Minimap - Bottom right */}
      <div className="absolute bottom-4 right-4 pointer-events-auto">
        <Minimap />
      </div>

      {/* Quick actions - Bottom left */}
      <div className="absolute bottom-4 left-4 flex space-x-2 pointer-events-auto">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => {
            AudioManager.getInstance().playSound('click');
            toggleUI('showInventory');
          }}
          className="w-14 h-14 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 flex items-center justify-center text-2xl hover:bg-white/20 transition-colors"
          title="Envanter (I)"
        >
          🎒
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => {
            AudioManager.getInstance().playSound('click');
            toggleUI('showQuests');
          }}
          className="w-14 h-14 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 flex items-center justify-center text-2xl hover:bg-white/20 transition-colors"
          title="Görevler (Q)"
        >
          📋
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => {
            AudioManager.getInstance().playSound('click');
            toggleUI('showMap');
          }}
          className="w-14 h-14 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 flex items-center justify-center text-2xl hover:bg-white/20 transition-colors"
          title="Harita (M)"
        >
          🗺️
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => {
            AudioManager.getInstance().playSound('click');
            toggleUI('showChat');
          }}
          className="w-14 h-14 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 flex items-center justify-center text-2xl hover:bg-white/20 transition-colors"
          title="Sohbet (C)"
        >
          💬
        </motion.button>
      </div>

      {/* Menu button - Top left */}
      <div className="absolute top-4 left-4 pointer-events-auto">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleMenuToggle}
          className="w-12 h-12 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 flex items-center justify-center text-2xl hover:bg-white/20 transition-colors"
        >
          ☰
        </motion.button>
      </div>

      {/* Panels */}
      <AnimatePresence>
        {uiState.showInventory && <Inventory />}
        {uiState.showQuests && <QuestPanel />}
        {uiState.showMap && <MapPanel />}
        {uiState.showChat && <ChatPanel />}
        {uiState.showSettings && <SettingsPanel />}
      </AnimatePresence>

      {/* Menu overlay */}
      <AnimatePresence>
        {showMenu && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm pointer-events-auto"
            onClick={handleMenuToggle}
          >
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", damping: 25 }}
              className="absolute left-0 top-0 h-full w-80 bg-game-darker/95 backdrop-blur-md border-r border-white/10 p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-2xl font-bold gradient-text mb-8">
                Menü
              </h2>

              <div className="space-y-4">
                <button
                  onClick={() => {
                    AudioManager.getInstance().playSound('click');
                    toggleUI('showSettings');
                    setShowMenu(false);
                  }}
                  className="w-full btn-secondary text-left"
                >
                  ⚙️ Ayarlar
                </button>

                <button
                  onClick={() => {
                    AudioManager.getInstance().playSound('click');
                    toggleUI('showLeaderboard');
                    setShowMenu(false);
                  }}
                  className="w-full btn-secondary text-left"
                >
                  🏆 Liderlik Tablosu
                </button>

                <button
                  onClick={() => AudioManager.getInstance().playSound('click')}
                  className="w-full btn-secondary text-left"
                >
                  👥 Arkadaşlar
                </button>

                <button
                  onClick={() => AudioManager.getInstance().playSound('click')}
                  className="w-full btn-secondary text-left"
                >
                  🏰 Lonca
                </button>

                <button
                  onClick={() => AudioManager.getInstance().playSound('click')}
                  className="w-full btn-secondary text-left"
                >
                  ℹ️ Yardım
                </button>

                <button
                  onClick={() => AudioManager.getInstance().playSound('click')}
                  className="w-full btn-secondary text-left bg-red-500/20 hover:bg-red-500/30"
                >
                  🚪 Ana Menüye Dön
                </button>
              </div>

              {/* Player info */}
              <div className="absolute bottom-6 left-6 right-6">
                <div className="card">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-game-accent to-game-purple rounded-full flex items-center justify-center text-xl">
                      👤
                    </div>
                    <div>
                      <div className="font-bold text-white">
                        {player.username}
                      </div>
                      <div className="text-sm text-gray-400">
                        Seviye {player.level}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Notifications */}
      <NotificationPanel />

      {/* Touch Controls for Mobile */}
      <TouchControls />

      {/* Keyboard shortcuts hint */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 pointer-events-none">
        <div className="glass px-4 py-2 rounded-full text-sm text-gray-400">
          <span className="text-game-accent">I</span>:Envanter
          <span className="mx-2">•</span>
          <span className="text-game-accent">Q</span>:Görevler
          <span className="mx-2">•</span>
          <span className="text-game-accent">M</span>:Harita
          <span className="mx-2">•</span>
          <span className="text-game-accent">C</span>:Sohbet
        </div>
      </div>
    </div>
  );
}
