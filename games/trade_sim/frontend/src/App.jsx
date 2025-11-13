import React, { Suspense, useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GameWorld from '@game/GameWorld';
import GameUI from '@components/GameUI';
import MainMenu from '@components/MainMenu';
import LoadingScreen from '@components/LoadingScreen';
import { useGameStore } from '@utils/store';
import { NetworkManager } from '@utils/NetworkManager';
import { AudioManager } from '@utils/AudioManager';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [gameStarted, setGameStarted] = useState(false);
  const { initializeGame } = useGameStore();

  useEffect(() => {
    // Initialize game systems
    const init = async () => {
      try {
        // Initialize network manager
        await NetworkManager.getInstance().connect();
        
        // Initialize audio manager
        AudioManager.getInstance().init();
        
        // Initialize game store
        await initializeGame();
        
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to initialize game:', error);
        setIsLoading(false);
      }
    };

    init();
  }, [initializeGame]);

  const handleStartGame = async (mode) => {
    // mode: 'guest' | 'login' | 'classroom'
    try {
      if (mode === 'guest') {
        await NetworkManager.getInstance().guestOnboarding();
      }
      setGameStarted(true);
      AudioManager.getInstance().playMusic('game-main');
    } catch (error) {
      console.error('Failed to start game:', error);
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!gameStarted) {
    return <MainMenu onStartGame={handleStartGame} />;
  }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* 3D Game World - Three.js Canvas */}
      <Canvas
        shadows
        camera={{ position: [0, 5, 10], fov: 60 }}
        gl={{ 
          antialias: true,
          alpha: false,
          powerPreference: 'high-performance'
        }}
        dpr={[1, 2]} // Responsive pixel ratio
        style={{ 
          position: 'absolute', 
          top: 0, 
          left: 0,
          width: '100%',
          height: '100%'
        }}
      >
        <Suspense fallback={null}>
          <GameWorld />
        </Suspense>
      </Canvas>

      {/* 2D UI Overlay - React Components */}
      <GameUI />
    </div>
  );
}

export default App;
