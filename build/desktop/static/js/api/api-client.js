/**
 * API İstemcisi
 * 
 * Bu modül, backend API'si ile iletişim için Axios tabanlı bir istemci sağlar.
 * JWT token'larını otomatik olarak isteklere ekler ve token'ın geçerliliğini kontrol eder.
 */

// Temel API URL
const API_BASE_URL = '/api';

// Axios istemcisi
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// İstek interceptor'ı - token ekleme ve kontrol
apiClient.interceptors.request.use(
    async (config) => {
        // Token kontrolü yoksa direkt gönder (login gibi)
        if (config.skipAuthRefresh) {
            return config;
        }
        
        let token = JWTAuth.getAccessToken();
        
        // Token yoksa, config'de belirtilmişse hata ver
        if (!token && !config.allowNoAuth) {
            return Promise.reject(new Error('Token bulunamadı'));
        }
        
        // Token var ama süresi dolmuşsa yenile
        if (token && JWTAuth.isTokenExpired(token)) {
            try {
                const refreshResult = await JWTAuth.refreshToken();
                token = refreshResult.access;
            } catch (error) {
                // Yenileme başarısız olursa ve allowNoAuth yoksa hata ver
                if (!config.allowNoAuth) {
                    return Promise.reject(error);
                }
            }
        }
        
        // Token var ama yakında süresi dolacaksa arka planda yenile
        if (token && JWTAuth.isTokenExpiringSoon(token)) {
            // Mevcut isteği engellemeden arka planda yenile
            JWTAuth.refreshToken().catch(error => {
                console.warn('Arka plan token yenileme hatası:', error);
            });
        }
        
        // Token varsa ekle
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Yanıt interceptor'ı - hata yönetimi
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        // Orijinal istek yapılandırması
        const originalRequest = error.config;
        
        // Orijinal istek zaten yeniden denenmiş veya auth atlanıyorsa, hatayı devam ettir
        if (originalRequest._retry || originalRequest.skipAuthRefresh) {
            return Promise.reject(error);
        }
        
        // 401 Unauthorized hatası ve token varsa
        if (error.response && error.response.status === 401 && JWTAuth.getRefreshToken()) {
            originalRequest._retry = true;
            
            try {
                // Token'ı yenile
                const refreshResult = await JWTAuth.refreshToken();
                
                // Yeni token ile isteği tekrarla
                originalRequest.headers.Authorization = `Bearer ${refreshResult.access}`;
                return apiClient(originalRequest);
            } catch (refreshError) {
                // Token yenileme başarısız olursa, oturum sona erdi
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
);

// API endpointleri
const api = {
    // Kimlik doğrulama
    auth: {
        login: (username, password, rememberMe = false, deviceType = 'web') => 
            apiClient.post('/token/', { username, password, remember_me: rememberMe, device_type: deviceType }, { skipAuthRefresh: true }),
        
        refreshToken: () => 
            apiClient.post('/token/refresh/', { refresh: JWTAuth.getRefreshToken() }, { skipAuthRefresh: true }),
        
        logout: () => 
            apiClient.post('/token/blacklist/', { refresh: JWTAuth.getRefreshToken() })
                .finally(() => JWTAuth.clearTokens()),
    },
    
    // Kullanıcı işlemleri
    user: {
        getProfile: () => apiClient.get('/users/me/'),
        updateProfile: (userData) => apiClient.put('/users/me/', userData),
        changePassword: (oldPassword, newPassword) => apiClient.post('/users/change-password/', { old_password: oldPassword, new_password: newPassword }),
    },
    
    // Diğer API endpointleri burada tanımlanabilir
    // ...
};

// Global API nesnesini dışa aktar
window.API = api; 