/**
 * Mobile Touch Controls Component
 * Virtual joystick for movement and touch UI
 */
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import useGameStore from '@utils/store';

export default function TouchControls() {
  const isMobile = useGameStore((state) => state.gameState.isMobile);
  const [joystickActive, setJoystickActive] = useState(false);
  const [joystickPosition, setJoystickPosition] = useState({ x: 0, y: 0 });
  const [touchStart, setTouchStart] = useState({ x: 0, y: 0 });
  const joystickRef = useRef(null);
  const moveIntervalRef = useRef(null);

  const JOYSTICK_MAX_DISTANCE = 50; // Maximum distance from center
  const JOYSTICK_DEADZONE = 10; // Minimum distance to register movement

  useEffect(() => {
    // Clean up on unmount
    return () => {
      if (moveIntervalRef.current) {
        clearInterval(moveIntervalRef.current);
      }
    };
  }, []);

  const handleTouchStart = (e) => {
    const touch = e.touches[0];
    const rect = joystickRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    setTouchStart({ x: centerX, y: centerY });
    setJoystickActive(true);
    updateJoystickPosition(touch.clientX, touch.clientY, centerX, centerY);
  };

  const handleTouchMove = (e) => {
    if (!joystickActive) return;

    const touch = e.touches[0];
    updateJoystickPosition(
      touch.clientX,
      touch.clientY,
      touchStart.x,
      touchStart.y
    );
  };

  const handleTouchEnd = () => {
    setJoystickActive(false);
    setJoystickPosition({ x: 0, y: 0 });
    if (moveIntervalRef.current) {
      clearInterval(moveIntervalRef.current);
      moveIntervalRef.current = null;
    }
  };

  const updateJoystickPosition = (touchX, touchY, centerX, centerY) => {
    let deltaX = touchX - centerX;
    let deltaY = touchY - centerY;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    // Apply deadzone
    if (distance < JOYSTICK_DEADZONE) {
      setJoystickPosition({ x: 0, y: 0 });
      return;
    }

    // Limit to max distance
    if (distance > JOYSTICK_MAX_DISTANCE) {
      const angle = Math.atan2(deltaY, deltaX);
      deltaX = Math.cos(angle) * JOYSTICK_MAX_DISTANCE;
      deltaY = Math.sin(angle) * JOYSTICK_MAX_DISTANCE;
    }

    setJoystickPosition({ x: deltaX, y: deltaY });

    // Emit movement event
    emitMovementEvent(deltaX, deltaY, distance);
  };

  const emitMovementEvent = (deltaX, deltaY, distance) => {
    // Calculate direction vector (normalized)
    const normalizedX = deltaX / JOYSTICK_MAX_DISTANCE;
    const normalizedY = deltaY / JOYSTICK_MAX_DISTANCE;

    // Calculate angle for rotation
    const angle = Math.atan2(deltaY, deltaX);

    // Emit custom event for game world to listen to
    const event = new CustomEvent('touchmove-control', {
      detail: {
        direction: { x: normalizedX, y: normalizedY },
        angle: angle,
        intensity: Math.min(distance / JOYSTICK_MAX_DISTANCE, 1),
      },
    });
    window.dispatchEvent(event);
  };

  // Don't render on desktop
  if (!isMobile) return null;

  return (
    <>
      {/* Virtual Joystick */}
      <div className="fixed bottom-8 left-8 z-50">
        <div
          ref={joystickRef}
          className="relative w-32 h-32 bg-black/20 rounded-full border-2 border-white/30 backdrop-blur-sm"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          {/* Joystick base */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 bg-white/10 rounded-full" />
          </div>

          {/* Joystick stick */}
          <motion.div
            className="absolute top-1/2 left-1/2 w-12 h-12 -mt-6 -ml-6 bg-blue-500/80 rounded-full shadow-lg border-2 border-white/50"
            animate={{
              x: joystickPosition.x,
              y: joystickPosition.y,
            }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            {/* Stick glow */}
            {joystickActive && (
              <div className="absolute inset-0 bg-blue-400 rounded-full animate-ping opacity-75" />
            )}
          </motion.div>

          {/* Direction indicators */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="w-full h-full relative">
              {/* Up */}
              <div className="absolute top-2 left-1/2 -translate-x-1/2 text-white/30 text-xs">
                ↑
              </div>
              {/* Down */}
              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-white/30 text-xs">
                ↓
              </div>
              {/* Left */}
              <div className="absolute left-2 top-1/2 -translate-y-1/2 text-white/30 text-xs">
                ←
              </div>
              {/* Right */}
              <div className="absolute right-2 top-1/2 -translate-y-1/2 text-white/30 text-xs">
                →
              </div>
            </div>
          </div>
        </div>

        {/* Joystick label */}
        <div className="text-center text-white/50 text-xs mt-2">Hareket</div>
      </div>

      {/* Action Buttons (Right side) */}
      <div className="fixed bottom-8 right-8 z-50 flex flex-col gap-3">
        {/* Jump/Interact Button */}
        <TouchButton
          icon="🎯"
          label="Etkileşim"
          color="green"
          onPress={() => emitActionEvent('interact')}
        />

        {/* Inventory Button */}
        <TouchButton
          icon="🎒"
          label="Envanter"
          color="purple"
          onPress={() => useGameStore.getState().toggleInventory()}
        />

        {/* Map Button */}
        <TouchButton
          icon="🗺️"
          label="Harita"
          color="blue"
          onPress={() => useGameStore.getState().toggleMap()}
        />

        {/* Menu Button */}
        <TouchButton
          icon="☰"
          label="Menü"
          color="gray"
          onPress={() => useGameStore.getState().setGameState('menu')}
        />
      </div>

      {/* Camera Control Hint */}
      <div className="fixed top-1/2 right-4 -translate-y-1/2 z-40 bg-black/20 backdrop-blur-sm rounded-lg p-3 text-white/60 text-xs text-center">
        <div className="mb-1">📷</div>
        <div>Kamerayı</div>
        <div>sürükle</div>
      </div>
    </>
  );
}

/**
 * Touch Button Component
 */
function TouchButton({ icon, label, color, onPress }) {
  const [isPressed, setIsPressed] = useState(false);

  const colorMap = {
    green: 'bg-green-500/80 border-green-400',
    purple: 'bg-purple-500/80 border-purple-400',
    blue: 'bg-blue-500/80 border-blue-400',
    gray: 'bg-gray-500/80 border-gray-400',
    red: 'bg-red-500/80 border-red-400',
  };

  const handleTouchStart = () => {
    setIsPressed(true);
    onPress();
  };

  const handleTouchEnd = () => {
    setIsPressed(false);
  };

  return (
    <motion.button
      className={`w-16 h-16 ${colorMap[color]} rounded-full border-2 shadow-lg flex items-center justify-center text-2xl transition-transform active:scale-95`}
      whileTap={{ scale: 0.9 }}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div className="flex flex-col items-center">
        <div className={isPressed ? 'scale-90' : ''}>{icon}</div>
        {isPressed && (
          <div className="absolute -bottom-6 text-xs text-white/80 whitespace-nowrap">
            {label}
          </div>
        )}
      </div>

      {/* Button glow effect */}
      {isPressed && (
        <div className="absolute inset-0 bg-white/20 rounded-full animate-pulse" />
      )}
    </motion.button>
  );
}

/**
 * Emit action event for game world
 */
function emitActionEvent(action) {
  const event = new CustomEvent('touch-action', {
    detail: { action },
  });
  window.dispatchEvent(event);
}
