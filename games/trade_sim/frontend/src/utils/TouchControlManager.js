/**
 * Touch Control Manager
 * Manages touch input events for mobile gameplay
 */

class TouchControlManager {
  constructor() {
    this.isActive = false;
    this.currentDirection = { x: 0, y: 0 };
    this.currentIntensity = 0;
    this.moveCallback = null;
    this.actionCallback = null;
    this.setupListeners();
  }

  setupListeners() {
    // Listen for touch movement events from TouchControls component
    window.addEventListener('touchmove-control', (e) => {
      const { direction, angle, intensity } = e.detail;
      this.currentDirection = direction;
      this.currentIntensity = intensity;
      this.isActive = intensity > 0;

      // Call movement callback if registered
      if (this.moveCallback) {
        this.moveCallback(direction, angle, intensity);
      }
    });

    // Listen for touch action events (buttons)
    window.addEventListener('touch-action', (e) => {
      const { action } = e.detail;
      
      // Call action callback if registered
      if (this.actionCallback) {
        this.actionCallback(action);
      }
    });

    // Detect mobile device
    this.detectMobile();
  }

  detectMobile() {
    const isMobile =
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      ) || window.innerWidth <= 768;
    
    return isMobile;
  }

  /**
   * Register a callback for movement events
   * @param {Function} callback - (direction, angle, intensity) => void
   */
  onMove(callback) {
    this.moveCallback = callback;
  }

  /**
   * Register a callback for action events
   * @param {Function} callback - (action) => void
   */
  onAction(callback) {
    this.actionCallback = callback;
  }

  /**
   * Get current movement direction
   * @returns {{x: number, y: number}}
   */
  getDirection() {
    return this.currentDirection;
  }

  /**
   * Get current movement intensity (0-1)
   * @returns {number}
   */
  getIntensity() {
    return this.currentIntensity;
  }

  /**
   * Check if touch controls are currently active
   * @returns {boolean}
   */
  isMoving() {
    return this.isActive && this.currentIntensity > 0;
  }

  /**
   * Reset touch control state
   */
  reset() {
    this.isActive = false;
    this.currentDirection = { x: 0, y: 0 };
    this.currentIntensity = 0;
  }

  /**
   * Calculate movement vector for 3D space
   * @param {number} speed - Movement speed multiplier
   * @returns {{x: number, y: number, z: number}}
   */
  getMovementVector(speed = 1) {
    if (!this.isActive) {
      return { x: 0, y: 0, z: 0 };
    }

    // Convert 2D touch direction to 3D movement
    // x: horizontal movement, z: forward/backward
    return {
      x: this.currentDirection.x * speed * this.currentIntensity,
      y: 0,
      z: -this.currentDirection.y * speed * this.currentIntensity,
    };
  }

  /**
   * Get rotation angle based on movement direction
   * @returns {number} - Rotation in radians
   */
  getRotationAngle() {
    if (!this.isActive) {
      return 0;
    }

    return Math.atan2(this.currentDirection.x, -this.currentDirection.y);
  }
}

// Singleton instance
let instance = null;

export function getTouchControlManager() {
  if (!instance) {
    instance = new TouchControlManager();
  }
  return instance;
}

export default TouchControlManager;
