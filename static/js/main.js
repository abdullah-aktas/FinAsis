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

// Sayfa yüklendiğinde çalışacak fonksiyonlar
document.addEventListener('DOMContentLoaded', function() {
    // Aktif menü öğesini işaretle
    highlightActiveMenuItem();
    
    // Form validasyonlarını etkinleştir
    enableFormValidations();
    
    // Tooltip ve Popover'ları etkinleştir
    enableTooltipsAndPopovers();
    
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

    // Alert mesajlarını otomatik kapat
    initializeAlerts();

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

// Form validasyonlarını etkinleştirme
function enableFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Tooltip ve Popover'ları etkinleştirme
function enableTooltipsAndPopovers() {
    // Bootstrap 5 tooltip'lerini etkinleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Bootstrap 5 popover'larını etkinleştir
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
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
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                alert.classList.add('fade-out');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }, 5000);
        }
    });
}

// Form gönderimlerini yönetme
function handleFormSubmit(formElement, successCallback, errorCallback) {
    formElement.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        try {
            const formData = new FormData(formElement);
            const response = await fetch(formElement.action, {
                method: formElement.method,
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (successCallback) successCallback(data);
            } else {
                throw new Error('Form submission failed');
            }
        } catch (error) {
            if (errorCallback) errorCallback(error);
        }
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