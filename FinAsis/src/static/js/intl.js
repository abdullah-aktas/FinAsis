// FinAsis Global Formatlama Yardımcıları
// Kullanım: formatDate(date), formatNumber(num), formatCurrency(num, currencyCode)

function getLocale() {
  // i18n.js ile uyumlu olsun
  return localStorage.getItem('finasis-lang') || navigator.language.slice(0,2) || 'en';
}
function getRegion() {
  // Basit eşleştirme, daha gelişmişi için dil dosyasında tutulabilir
  const map = { tr: 'TR', en: 'US', de: 'DE', fr: 'FR', ar: 'SA', ku: 'TR' };
  const lang = getLocale();
  return map[lang] || 'US';
}
function formatDate(date) {
  const locale = getLocale();
  return new Intl.DateTimeFormat(locale, { dateStyle: 'medium' }).format(new Date(date));
}
function formatNumber(num) {
  const locale = getLocale();
  return new Intl.NumberFormat(locale).format(num);
}
function formatCurrency(num, currencyCode) {
  const locale = getLocale();
  return new Intl.NumberFormat(locale, { style: 'currency', currency: currencyCode || getDefaultCurrency() }).format(num);
}
function getDefaultCurrency() {
  const map = { tr: 'TRY', en: 'USD', de: 'EUR', fr: 'EUR', ar: 'SAR', ku: 'TRY' };
  const lang = getLocale();
  return map[lang] || 'USD';
}
window.formatDate = formatDate;
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency; 