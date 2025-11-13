import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '@utils/store';
import { AudioManager } from '@utils/AudioManager';

export default function NotificationPanel() {
  const { gameState } = useGameStore();
  const notifications = gameState.notifications || [];

  useEffect(() => {
    if (notifications.length > 0) {
      const latestNotification = notifications[0];
      
      // Play sound based on notification type
      if (latestNotification.type === 'achievement') {
        AudioManager.getInstance().playSound('achievement');
      } else if (latestNotification.type === 'success') {
        AudioManager.getInstance().playSound('success');
      } else if (latestNotification.type === 'error') {
        AudioManager.getInstance().playSound('error');
      } else {
        AudioManager.getInstance().playSound('notification');
      }
    }
  }, [notifications]);

  const getIcon = (type) => {
    switch (type) {
      case 'achievement':
        return '🏆';
      case 'quest':
        return '📋';
      case 'trade':
        return '💰';
      case 'friend':
        return '👥';
      case 'tournament':
        return '⚔️';
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  const getColor = (type) => {
    switch (type) {
      case 'achievement':
        return 'from-yellow-500 to-orange-500';
      case 'quest':
        return 'from-blue-500 to-purple-500';
      case 'trade':
        return 'from-green-500 to-emerald-500';
      case 'error':
        return 'from-red-500 to-pink-500';
      case 'success':
        return 'from-game-accent to-game-purple';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  return (
    <div className="absolute top-20 right-4 space-y-2 pointer-events-none">
      <AnimatePresence>
        {notifications.slice(0, 5).map((notification, index) => (
          <motion.div
            key={notification.id || index}
            initial={{ opacity: 0, x: 100, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.8 }}
            transition={{
              type: "spring",
              damping: 25,
              stiffness: 300,
            }}
            className="pointer-events-auto"
          >
            <div className={`glass rounded-lg p-4 min-w-[300px] max-w-md border-l-4 bg-gradient-to-r ${getColor(notification.type)}`}>
              <div className="flex items-start space-x-3">
                {/* Icon */}
                <div className="text-2xl">
                  {getIcon(notification.type)}
                </div>

                {/* Content */}
                <div className="flex-1">
                  <h4 className="font-bold text-white mb-1">
                    {notification.title}
                  </h4>
                  <p className="text-sm text-gray-200">
                    {notification.message}
                  </p>
                  
                  {notification.rewards && (
                    <div className="mt-2 flex items-center space-x-2 text-xs">
                      {notification.rewards.coins && (
                        <span className="bg-white/20 px-2 py-1 rounded">
                          💰 +{notification.rewards.coins}
                        </span>
                      )}
                      {notification.rewards.xp && (
                        <span className="bg-white/20 px-2 py-1 rounded">
                          ⭐ +{notification.rewards.xp}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Close button */}
                <button
                  onClick={() => {
                    // Remove notification logic here
                  }}
                  className="text-white/60 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              {/* Progress bar for auto-dismiss */}
              <motion.div
                className="absolute bottom-0 left-0 h-1 bg-white/30 rounded-b-lg"
                initial={{ width: '100%' }}
                animate={{ width: '0%' }}
                transition={{ duration: 5, ease: 'linear' }}
              />
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
