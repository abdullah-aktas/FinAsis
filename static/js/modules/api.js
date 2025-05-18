/*
 * API modülü
 * API istekleri ve yanıt yönetimi
 */

const API_BASE_URL = '/api/v1/';

export async function initAPI() {
    try {
        // API istekleri için interceptor
        window.fetch = createFetchInterceptor(window.fetch);
        
        return true;
    } catch (error) {
        console.error('API modülü başlatma hatası:', error);
        return false;
    }
}

function createFetchInterceptor(originalFetch) {
    return async function(url, options = {}) {
        // CSRF token ekle
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            options.headers = {
                ...options.headers,
                'X-CSRFToken': csrfToken
            };
        }

        // API URL'lerini normalize et
        if (url.startsWith('/api/')) {
            url = API_BASE_URL + url.slice(5);
        }

        try {
            const response = await originalFetch(url, options);
            
            // 401 hatası durumunda oturumu sonlandır
            if (response.status === 401) {
                window.location.href = '/account/login/';
                return;
            }
            
            // 403 hatası durumunda yetkisiz erişim
            if (response.status === 403) {
                throw new Error('Bu işlem için yetkiniz bulunmuyor');
            }
            
            return response;
        } catch (error) {
            console.error('API isteği hatası:', error);
            throw error;
        }
    };
}

// API yardımcı fonksiyonları
export async function get(endpoint, params = {}) {
    const url = new URL(API_BASE_URL + endpoint);
    url.search = new URLSearchParams(params).toString();
    
    const response = await fetch(url);
    return response.json();
}

export async function post(endpoint, data = {}) {
    const response = await fetch(API_BASE_URL + endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    return response.json();
}

export async function put(endpoint, data = {}) {
    const response = await fetch(API_BASE_URL + endpoint, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    return response.json();
}

export async function del(endpoint) {
    const response = await fetch(API_BASE_URL + endpoint, {
        method: 'DELETE'
    });
    
    return response.json();
}

// CSRF token alma
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 