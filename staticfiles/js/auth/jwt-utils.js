/**
 * JWT Token Yönetimi
 * 
 * Bu modül, JWT token'larının yönetimini ve sessiz yenileme (silent refresh) mekanizmasını sağlar.
 */

// Token saklama anahtarları
const ACCESS_TOKEN_KEY = 'finasis_access_token';
const REFRESH_TOKEN_KEY = 'finasis_refresh_token';
const TOKEN_EXPIRY_KEY = 'finasis_token_expiry';

// Yenileme süresi (token sona ermeden kaç ms önce yenilenecek)
const REFRESH_THRESHOLD_MS = 5 * 60 * 1000; // 5 dakika

// Sessiz yenileme zamanlayıcısı
let refreshTimer = null;

/**
 * Token'ın sona erme tarihini JWT token'dan alır.
 * 
 * @param {string} token - JWT token
 * @returns {number} Token'ın sona erme tarihi (milisaniye cinsinden)
 */
function getTokenExpiry(token) {
    try {
        // Token'ı parçalarına ayır
        const payload = token.split('.')[1];
        
        // Base64 decode işlemi
        const decodedPayload = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
        
        // JSON olarak ayrıştır
        const payloadObj = JSON.parse(decodedPayload);
        
        // Sona erme tarihini al (saniye -> milisaniye)
        return payloadObj.exp * 1000;
    } catch (error) {
        console.error('Token çözümleme hatası:', error);
        return 0;
    }
}

/**
 * Verilen token'ın süresi dolmuş mu kontrol eder.
 * 
 * @param {string} token - JWT token
 * @returns {boolean} Token süresi dolduysa true, dolmadıysa false
 */
function isTokenExpired(token) {
    if (!token) return true;
    
    const expiry = getTokenExpiry(token);
    return expiry < Date.now();
}

/**
 * Token'ın yakında süresi dolacak mı kontrol eder.
 * 
 * @param {string} token - JWT token
 * @returns {boolean} Token süresi yakında dolacaksa true, aksi takdirde false
 */
function isTokenExpiringSoon(token) {
    if (!token) return false;
    
    const expiry = getTokenExpiry(token);
    return expiry - Date.now() < REFRESH_THRESHOLD_MS;
}

/**
 * Token'ları localStorage'a kaydeder.
 * 
 * @param {Object} tokens - Token bilgilerini içeren nesne
 * @param {string} tokens.access - Access token
 * @param {string} tokens.refresh - Refresh token
 */
function saveTokens(tokens) {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
    
    const expiry = getTokenExpiry(tokens.access);
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiry);
    
    // Sessiz yenileme için zamanlayıcı başlat
    setupSilentRefresh();
}

/**
 * Access token'ı localStorage'dan alır.
 * 
 * @returns {string|null} Access token veya null
 */
function getAccessToken() {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Refresh token'ı localStorage'dan alır.
 * 
 * @returns {string|null} Refresh token veya null
 */
function getRefreshToken() {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Tüm token bilgilerini temizler.
 */
function clearTokens() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_EXPIRY_KEY);
    
    // Sessiz yenileme zamanlayıcısını durdur
    if (refreshTimer) {
        clearTimeout(refreshTimer);
        refreshTimer = null;
    }
}

/**
 * Token'ı sunucudan yeniler.
 * 
 * @returns {Promise<Object>} Yeni token bilgilerini içeren nesne
 */
async function refreshToken() {
    try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
            throw new Error('Refresh token bulunamadı');
        }
        
        // Sunucudan yeni token al
        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });
        
        if (!response.ok) {
            throw new Error('Token yenileme başarısız');
        }
        
        const data = await response.json();
        
        // Yeni token'ları sakla
        saveTokens({
            access: data.access,
            refresh: data.refresh || refreshToken,
        });
        
        return data;
    } catch (error) {
        console.error('Token yenileme hatası:', error);
        // Hata durumunda kullanıcıyı çıkış yap
        clearTokens();
        window.location.href = '/accounts/login/?session_expired=true';
        throw error;
    }
}

/**
 * Sessiz yenileme zamanlayıcısını kurar.
 */
function setupSilentRefresh() {
    // Önceki zamanlayıcıyı temizle
    if (refreshTimer) {
        clearTimeout(refreshTimer);
    }
    
    const accessToken = getAccessToken();
    if (!accessToken) return;
    
    const expiry = parseInt(localStorage.getItem(TOKEN_EXPIRY_KEY), 10);
    if (!expiry) return;
    
    // Token'ın süresi ne zaman dolacak hesapla
    const timeUntilExpiry = expiry - Date.now();
    
    // Eşik değerinden ne kadar önce yenileneceğini hesapla
    const refreshTime = Math.max(0, timeUntilExpiry - REFRESH_THRESHOLD_MS);
    
    // Zamanlayıcıyı kur
    refreshTimer = setTimeout(async () => {
        try {
            await refreshToken();
        } catch (error) {
            console.error('Sessiz yenileme hatası:', error);
        }
    }, refreshTime);
}

/**
 * Sayfada önceki oturumu devam ettirmek için kontrol.
 */
function initTokenRefresh() {
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();
    
    // Token yoksa veya süresi dolduysa kontrol etme
    if (!accessToken || !refreshToken) {
        return;
    }
    
    if (isTokenExpired(accessToken)) {
        // Token süresi dolmuş, yenilemeyi dene
        refreshToken().catch(() => {
            // Hata durumunda işlem yapma, zaten refreshToken içinde hata ele alınıyor
        });
    } else if (isTokenExpiringSoon(accessToken)) {
        // Token süresi yakında dolacak, yenilemeyi dene
        refreshToken().catch(() => {
            // Hata durumunda işlem yapma, zaten refreshToken içinde hata ele alınıyor
        });
    } else {
        // Token geçerli, sessiz yenileme için zamanlayıcı kur
        setupSilentRefresh();
    }
}

// Sayfa yüklendiğinde token durumunu kontrol et
document.addEventListener('DOMContentLoaded', initTokenRefresh);

// Auth modülünü dışa aktar
window.JWTAuth = {
    saveTokens,
    getAccessToken,
    getRefreshToken,
    clearTokens,
    refreshToken,
    isTokenExpired,
    isTokenExpiringSoon,
    initTokenRefresh
}; 