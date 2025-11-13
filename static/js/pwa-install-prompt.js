/**
 * PWA Kurulum Hatırlatıcı - Akıllı & Kullanıcı Dostu
 * Kullanıcıyı sıkmadan PWA kurulumunu teşvik eder
 */

(function() {
  'use strict';

  const STORAGE_KEYS = {
    DISMISSED_AT: 'finasis_pwa_dismissed_at',
    NEVER_SHOW: 'finasis_pwa_never_show',
    INSTALL_ATTEMPTED: 'finasis_pwa_install_attempted'
  };

  const CONFIG = {
    REMIND_AFTER_DAYS: 7,           // "Şimdi değil" dedikten sonra kaç gün bekle
    INITIAL_DELAY_MS: 3000,         // İlk gösterim gecikmesi (3 saniye)
    MIN_VISIT_COUNT: 2              // En az kaç ziyaretten sonra göster
  };

  let deferredPrompt = null;
  let isInstalled = false;

  /**
   * PWA'nın zaten kurulu olup olmadığını kontrol et
   */
  function isPWAInstalled() {
    // Standalone modda çalışıyor mu?
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return true;
    }
    
    // iOS Safari standalone mode
    if (window.navigator.standalone === true) {
      return true;
    }
    
    return false;
  }

  /**
   * Kullanıcının tercihleri prompt'u göstermeye uygun mu?
   */
  function shouldShowPrompt() {
    // Zaten kuruluysa gösterme
    if (isPWAInstalled()) {
      console.debug('[PWA] Uygulama zaten kurulu, prompt gösterilmeyecek');
      return false;
    }

    // "Bir daha gösterme" seçilmiş mi?
    if (localStorage.getItem(STORAGE_KEYS.NEVER_SHOW) === 'true') {
      console.debug('[PWA] Kullanıcı "bir daha gösterme" seçeneğini seçmiş');
      return false;
    }

    // Kurulum denendi mi?
    if (localStorage.getItem(STORAGE_KEYS.INSTALL_ATTEMPTED) === 'true') {
      console.debug('[PWA] Kullanıcı daha önce kurulum yapmayı denedi');
      return false;
    }

    // Son kapatma zamanını kontrol et
    const dismissedAt = localStorage.getItem(STORAGE_KEYS.DISMISSED_AT);
    if (dismissedAt) {
      const daysSinceDismissed = (Date.now() - parseInt(dismissedAt)) / (1000 * 60 * 60 * 24);
      if (daysSinceDismissed < CONFIG.REMIND_AFTER_DAYS) {
        console.debug(`[PWA] ${Math.ceil(CONFIG.REMIND_AFTER_DAYS - daysSinceDismissed)} gün sonra tekrar gösterilecek`);
        return false;
      }
    }

    // Ziyaret sayısını artır ve kontrol et
    const visitCount = parseInt(localStorage.getItem('finasis_visit_count') || '0') + 1;
    localStorage.setItem('finasis_visit_count', visitCount.toString());
    
    if (visitCount < CONFIG.MIN_VISIT_COUNT) {
      console.debug(`[PWA] En az ${CONFIG.MIN_VISIT_COUNT} ziyaret gerekli (şu an: ${visitCount})`);
      return false;
    }

    return true;
  }

  /**
   * Prompt'u göster
   */
  function showPrompt() {
    const promptEl = document.getElementById('pwa-install-prompt');
    if (!promptEl) {
      console.warn('[PWA] Prompt elementi bulunamadı');
      return;
    }

    promptEl.classList.remove('d-none');
    promptEl.classList.add('fade-in');

    // Analytics event
    if (window.dataLayer) {
      window.dataLayer.push({
        event: 'pwa_prompt_shown',
        path: location.pathname
      });
    }
  }

  /**
   * Prompt'u gizle
   */
  function hidePrompt() {
    const promptEl = document.getElementById('pwa-install-prompt');
    if (promptEl) {
      promptEl.classList.add('fade-out');
      setTimeout(() => {
        promptEl.classList.add('d-none');
        promptEl.classList.remove('fade-in', 'fade-out');
      }, 300);
    }
  }

  /**
   * "Şimdi değil" butonu
   */
  function handleDismiss() {
    localStorage.setItem(STORAGE_KEYS.DISMISSED_AT, Date.now().toString());
    hidePrompt();

    if (window.dataLayer) {
      window.dataLayer.push({
        event: 'pwa_prompt_dismissed',
        action: 'later'
      });
    }
  }

  /**
   * "Bir daha gösterme" butonu
   */
  function handleNeverShow() {
    localStorage.setItem(STORAGE_KEYS.NEVER_SHOW, 'true');
    hidePrompt();

    if (window.dataLayer) {
      window.dataLayer.push({
        event: 'pwa_prompt_dismissed',
        action: 'never'
      });
    }
  }

  /**
   * "Kur" butonu - PWA kurulumunu başlat
   */
  async function handleInstall() {
    if (!deferredPrompt) {
      console.warn('[PWA] Kurulum prompt\'u mevcut değil');
      // Mobil cihazlarda manuel talimat göster
      showManualInstructions();
      return;
    }

    localStorage.setItem(STORAGE_KEYS.INSTALL_ATTEMPTED, 'true');

    // Prompt'u göster
    deferredPrompt.prompt();
    
    // Kullanıcının seçimini bekle
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('[PWA] Kullanıcı kurulumu kabul etti');
      if (window.dataLayer) {
        window.dataLayer.push({
          event: 'pwa_install_accepted'
        });
      }
    } else {
      console.log('[PWA] Kullanıcı kurulumu reddetti');
      if (window.dataLayer) {
        window.dataLayer.push({
          event: 'pwa_install_declined'
        });
      }
    }
    
    deferredPrompt = null;
    hidePrompt();
  }

  /**
   * Manuel kurulum talimatları (iOS ve diğer cihazlar için)
   */
  function showManualInstructions() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
    
    let message = 'Bu uygulamayı ana ekranınıza ekleyebilirsiniz!\n\n';
    
    if (isIOS && isSafari) {
      message += 'Safari\'de:\n1. Paylaş butonuna (⬆️) tıklayın\n2. "Ana Ekrana Ekle" seçeneğini seçin';
    } else if (isIOS) {
      message += 'Lütfen Safari tarayıcısını kullanarak tekrar deneyin.';
    } else {
      message += 'Tarayıcınızın menüsünden "Ana ekrana ekle" veya "Uygulama olarak yükle" seçeneğini kullanın.';
    }
    
    alert(message);
    
    if (window.dataLayer) {
      window.dataLayer.push({
        event: 'pwa_manual_instructions_shown',
        device: isIOS ? 'ios' : 'other'
      });
    }
  }

  /**
   * Event listeners'ı kur
   */
  function setupEventListeners() {
    // beforeinstallprompt eventini yakala
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('[PWA] beforeinstallprompt event tetiklendi');
      e.preventDefault();
      deferredPrompt = e;
      
      // Prompt gösterilmeye uygunsa göster
      if (shouldShowPrompt()) {
        setTimeout(showPrompt, CONFIG.INITIAL_DELAY_MS);
      }
    });

    // Kurulum tamamlandığında
    window.addEventListener('appinstalled', () => {
      console.log('[PWA] Uygulama başarıyla kuruldu');
      isInstalled = true;
      localStorage.setItem(STORAGE_KEYS.INSTALL_ATTEMPTED, 'true');
      hidePrompt();
      
      if (window.dataLayer) {
        window.dataLayer.push({
          event: 'pwa_install_completed'
        });
      }
    });

    // Buton event listeners
    document.addEventListener('DOMContentLoaded', () => {
      const installBtn = document.getElementById('pwa-install-btn');
      const dismissBtn = document.getElementById('pwa-dismiss-btn');
      const neverShowBtn = document.getElementById('pwa-never-show-btn');
      
      if (installBtn) {
        installBtn.addEventListener('click', handleInstall);
      }
      
      if (dismissBtn) {
        dismissBtn.addEventListener('click', handleDismiss);
      }
      
      if (neverShowBtn) {
        neverShowBtn.addEventListener('click', handleNeverShow);
      }
    });
  }

  /**
   * Service Worker'ı kaydet
   */
  function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker
          .register('/static/js/service-worker.js')
          .then((registration) => {
            console.log('[PWA] Service Worker kayıt başarılı:', registration.scope);
          })
          .catch((error) => {
            console.error('[PWA] Service Worker kayıt hatası:', error);
          });
      });
    }
  }

  /**
   * Initialize
   */
  function init() {
    console.log('[PWA] PWA Install Prompt başlatıldı');
    registerServiceWorker();
    setupEventListeners();
    
    // iOS veya beforeinstallprompt desteklemeyen tarayıcılar için
    // Manuel kontrol
    if (isPWAInstalled()) {
      console.log('[PWA] Uygulama zaten kurulu');
      return;
    }
    
    // Eğer beforeinstallprompt desteklenmiyorsa ve gösterilmesi gerekiyorsa
    // Prompt'u yine de göster (iOS için)
    const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isInStandaloneMode = window.navigator.standalone === true;
    
    if (isIOSDevice && !isInStandaloneMode && shouldShowPrompt()) {
      setTimeout(showPrompt, CONFIG.INITIAL_DELAY_MS);
    }
  }

  // Sayfa yüklendiğinde başlat
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

