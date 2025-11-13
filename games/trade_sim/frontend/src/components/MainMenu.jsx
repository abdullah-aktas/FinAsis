import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AudioManager } from '@utils/AudioManager';

export default function MainMenu({ onStartGame }) {
  const [showMode, setShowMode] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handlePlayClick = () => {
    AudioManager.getInstance().playSound('click');
    setShowMode(true);
  };

  const handleModeSelect = (mode) => {
    AudioManager.getInstance().playSound('success');
    onStartGame(mode);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-game-dark via-game-darker to-game-dark overflow-hidden">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {Array.from({ length: 50 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-game-accent rounded-full opacity-20"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            transition={{
              duration: 20 + Math.random() * 10,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </div>

      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <h1 className="text-7xl md:text-9xl font-bold gradient-text neon-glow mb-4">
            TradeSim 3D
          </h1>
          <p className="text-xl md:text-2xl text-gray-400 mb-12">
            🌍 Dünya Çapında Ticaret ve Ekonomi Simülasyonu
          </p>
        </motion.div>

        {/* Main menu */}
        <AnimatePresence mode="wait">
          {!showMode ? (
            <motion.div
              key="main-menu"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(0, 212, 255, 0.5)" }}
                whileTap={{ scale: 0.95 }}
                onClick={handlePlayClick}
                className="btn-primary w-full max-w-md mx-auto block text-2xl py-6 px-12"
              >
                🎮 Oyna
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => AudioManager.getInstance().playSound('click')}
                className="btn-secondary w-full max-w-md mx-auto block text-xl py-4"
              >
                ⚙️ Ayarlar
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => AudioManager.getInstance().playSound('click')}
                className="btn-secondary w-full max-w-md mx-auto block text-xl py-4"
              >
                📊 Liderlik Tablosu
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => AudioManager.getInstance().playSound('click')}
                className="btn-secondary w-full max-w-md mx-auto block text-xl py-4"
              >
                ℹ️ Nasıl Oynanır
              </motion.button>
            </motion.div>
          ) : (
            <motion.div
              key="mode-selection"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <h2 className="text-3xl font-bold text-white mb-8">
                Oyun Modunu Seç
              </h2>

              {/* Guest Mode */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleModeSelect('guest')}
                className="card cursor-pointer text-left max-w-2xl mx-auto"
              >
                <h3 className="text-2xl font-bold text-game-accent mb-2">
                  👤 Misafir Olarak Oyna
                </h3>
                <p className="text-gray-400">
                  Hızlıca başla, kayıt olmadan oyna. İlerleme kaydedilmez.
                </p>
              </motion.div>

              {/* Login Mode */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="card text-left max-w-2xl mx-auto"
              >
                <h3 className="text-2xl font-bold text-game-accent mb-4">
                  🔐 Giriş Yap
                </h3>
                <div className="space-y-4">
                  <input
                    type="text"
                    placeholder="Kullanıcı adı"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-game-accent"
                  />
                  <input
                    type="password"
                    placeholder="Şifre"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-game-accent"
                  />
                  <button
                    onClick={() => handleModeSelect('login')}
                    className="btn-primary w-full"
                  >
                    Giriş Yap
                  </button>
                </div>
              </motion.div>

              {/* Classroom Mode */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleModeSelect('classroom')}
                className="card cursor-pointer text-left max-w-2xl mx-auto"
              >
                <h3 className="text-2xl font-bold text-game-purple mb-2">
                  🎓 Sınıf Modu
                </h3>
                <p className="text-gray-400">
                  Öğretmen kontrolü ile grup oyunu. Eğitim senaryoları.
                </p>
              </motion.div>

              {/* Back button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  AudioManager.getInstance().playSound('click');
                  setShowMode(false);
                }}
                className="btn-secondary mt-8"
              >
                ← Geri
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
          className="mt-16 text-gray-500 text-sm"
        >
          <p>© 2025 FinAsis - TradeSim 3D v1.0.0</p>
          <p className="mt-2">
            <span className="text-game-accent">●</span> Çevrimiçi: 1,234 oyuncu
          </p>
        </motion.div>
      </div>
    </div>
  );
}
