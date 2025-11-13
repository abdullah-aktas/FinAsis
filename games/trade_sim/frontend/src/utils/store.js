import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// Main game state store using Zustand
export const useGameStore = create(
  devtools(
    persist(
      (set, get) => ({
        // Player data
        player: {
          id: null,
          username: 'Guest',
          character: null,
          position: [0, 0, 0],
          rotation: 0,
          score: 0,
          level: 1,
          coins: 1000,
          gems: 10,
          inventory: [],
          cosmetics: [],
          skills: {},
          needs: {
            energy: 100,
            happiness: 100,
            hunger: 100,
          },
        },

        // Game state
        gameState: {
          currentCity: null,
          cities: [],
          products: [],
          markets: [],
          quests: [],
          activeQuests: [],
          achievements: [],
          notifications: [],
          friends: [],
          guilds: [],
          tournaments: [],
        },

        // UI state
        uiState: {
          showInventory: false,
          showMap: false,
          showQuests: false,
          showLeaderboard: false,
          showSettings: false,
          showChat: false,
          selectedCity: null,
          selectedProduct: null,
        },

        // Network state
        networkState: {
          connected: false,
          latency: 0,
          playersOnline: 0,
        },

        // Actions
        initializeGame: async () => {
          // Initialize game data
          console.log('Initializing game...');
        },

        setPlayer: (playerData) => set({ player: { ...get().player, ...playerData } }),
        
        updatePlayerPosition: (position) => 
          set(state => ({ 
            player: { ...state.player, position } 
          })),

        updatePlayerNeeds: (needs) =>
          set(state => ({
            player: { 
              ...state.player, 
              needs: { ...state.player.needs, ...needs }
            }
          })),

        addToInventory: (item) =>
          set(state => ({
            player: {
              ...state.player,
              inventory: [...state.player.inventory, item]
            }
          })),

        removeFromInventory: (itemId) =>
          set(state => ({
            player: {
              ...state.player,
              inventory: state.player.inventory.filter(i => i.id !== itemId)
            }
          })),

        updateCoins: (amount) =>
          set(state => ({
            player: {
              ...state.player,
              coins: state.player.coins + amount
            }
          })),

        updateScore: (amount) =>
          set(state => ({
            player: {
              ...state.player,
              score: state.player.score + amount
            }
          })),

        // Game state actions
        setCities: (cities) => 
          set(state => ({ 
            gameState: { ...state.gameState, cities } 
          })),

        setProducts: (products) =>
          set(state => ({
            gameState: { ...state.gameState, products }
          })),

        setMarkets: (markets) =>
          set(state => ({
            gameState: { ...state.gameState, markets }
          })),

        setQuests: (quests) =>
          set(state => ({
            gameState: { ...state.gameState, quests }
          })),

        addQuest: (quest) =>
          set(state => ({
            gameState: {
              ...state.gameState,
              activeQuests: [...state.gameState.activeQuests, quest]
            }
          })),

        completeQuest: (questId) =>
          set(state => ({
            gameState: {
              ...state.gameState,
              activeQuests: state.gameState.activeQuests.filter(q => q.id !== questId)
            }
          })),

        addNotification: (notification) =>
          set(state => ({
            gameState: {
              ...state.gameState,
              notifications: [notification, ...state.gameState.notifications].slice(0, 20)
            }
          })),

        clearNotifications: () =>
          set(state => ({
            gameState: {
              ...state.gameState,
              notifications: []
            }
          })),

        // UI actions
        toggleUI: (key) =>
          set(state => ({
            uiState: {
              ...state.uiState,
              [key]: !state.uiState[key]
            }
          })),

        setUIState: (updates) =>
          set(state => ({
            uiState: { ...state.uiState, ...updates }
          })),

        // Network actions
        setNetworkState: (updates) =>
          set(state => ({
            networkState: { ...state.networkState, ...updates }
          })),
      }),
      {
        name: 'tradesim-storage',
        partialize: (state) => ({
          player: state.player,
          // Don't persist UI state and network state
        }),
      }
    )
  )
);
