/**
 * Asset Loader
 * Centralized asset loading and caching system
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader';

class AssetLoader {
  constructor() {
    this.cache = new Map();
    this.loadingPromises = new Map();
    
    // Setup loaders
    this.textureLoader = new THREE.TextureLoader();
    this.cubeTextureLoader = new THREE.CubeTextureLoader();
    
    // Setup GLTF loader with Draco compression
    this.gltfLoader = new GLTFLoader();
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath('/draco/');
    this.gltfLoader.setDRACOLoader(dracoLoader);
    
    this.loadingManager = new THREE.LoadingManager();
    this.setupLoadingManager();
  }

  setupLoadingManager() {
    this.loadingManager.onStart = (url, itemsLoaded, itemsTotal) => {
      console.log(`Started loading: ${url} (${itemsLoaded}/${itemsTotal})`);
    };

    this.loadingManager.onLoad = () => {
      console.log('All assets loaded');
      this.dispatchEvent('assets-loaded');
    };

    this.loadingManager.onProgress = (url, itemsLoaded, itemsTotal) => {
      const progress = (itemsLoaded / itemsTotal) * 100;
      this.dispatchEvent('loading-progress', { progress, itemsLoaded, itemsTotal });
    };

    this.loadingManager.onError = (url) => {
      console.error(`Error loading: ${url}`);
      this.dispatchEvent('loading-error', { url });
    };
  }

  dispatchEvent(type, detail = {}) {
    window.dispatchEvent(new CustomEvent(`asset-${type}`, { detail }));
  }

  /**
   * Load a texture
   * @param {string} url - Texture URL
   * @returns {Promise<THREE.Texture>}
   */
  async loadTexture(url) {
    // Check cache
    if (this.cache.has(url)) {
      return this.cache.get(url);
    }

    // Check if already loading
    if (this.loadingPromises.has(url)) {
      return this.loadingPromises.get(url);
    }

    // Load texture
    const promise = new Promise((resolve, reject) => {
      this.textureLoader.load(
        url,
        (texture) => {
          this.cache.set(url, texture);
          this.loadingPromises.delete(url);
          resolve(texture);
        },
        undefined,
        (error) => {
          this.loadingPromises.delete(url);
          reject(error);
        }
      );
    });

    this.loadingPromises.set(url, promise);
    return promise;
  }

  /**
   * Load a GLTF model
   * @param {string} url - Model URL
   * @returns {Promise<GLTF>}
   */
  async loadModel(url) {
    // Check cache
    if (this.cache.has(url)) {
      return this.cache.get(url);
    }

    // Check if already loading
    if (this.loadingPromises.has(url)) {
      return this.loadingPromises.get(url);
    }

    // Load model
    const promise = new Promise((resolve, reject) => {
      this.gltfLoader.load(
        url,
        (gltf) => {
          this.cache.set(url, gltf);
          this.loadingPromises.delete(url);
          resolve(gltf);
        },
        (progress) => {
          const percentComplete = (progress.loaded / progress.total) * 100;
          console.log(`Loading model: ${url} - ${percentComplete.toFixed(2)}%`);
        },
        (error) => {
          this.loadingPromises.delete(url);
          reject(error);
        }
      );
    });

    this.loadingPromises.set(url, promise);
    return promise;
  }

  /**
   * Load a cube texture (skybox)
   * @param {string[]} urls - Array of 6 URLs for cube faces
   * @returns {Promise<THREE.CubeTexture>}
   */
  async loadCubeTexture(urls) {
    const key = urls.join(',');
    
    // Check cache
    if (this.cache.has(key)) {
      return this.cache.get(key);
    }

    // Load cube texture
    const promise = new Promise((resolve, reject) => {
      this.cubeTextureLoader.load(
        urls,
        (texture) => {
          this.cache.set(key, texture);
          resolve(texture);
        },
        undefined,
        reject
      );
    });

    return promise;
  }

  /**
   * Preload multiple assets
   * @param {Object} assets - { textures: [...], models: [...], cubeMaps: [...] }
   * @returns {Promise<void>}
   */
  async preloadAssets(assets = {}) {
    const promises = [];

    // Load textures
    if (assets.textures) {
      assets.textures.forEach((url) => {
        promises.push(this.loadTexture(url));
      });
    }

    // Load models
    if (assets.models) {
      assets.models.forEach((url) => {
        promises.push(this.loadModel(url));
      });
    }

    // Load cube maps
    if (assets.cubeMaps) {
      assets.cubeMaps.forEach((urls) => {
        promises.push(this.loadCubeTexture(urls));
      });
    }

    await Promise.all(promises);
  }

  /**
   * Get cached asset
   * @param {string} url - Asset URL
   * @returns {any}
   */
  getFromCache(url) {
    return this.cache.get(url);
  }

  /**
   * Clear cache
   */
  clearCache() {
    // Dispose textures and geometries
    this.cache.forEach((asset) => {
      if (asset.dispose) {
        asset.dispose();
      }
    });
    
    this.cache.clear();
    this.loadingPromises.clear();
  }

  /**
   * Get cache size
   * @returns {number}
   */
  getCacheSize() {
    return this.cache.size;
  }
}

// Singleton instance
let instance = null;

export function getAssetLoader() {
  if (!instance) {
    instance = new AssetLoader();
  }
  return instance;
}

export default AssetLoader;
