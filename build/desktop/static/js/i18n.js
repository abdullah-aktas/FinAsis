/**
 * FinAsis çeviri modülü
 * Uygulamanın çoklu dil desteği için kullanılan JavaScript modülü
 */

// Mevcut destek dilleri
const SUPPORTED_LANGUAGES = ['tr', 'en'];

// Varsayılan dil
const DEFAULT_LANGUAGE = 'tr';

// Dil çevirileri
let translations = {};

// Mevcut aktif dil
let currentLanguage = localStorage.getItem('finasis_language') || DEFAULT_LANGUAGE;

/**
 * Dil paketlerini yükler
 * @returns {Promise} - Tüm dil paketlerinin yüklendiği promise
 */
async function loadTranslations() {
  const promises = SUPPORTED_LANGUAGES.map(async (lang) => {
    try {
      const response = await fetch(`/locale/js/${lang}.json`);
      if (!response.ok) {
        throw new Error(`Failed to load ${lang} translations`);
      }
      const data = await response.json();
      translations[lang] = data;
    } catch (error) {
      console.error(`Error loading ${lang} translations:`, error);
      // Dil dosyası yüklenemezse boş obje kullan
      translations[lang] = {};
    }
  });

  return Promise.all(promises);
}

/**
 * Aktif dili değiştirir ve arayüzü günceller
 * @param {string} language - Dil kodu (tr, en, vb.)
 */
function changeLanguage(language) {
  if (!SUPPORTED_LANGUAGES.includes(language)) {
    console.warn(`Unsupported language: ${language}`);
    return;
  }

  currentLanguage = language;
  localStorage.setItem('finasis_language', language);
  
  // HTML lang özniteliğini güncelle
  document.documentElement.lang = language;
  
  // Dil değişikliği olayını tetikle
  document.dispatchEvent(new CustomEvent('language-changed', { detail: { language } }));
  
  // Sayfadaki çevrilebilir elementleri güncelle
  updateTranslations();
}

/**
 * Belirli bir çeviri anahtarının değerini döndürür
 * @param {string} key - Çeviri anahtarı (dot notation, ör: "common.save")
 * @param {Object} params - Çeviri içindeki yer tutucuları değiştirmek için parametreler
 * @returns {string} - Çevrilmiş metin
 */
function t(key, params = {}) {
  // Dil dosyaları yüklenmemişse
  if (!translations[currentLanguage]) {
    return key;
  }
  
  // Anahtarı noktalı gösterime göre parçala
  const keys = key.split('.');
  
  // Çeviriyi bul
  let translation = translations[currentLanguage];
  for (const k of keys) {
    translation = translation?.[k];
    if (translation === undefined) {
      // Çeviri bulunamazsa anahtar değerini döndür
      return key;
    }
  }
  
  // Çeviri içindeki yer tutucuları değiştir, ör: {{name}}
  let result = translation;
  Object.entries(params).forEach(([param, value]) => {
    result = result.replace(new RegExp(`{{${param}}}`, 'g'), value);
  });
  
  return result;
}

/**
 * Sayfadaki tüm çevrilebilir elementleri günceller
 */
function updateTranslations() {
  // data-i18n özniteliği olan elementleri bul
  const elements = document.querySelectorAll('[data-i18n]');
  
  elements.forEach(el => {
    const key = el.getAttribute('data-i18n');
    const translation = t(key);
    
    // Özel durumlar için data-i18n-attr özniteliği kontrolü
    const attr = el.getAttribute('data-i18n-attr');
    if (attr) {
      // Belirli bir özniteliği çevir (ör: placeholder, title, vb.)
      el.setAttribute(attr, translation);
    } else {
      // Varsayılan olarak elementin içeriğini çevir
      el.textContent = translation;
    }
  });
}

/**
 * Dil seçim düğmelerini etkinleştirir
 */
function setupLanguageSelectors() {
  document.querySelectorAll('[data-language]').forEach(el => {
    el.addEventListener('click', () => {
      const language = el.getAttribute('data-language');
      changeLanguage(language);
    });
    
    // Aktif dil için sınıf ekle
    if (el.getAttribute('data-language') === currentLanguage) {
      el.classList.add('active');
    }
  });
}

/**
 * Sayfa yüklendiğinde çevirileri başlat
 */
document.addEventListener('DOMContentLoaded', async () => {
  await loadTranslations();
  updateTranslations();
  setupLanguageSelectors();
});

// Modülü dışa aktar
window.i18n = {
  t,
  changeLanguage,
  getCurrentLanguage: () => currentLanguage,
  getSupportedLanguages: () => [...SUPPORTED_LANGUAGES]
}; 