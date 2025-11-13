import { Howl, Howler } from 'howler';

/**
 * AudioManager - Singleton class for managing game audio
 * Handles background music, sound effects, and spatial audio
 */
export class AudioManager {
  static instance = null;

  constructor() {
    if (AudioManager.instance) {
      return AudioManager.instance;
    }

    this.sounds = {};
    this.music = {};
    this.currentMusic = null;
    this.musicVolume = 0.5;
    this.sfxVolume = 0.7;
    this.masterVolume = 1.0;
    this.muted = false;

    AudioManager.instance = this;
  }

  static getInstance() {
    if (!AudioManager.instance) {
      AudioManager.instance = new AudioManager();
    }
    return AudioManager.instance;
  }

  /**
   * Initialize audio system
   */
  init() {
    Howler.volume(this.masterVolume);
    
    // Load music tracks
    this.loadMusic();
    
    // Load sound effects
    this.loadSoundEffects();
  }

  /**
   * Load music tracks
   */
  loadMusic() {
    this.music = {
      'menu': new Howl({
        src: ['/assets/audio/music/menu.mp3'],
        loop: true,
        volume: this.musicVolume,
      }),
      'game-main': new Howl({
        src: ['/assets/audio/music/game-main.mp3'],
        loop: true,
        volume: this.musicVolume,
      }),
      'city-theme': new Howl({
        src: ['/assets/audio/music/city-theme.mp3'],
        loop: true,
        volume: this.musicVolume,
      }),
      'battle': new Howl({
        src: ['/assets/audio/music/battle.mp3'],
        loop: true,
        volume: this.musicVolume,
      }),
      'victory': new Howl({
        src: ['/assets/audio/music/victory.mp3'],
        loop: false,
        volume: this.musicVolume,
      }),
    };
  }

  /**
   * Load sound effects
   */
  loadSoundEffects() {
    this.sounds = {
      'click': new Howl({
        src: ['/assets/audio/sfx/click.mp3'],
        volume: this.sfxVolume,
      }),
      'coin': new Howl({
        src: ['/assets/audio/sfx/coin.mp3'],
        volume: this.sfxVolume,
      }),
      'trade': new Howl({
        src: ['/assets/audio/sfx/trade.mp3'],
        volume: this.sfxVolume,
      }),
      'success': new Howl({
        src: ['/assets/audio/sfx/success.mp3'],
        volume: this.sfxVolume,
      }),
      'error': new Howl({
        src: ['/assets/audio/sfx/error.mp3'],
        volume: this.sfxVolume,
      }),
      'notification': new Howl({
        src: ['/assets/audio/sfx/notification.mp3'],
        volume: this.sfxVolume,
      }),
      'achievement': new Howl({
        src: ['/assets/audio/sfx/achievement.mp3'],
        volume: this.sfxVolume,
      }),
      'footstep': new Howl({
        src: ['/assets/audio/sfx/footstep.mp3'],
        volume: this.sfxVolume * 0.5,
      }),
      'ambient-city': new Howl({
        src: ['/assets/audio/sfx/ambient-city.mp3'],
        loop: true,
        volume: this.sfxVolume * 0.3,
      }),
    };
  }

  /**
   * Play music track
   */
  playMusic(trackName) {
    if (!this.music[trackName]) {
      console.warn(`Music track '${trackName}' not found`);
      return;
    }

    // Stop current music
    if (this.currentMusic && this.currentMusic !== trackName) {
      this.stopMusic();
    }

    // Play new music
    this.music[trackName].play();
    this.currentMusic = trackName;
  }

  /**
   * Stop current music
   */
  stopMusic() {
    if (this.currentMusic && this.music[this.currentMusic]) {
      this.music[this.currentMusic].stop();
      this.currentMusic = null;
    }
  }

  /**
   * Pause current music
   */
  pauseMusic() {
    if (this.currentMusic && this.music[this.currentMusic]) {
      this.music[this.currentMusic].pause();
    }
  }

  /**
   * Resume current music
   */
  resumeMusic() {
    if (this.currentMusic && this.music[this.currentMusic]) {
      this.music[this.currentMusic].play();
    }
  }

  /**
   * Play sound effect
   */
  playSound(soundName) {
    if (!this.sounds[soundName]) {
      console.warn(`Sound effect '${soundName}' not found`);
      return;
    }

    this.sounds[soundName].play();
  }

  /**
   * Play spatial sound (3D audio)
   */
  playSpatialSound(soundName, position, listenerPosition) {
    if (!this.sounds[soundName]) {
      console.warn(`Sound effect '${soundName}' not found`);
      return;
    }

    const sound = this.sounds[soundName];
    
    // Calculate distance and volume
    const distance = Math.sqrt(
      Math.pow(position[0] - listenerPosition[0], 2) +
      Math.pow(position[1] - listenerPosition[1], 2) +
      Math.pow(position[2] - listenerPosition[2], 2)
    );

    const maxDistance = 50;
    const volume = Math.max(0, 1 - (distance / maxDistance)) * this.sfxVolume;

    sound.volume(volume);
    sound.play();
  }

  /**
   * Set master volume
   */
  setMasterVolume(volume) {
    this.masterVolume = Math.max(0, Math.min(1, volume));
    Howler.volume(this.masterVolume);
  }

  /**
   * Set music volume
   */
  setMusicVolume(volume) {
    this.musicVolume = Math.max(0, Math.min(1, volume));
    Object.values(this.music).forEach(track => {
      track.volume(this.musicVolume);
    });
  }

  /**
   * Set sound effects volume
   */
  setSFXVolume(volume) {
    this.sfxVolume = Math.max(0, Math.min(1, volume));
    Object.values(this.sounds).forEach(sound => {
      sound.volume(this.sfxVolume);
    });
  }

  /**
   * Toggle mute
   */
  toggleMute() {
    this.muted = !this.muted;
    Howler.mute(this.muted);
  }

  /**
   * Cleanup
   */
  cleanup() {
    Object.values(this.music).forEach(track => track.unload());
    Object.values(this.sounds).forEach(sound => sound.unload());
  }
}

export default AudioManager;
