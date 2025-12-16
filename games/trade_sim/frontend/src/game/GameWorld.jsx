import React, { useRef, useEffect, useState } from 'react';
import VRManager from './VRManager.jsx';
import { generateCities } from './CityGenerator.js';
import { TradeBot, createNPCs } from './AIManager.js';
import { mintNFT, transferNFT, getNFTs } from '@utils/NFTManager.js';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Sky, Environment, Stars, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import { useGameStore } from '@utils/store';
import { NetworkManager } from '@utils/NetworkManager';

// Game lighting setup
function Lighting() {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight
        position={[50, 50, 25]}
        intensity={1.5}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={100}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
      />
      <hemisphereLight
        skyColor={new THREE.Color(0x7ec0ff)}
        groundColor={new THREE.Color(0x8b7355)}
        intensity={0.5}
      />
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#00d4ff" />
      <pointLight position={[-10, 10, -10]} intensity={0.5} color="#7000ff" />
    </>
  );
}

// Trading route visualization
function TradeRoute({ from, to }) {
  const points = [];
  const segments = 20;

  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const x = from[0] + (to[0] - from[0]) * t;
    const z = from[2] + (to[2] - from[2]) * t;
    const y = Math.sin(t * Math.PI) * 3 + 1; // Arc
    points.push(new THREE.Vector3(x, y, z));
  }

  const curve = new THREE.CatmullRomCurve3(points);
  const geometry = new THREE.TubeGeometry(curve, segments, 0.1, 8, false);

  return (
    <mesh geometry={geometry}>
      <meshBasicMaterial color="#00d4ff" transparent opacity={0.5} />
    </mesh>
  );
}

