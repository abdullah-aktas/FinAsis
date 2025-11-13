import axios from 'axios';
import io from 'socket.io-client';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

/**
 * NetworkManager - Singleton class for managing network connections
 * Handles both REST API calls and WebSocket connections
 */
export class NetworkManager {
  static instance = null;

  constructor() {
    if (NetworkManager.instance) {
      return NetworkManager.instance;
    }

    this.socket = null;
    this.connected = false;
    this.token = localStorage.getItem('auth_token');
    this.callbacks = {};

    // Configure axios
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    NetworkManager.instance = this;
  }

  static getInstance() {
    if (!NetworkManager.instance) {
      NetworkManager.instance = new NetworkManager();
    }
    return NetworkManager.instance;
  }

  /**
   * Connect to WebSocket server
   */
  async connect() {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(WS_URL, {
          transports: ['websocket', 'polling'],
          auth: {
            token: this.token,
          },
        });

        this.socket.on('connect', () => {
          console.log('✅ WebSocket connected');
          this.connected = true;
          this.setupEventHandlers();
          resolve();
        });

        this.socket.on('connect_error', (error) => {
          console.error('❌ WebSocket connection error:', error);
          reject(error);
        });

        this.socket.on('disconnect', () => {
          console.log('⚠️ WebSocket disconnected');
          this.connected = false;
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Setup WebSocket event handlers
   */
  setupEventHandlers() {
    // Player events
    this.socket.on('player:update', (data) => {
      this.trigger('player:update', data);
    });

    this.socket.on('player:move', (data) => {
      this.trigger('player:move', data);
    });

    // Game events
    this.socket.on('game:state', (data) => {
      this.trigger('game:state', data);
    });

    // Market events
    this.socket.on('market:update', (data) => {
      this.trigger('market:update', data);
    });

    this.socket.on('market:trade', (data) => {
      this.trigger('market:trade', data);
    });

    // Chat events
    this.socket.on('chat:message', (data) => {
      this.trigger('chat:message', data);
    });

    // Notification events
    this.socket.on('notification', (data) => {
      this.trigger('notification', data);
    });

    // Quest events
    this.socket.on('quest:update', (data) => {
      this.trigger('quest:update', data);
    });

    this.socket.on('quest:complete', (data) => {
      this.trigger('quest:complete', data);
    });
  }

  /**
   * Register callback for event
   */
  on(event, callback) {
    if (!this.callbacks[event]) {
      this.callbacks[event] = [];
    }
    this.callbacks[event].push(callback);
  }

  /**
   * Trigger event callbacks
   */
  trigger(event, data) {
    if (this.callbacks[event]) {
      this.callbacks[event].forEach(callback => callback(data));
    }
  }

  /**
   * Emit event to server
   */
  emit(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data);
    }
  }

  // ============ API Methods ============

  /**
   * Guest onboarding - Create temporary account
   */
  async guestOnboarding() {
    try {
      const response = await this.api.post('/games/trade-sim/guest-onboarding/');
      if (response.data.status === 'ok') {
        return response.data;
      }
      throw new Error('Guest onboarding failed');
    } catch (error) {
      console.error('Guest onboarding error:', error);
      throw error;
    }
  }

  /**
   * Authenticated user onboarding
   */
  async userOnboarding() {
    try {
      const response = await this.api.post('/games/trade-sim/onboarding/');
      return response.data;
    } catch (error) {
      console.error('User onboarding error:', error);
      throw error;
    }
  }

  /**
   * Get all cities
   */
  async getCities() {
    try {
      const response = await this.api.get('/games/trade-sim/cities/');
      return response.data.cities;
    } catch (error) {
      console.error('Get cities error:', error);
      return [];
    }
  }

  /**
   * Get city details
   */
  async getCity(cityId) {
    try {
      const response = await this.api.get(`/games/trade-sim/cities/${cityId}/`);
      return response.data.city;
    } catch (error) {
      console.error('Get city error:', error);
      return null;
    }
  }

  /**
   * Get all products
   */
  async getProducts() {
    try {
      const response = await this.api.get('/games/trade-sim/products/');
      return response.data.products;
    } catch (error) {
      console.error('Get products error:', error);
      return [];
    }
  }

  /**
   * Get city markets
   */
  async getCityMarkets(cityId) {
    try {
      const response = await this.api.get(`/games/trade-sim/city-markets/${cityId}/`);
      return response.data.markets;
    } catch (error) {
      console.error('Get city markets error:', error);
      return [];
    }
  }

  /**
   * Execute trade between cities
   */
  async executeTrade(fromCityId, toCityId, productId, amount) {
    try {
      const response = await this.api.post('/games/trade-sim/city-trade/', {
        from_city: fromCityId,
        to_city: toCityId,
        product_id: productId,
        amount,
      });
      return response.data;
    } catch (error) {
      console.error('Execute trade error:', error);
      throw error;
    }
  }

  /**
   * Trigger market event
   */
  async triggerMarketEvent(cityId, productId) {
    try {
      const response = await this.api.post('/games/trade-sim/trigger-market-event/', {
        city_id: cityId,
        product_id: productId,
      });
      return response.data;
    } catch (error) {
      console.error('Trigger market event error:', error);
      throw error;
    }
  }

  /**
   * Get character data
   */
  async getCharacter() {
    try {
      const response = await this.api.get('/games/trade-sim/characters/');
      return response.data;
    } catch (error) {
      console.error('Get character error:', error);
      return null;
    }
  }

  /**
   * Update character data
   */
  async updateCharacter(characterId, data) {
    try {
      const response = await this.api.patch(`/games/trade-sim/characters/${characterId}/`, data);
      return response.data;
    } catch (error) {
      console.error('Update character error:', error);
      throw error;
    }
  }

  /**
   * Get quests
   */
  async getQuests() {
    try {
      const response = await this.api.get('/games/trade-sim/quests/');
      return response.data;
    } catch (error) {
      console.error('Get quests error:', error);
      return [];
    }
  }

  /**
   * Get active character quests
   */
  async getCharacterQuests(characterId) {
    try {
      const response = await this.api.get(`/games/trade-sim/characters/${characterId}/quests/`);
      return response.data;
    } catch (error) {
      console.error('Get character quests error:', error);
      return [];
    }
  }

  /**
   * Get notifications
   */
  async getNotifications() {
    try {
      const response = await this.api.get('/games/trade-sim/notifications/');
      return response.data;
    } catch (error) {
      console.error('Get notifications error:', error);
      return [];
    }
  }

  /**
   * Mark notification as read
   */
  async markNotificationRead(notificationId) {
    try {
      await this.api.patch(`/games/trade-sim/notifications/${notificationId}/read/`);
    } catch (error) {
      console.error('Mark notification read error:', error);
    }
  }

  /**
   * Get chat messages
   */
  async getChatMessages(room = 'global') {
    try {
      const response = await this.api.get(`/games/trade-sim/chat/?room=${room}`);
      return response.data;
    } catch (error) {
      console.error('Get chat messages error:', error);
      return [];
    }
  }

  /**
   * Send chat message
   */
  async sendChatMessage(room, message) {
    try {
      const response = await this.api.post('/games/trade-sim/chat/', {
        room,
        message,
      });
      return response.data;
    } catch (error) {
      console.error('Send chat message error:', error);
      throw error;
    }
  }

  /**
   * Scan QR code for reward
   */
  async scanQRReward(code) {
    try {
      const response = await this.api.post('/games/trade-sim/qr-reward/', {
        code,
      });
      return response.data;
    } catch (error) {
      console.error('Scan QR reward error:', error);
      throw error;
    }
  }

  /**
   * Disconnect from server
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.connected = false;
    }
  }
}

export default NetworkManager;
