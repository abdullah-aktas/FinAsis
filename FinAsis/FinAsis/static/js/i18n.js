// Basit i18n altyapısı
const supportedLangs = ['tr', 'en', 'de', 'fr', 'ar', 'ku'];
const rtlLangs = ['ar', 'he', 'fa', 'ur']; // Kürtçe Kurmançî Latin alfabesiyle LTR, Sorani ise RTL'dir. Burada Kurmançî (ku) LTR kabul edilecek.
let currentLang = localStorage.getItem('finasis-lang') || navigator.language.slice(0,2) || 'en';
if (!supportedLangs.includes(currentLang)) currentLang = 'en';

function setLang(lang) {
  if (!supportedLangs.includes(lang)) lang = 'en';
  currentLang = lang;
  localStorage.setItem('finasis-lang', lang);
  fetch(`/static/locales/${lang}.json`)
    .then(res => res.json())
    .then(dict => {
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) el.innerHTML = dict[key];
      });
      // RTL desteği
      if (rtlLangs.includes(lang)) {
        document.body.setAttribute('dir', 'rtl');
      } else {
        document.body.setAttribute('dir', 'ltr');
      }
    });
}
window.setLang = setLang;
window.addEventListener('DOMContentLoaded', function() {
  setLang(currentLang);
  // Dil seçici dropdown
  const langSel = document.getElementById('lang-select');
  if (langSel) {
    langSel.value = currentLang;
    langSel.addEventListener('change', e => setLang(e.target.value));
  }
}); 