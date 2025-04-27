/*
 * Ana JavaScript dosyası
 * Modern ve modüler yapıda JavaScript kodu
 */

// ES6+ modül sistemi
import { initNotifications } from './modules/notifications.js';
import { initForms } from './modules/forms.js';
import { initUI } from './modules/ui.js';
import { initAPI } from './modules/api.js';

// Ana uygulama sınıfı
class FinAsisApp {
    constructor() {
        this.init();
    }

    async init() {
        try {
            // Modülleri başlat
            await this.initializeModules();
            
            // PWA desteği
            if ('serviceWorker' in navigator) {
                this.registerServiceWorker();
            }
            
            // Çevrimdışı desteği
            this.setupOfflineSupport();
            
            // Performans izleme
            this.setupPerformanceMonitoring();
        } catch (error) {
            console.error('Uygulama başlatma hatası:', error);
        }
    }

    async initializeModules() {
        // Modülleri paralel olarak başlat
        await Promise.all([
            initNotifications(),
            initForms(),
            initUI(),
            initAPI()
        ]);
    }

    registerServiceWorker() {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/service-worker.js')
                .then(registration => {
                    console.log('ServiceWorker başarıyla kaydedildi:', registration.scope);
                })
                .catch(error => {
                    console.error('ServiceWorker kaydı başarısız:', error);
                });
        });
    }

    setupOfflineSupport() {
        window.addEventListener('online', () => {
            this.showNotification('Bağlantı yeniden sağlandı', 'success');
        });

        window.addEventListener('offline', () => {
            this.showNotification('Çevrimdışı moda geçildi', 'warning');
        });
    }

    setupPerformanceMonitoring() {
        // Performans ölçümleri
        if ('performance' in window) {
            const timing = performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            console.log(`Sayfa yüklenme süresi: ${loadTime}ms`);
        }
    }

    showNotification(message, type = 'info') {
        // Bildirim göster
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    new FinAsisApp();
});

// DOM yüklendiğinde çalışacak fonksiyonlar
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips'i aktifleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Bootstrap popovers'ı aktifleştir
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Alert mesajlarını otomatik kapat
    setupAlertDismissal();

    // Form doğrulama
    setupFormValidation();

    // Aktif menü öğesini işaretle
    highlightActiveMenuItem();
    
    // Klavye navigasyonunu etkinleştir
    enableKeyboardNavigation();

    // Navbar scroll efekti
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });

    // Oyun kontrolleri
    const gameContainer = document.getElementById('game-container');
    if (gameContainer) {
        // Oyun başlatma
        const startButton = document.getElementById('start-game');
        if (startButton) {
            startButton.addEventListener('click', function() {
                console.log('Oyun başlatılıyor...');
            });
        }

        // Oyunu duraklatma
        const pauseButton = document.getElementById('pause-game');
        if (pauseButton) {
            pauseButton.addEventListener('click', function() {
                console.log('Oyun duraklatılıyor...');
            });
        }

        // Oyunu devam ettirme
        const resumeButton = document.getElementById('resume-game');
        if (resumeButton) {
            resumeButton.addEventListener('click', function() {
                console.log('Oyun devam ediyor...');
            });
        }

        // Oyunu bitirme
        const endButton = document.getElementById('end-game');
        if (endButton) {
            endButton.addEventListener('click', function() {
                console.log('Oyun sonlandırılıyor...');
            });
        }
    }
});

// Aktif menü öğesini işaretleme
function highlightActiveMenuItem() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.nav-link');
    
    menuItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
            item.setAttribute('aria-current', 'page');
        }
    });
}

// Klavye navigasyonunu etkinleştirme
function enableKeyboardNavigation() {
    // Tab ile gezinme için tüm etkileşimli öğelere tabindex ekle
    const interactiveElements = document.querySelectorAll('a, button, input, select, textarea');
    interactiveElements.forEach((element, index) => {
        if (!element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', '0');
        }
    });
    
    // Enter tuşu ile tıklama
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.classList.contains('nav-link')) {
                activeElement.click();
            }
        }
    });
}

// Alert mesajlarını otomatik kapatma
function setupAlertDismissal() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Form doğrulama
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// AJAX form gönderimi
function submitFormAjax(formElement, successCallback, errorCallback) {
    const formData = new FormData(formElement);
    const url = formElement.getAttribute('action');
    const method = formElement.getAttribute('method') || 'POST';

    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (successCallback) successCallback(data);
    })
    .catch(error => {
        if (errorCallback) errorCallback(error);
        console.error('Form gönderimi hatası:', error);
    });
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

// Dinamik içerik yükleme
function loadContent(url, targetElement) {
    fetch(url)
        .then(response => response.text())
        .then(html => {
            targetElement.innerHTML = html;
        })
        .catch(error => {
            console.error('İçerik yükleme hatası:', error);
            targetElement.innerHTML = '<div class="alert alert-danger">İçerik yüklenirken bir hata oluştu.</div>';
        });
}

// Sayfa yönlendirme
function redirectTo(url, delay = 0) {
    setTimeout(() => {
        window.location.href = url;
    }, delay);
}

// Mobil menü kontrolü
function toggleMobileMenu() {
    const navbar = document.querySelector('.navbar-collapse');
    if (navbar.classList.contains('show')) {
        navbar.classList.remove('show');
    } else {
        navbar.classList.add('show');
    }
}

// Sayfa yukarı çık butonu
window.onscroll = function() {
    const scrollButton = document.getElementById('scrollTopBtn');
    if (scrollButton) {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            scrollButton.style.display = 'block';
        } else {
            scrollButton.style.display = 'none';
        }
    }
};

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Tema değiştirme
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Tema değişikliği olayını tetikle
    const event = new CustomEvent('themeChanged', { detail: { theme: newTheme } });
    document.dispatchEvent(event);
}

// Sayfa yüklendiğinde tema kontrolü
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
});

// Dinamik form alanları ekleme/çıkarma
function initializeDynamicFormFields() {
    const addButtons = document.querySelectorAll('.add-form-field');
    const removeButtons = document.querySelectorAll('.remove-form-field');
    
    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const template = this.dataset.template;
            const container = document.querySelector(this.dataset.container);
            const newField = document.createElement('div');
            newField.innerHTML = template;
            container.appendChild(newField);
        });
    });
    
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.form-field').remove();
        });
    });
} 