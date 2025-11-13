import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '@utils/store';
import { AudioManager } from '@utils/AudioManager';

export default function SettingsPanel() {
  const { toggleUI } = useGameStore();
  const audioManager = AudioManager.getInstance();
  
  const [settings, setSettings] = useState({
    masterVolume: 100,
    musicVolume: 50,
    sfxVolume: 70,
    graphics: 'high',
    showFPS: false,
    language: 'tr',
  });

  const handleVolumeChange = (type, value) => {
    setSettings(prev => ({ ...prev, [type]: value }));
    
    const normalizedValue = value / 100;
    if (type === 'masterVolume') {
      audioManager.setMasterVolume(normalizedValue);
    } else if (type === 'musicVolume') {
      audioManager.setMusicVolume(normalizedValue);
    } else if (type === 'sfxVolume') {
      audioManager.setSFXVolume(normalizedValue);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="absolute inset-0 flex items-center justify-center pointer-events-auto"
      onClick={() => toggleUI('showSettings')}
    >
      <motion.div
        className="glass rounded-2xl p-6 w-full max-w-2xl max-h-[80vh] overflow-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold gradient-text">
            ⚙️ Ayarlar
          </h2>
          <button
            onClick={() => toggleUI('showSettings')}
            className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* Audio Settings */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4">🔊 Ses Ayarları</h3>
            
            <div className="space-y-4">
              {/* Master Volume */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-gray-400">Ana Ses</label>
                  <span className="text-sm text-white font-bold">{settings.masterVolume}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={settings.masterVolume}
                  onChange={(e) => handleVolumeChange('masterVolume', parseInt(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>

              {/* Music Volume */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-gray-400">Müzik</label>
                  <span className="text-sm text-white font-bold">{settings.musicVolume}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={settings.musicVolume}
                  onChange={(e) => handleVolumeChange('musicVolume', parseInt(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>

              {/* SFX Volume */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-gray-400">Ses Efektleri</label>
                  <span className="text-sm text-white font-bold">{settings.sfxVolume}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={settings.sfxVolume}
                  onChange={(e) => handleVolumeChange('sfxVolume', parseInt(e.target.value))}
                  className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>
            </div>
          </section>

          {/* Graphics Settings */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4">🎨 Grafik Ayarları</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Grafik Kalitesi</label>
                <select
                  value={settings.graphics}
                  onChange={(e) => setSettings(prev => ({ ...prev, graphics: e.target.value }))}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-game-accent"
                >
                  <option value="low">Düşük</option>
                  <option value="medium">Orta</option>
                  <option value="high">Yüksek</option>
                  <option value="ultra">Ultra</option>
                </select>
              </div>

              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-sm text-gray-400">FPS Göster</span>
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={settings.showFPS}
                    onChange={(e) => setSettings(prev => ({ ...prev, showFPS: e.target.checked }))}
                    className="sr-only"
                  />
                  <div className={`w-12 h-6 rounded-full transition-colors ${settings.showFPS ? 'bg-game-accent' : 'bg-white/10'}`}>
                    <div className={`w-5 h-5 bg-white rounded-full transition-transform transform ${settings.showFPS ? 'translate-x-6' : 'translate-x-1'} mt-0.5`} />
                  </div>
                </div>
              </label>
            </div>
          </section>

          {/* Game Settings */}
          <section>
            <h3 className="text-xl font-bold text-white mb-4">🎮 Oyun Ayarları</h3>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Dil</label>
                <select
                  value={settings.language}
                  onChange={(e) => setSettings(prev => ({ ...prev, language: e.target.value }))}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-game-accent"
                >
                  <option value="tr">🇹🇷 Türkçe</option>
                  <option value="en">🇬🇧 English</option>
                  <option value="de">🇩🇪 Deutsch</option>
                  <option value="fr">🇫🇷 Français</option>
                  <option value="es">🇪🇸 Español</option>
                </select>
              </div>
            </div>
          </section>

          {/* Action buttons */}
          <div className="flex space-x-3 pt-4 border-t border-white/10">
            <button className="flex-1 btn-primary">
              Değişiklikleri Kaydet
            </button>
            <button
              onClick={() => toggleUI('showSettings')}
              className="flex-1 btn-secondary"
            >
              İptal
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