// Main game world
export default function GameWorld() {
  const { player, gameState, updatePlayerPosition, setCities } = useGameStore();
  const [cities, setCitiesLocal] = useState([]);
  const [otherPlayers, setOtherPlayers] = useState({});
  const [vrEnabled, setVrEnabled] = useState(false);
  const [nfts, setNfts] = useState([]);
  const [minting, setMinting] = useState(false);
  const [npcList, setNpcList] = useState([]);
  const controlsRef = useRef();

  // Gerçek şehir verilerini API'den al
  useEffect(() => {
    // API'den gerçek şehir verilerini çek
    fetch('/api/trade-sim/cities/')
      .then(res => res.json())
      .then(data => {
        if (data.cities && data.cities.length > 0) {
          const realCities = data.cities.map((city, i) => ({
            id: city.id,
            name: city.name,
            coordinates: city.coordinates || { x: i * 20, y: i * 10 },
            sectors: city.sectors || [],
            market_size: city.market_size || 1000,
          }));
          setCitiesLocal(realCities);
          setCities(realCities);
          // Gerçek şehirler için NPC'ler oluştur
          setNpcList(createNPCs(realCities.map(c => c.name)));
        } else {
          // Fallback: Eğer API'den veri gelmezse, gerçek şehir isimleri kullan
          const fallbackCities = generateCities([
            'Mardin', 'Izmir', 'Corum'
          ]).map((city, i) => ({
            id: i + 1,
            name: city.name,
            coordinates: { x: i * 20, y: i * 10 },
            ...city
          }));
          setCitiesLocal(fallbackCities);
          setCities(fallbackCities);
          setNpcList(createNPCs(['Mardin', 'Izmir', 'Corum']));
        }
      })
      .catch(err => {
        console.error('Şehir verileri alınamadı:', err);
        // Hata durumunda boş liste
        setCitiesLocal([]);
        setCities([]);
      });
    
    // Kullanıcının gerçek NFT'lerini çek (eğer varsa)
    if (player && player.wallet) {
      getNFTs(player.wallet).then(setNfts).catch(() => setNfts([]));
    }
  }, [setCities, player]);

  // Gerçek NFT mint işlemi
  const handleMintNFT = async () => {
    if (!player || !player.wallet) {
      alert('NFT mint etmek için cüzdan gerekli');
      return;
    }
    setMinting(true);
    const result = await mintNFT(
      { name: 'TradeSim NFT', image: '/assets/nft/tradesim.png' },
      player.wallet
    );
    if (result.success) {
      const updated = await getNFTs(player.wallet);
      setNfts(updated);
    }
    setMinting(false);
  };

  // AI NPC gerçek hareketi - gerçek pazar verileri ile
  useEffect(() => {
    if (npcList.length > 0 && gameState.marketData) {
      npcList.forEach(async (npc) => {
        await npc.init();
        // Gerçek pazar verileri ile tahmin
        const currentPrice = gameState.marketData.price || 100;
        const volume = gameState.marketData.volume || 5;
        await npc.predict(currentPrice, volume);
      });
    }
  }, [npcList, gameState.marketData]);

  // Gerçek şehir tıklama işlemi
  const handleCityClick = (city) => {
    // Şehir detay sayfasına yönlendir veya modal aç
    updatePlayerPosition(city.coordinates);
    // Gerçek şehir verilerini göster
    console.log('Şehir seçildi:', city);
  };

  return (
    <>
      {/* VRManager entegrasyonu */}
      <VRManager enabled={vrEnabled} />

      {/* VR modunu aç/kapat butonu */}
      <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 10 }}>
        <button onClick={() => setVrEnabled(v => !v)} style={{ padding: '8px 16px', fontWeight: 'bold', background: vrEnabled ? '#00d4ff' : '#222', color: '#fff', borderRadius: 8 }}>
          {vrEnabled ? 'VR Modu Açık' : 'VR Modunu Aç'}
        </button>
      </div>

      {/* NFT mint ve envanter demo */}
      <div style={{ position: 'absolute', top: 60, left: 20, zIndex: 10, background: '#fff', padding: 12, borderRadius: 8, boxShadow: '0 2px 8px #0002' }}>
        <div style={{ fontWeight: 'bold', marginBottom: 8 }}>NFT Envanteri</div>
        <button onClick={handleMintNFT} disabled={minting} style={{ marginBottom: 8, padding: '6px 12px', background: '#00d4ff', color: '#fff', borderRadius: 6 }}>
          {minting ? 'Minting...' : 'Demo NFT Mintle'}
        </button>
        <ul>
          {nfts.map(nft => (
            <li key={nft.tokenId} style={{ marginBottom: 4 }}>
              <img src={nft.image} alt={nft.name} style={{ width: 32, height: 32, marginRight: 8, verticalAlign: 'middle' }} />
              {nft.name}
            </li>
          ))}
        </ul>
      </div>

      {/* AI NPC demo paneli */}
      <div style={{ position: 'absolute', top: 160, left: 20, zIndex: 10, background: '#fff', padding: 12, borderRadius: 8, boxShadow: '0 2px 8px #0002' }}>
        <div style={{ fontWeight: 'bold', marginBottom: 8 }}>AI NPC'ler</div>
        <ul>
          {npcList.map(npc => (
            <li key={npc.name}>{npc.name} ({npc.city})</li>
          ))}
        </ul>
      </div>

      {/* Camera */}
      <PerspectiveCamera makeDefault position={[0, 10, 20]} fov={60} />

      {/* Controls */}
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.05}
        minDistance={5}
        maxDistance={50}
        maxPolarAngle={Math.PI / 2 - 0.1}
      />

      {/* Environment */}
      <Sky
        distance={450000}
        sunPosition={[100, 20, 100]}
        inclination={0.6}
        azimuth={0.25}
      />
      <Stars radius={300} depth={50} count={5000} factor={4} saturation={0} fade />
      <Environment preset="sunset" />

      {/* Lighting */}
      <Lighting />

      {/* Ground */}
      <Ground />

      {/* Local player */}
      {player.id && (
        <Player
          position={player.position || [0, 0, 0]}
          playerId={player.id}
          isLocalPlayer={true}
        />
      )}

      {/* Other players */}
      {Object.entries(otherPlayers).map(([playerId, position]) => (
        <Player
          key={playerId}
          position={position}
          playerId={playerId}
          isLocalPlayer={false}
        />
      ))}

      {/* Prosedürel şehirler */}
      {cities.map((city) => (
        <City
          key={city.id}
          city={city}
          onClick={() => handleCityClick(city)}
        />
      ))}

      {/* Trade routes (example) */}
      {cities.length > 1 && (
        <TradeRoute
          from={[cities[0].coordinates?.x || 0, 2, cities[0].coordinates?.y || 0]}
          to={[cities[1].coordinates?.x || 10, 2, cities[1].coordinates?.y || 10]}
        />
      )}

      {/* Fog for atmosphere */}
      <fog attach="fog" args={["#16213e", 50, 150]} />
    </>
  );
}
