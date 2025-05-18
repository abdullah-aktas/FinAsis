// FinAsis Temel JavaScript Fonksiyonları
document.addEventListener('DOMContentLoaded', function() {
    // Aktif menü öğesini işaretle
    highlightActiveMenuItem();
    
    // Form validasyonlarını etkinleştir
    enableFormValidations();
    
    // Bootstrap bileşenlerini etkinleştir
    initializeBootstrapComponents();
    
    // Alert mesajlarını otomatik kapat
    initializeAlerts();
    
    // Form gönderimlerini güçlendir
    enhanceFormSubmissions();
    
    // CSRF token için AJAX ayarı
    setupAjaxCSRF();
});

// CSRF token için AJAX ayarı
function setupAjaxCSRF() {
    // CSRF token'ı al
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
    
    // CSRF token'ı AJAX isteklerine ekle
    const csrftoken = getCookie('csrftoken');
    
    // JQuery kullanılıyorsa
    if (typeof $ !== 'undefined') {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }
    
    // Fetch API için
    document.addEventListener('fetch', function(event) {
        if (event.request.method !== 'GET') {
            event.request.headers.set('X-CSRFToken', csrftoken);
        }
    });
}

// Aktif menü öğesini işaretleme
function highlightActiveMenuItem() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.nav-link, .dropdown-item');
    
    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && (href === currentPath || currentPath.startsWith(href) && href !== '/')) {
            item.classList.add('active');
            
            // Eğer dropdown içindeyse, dropdown toggle'ı da aktif yap
            const dropdownParent = item.closest('.dropdown');
            if (dropdownParent) {
                const dropdownToggle = dropdownParent.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
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

// Bootstrap bileşenlerini etkinleştirme
function initializeBootstrapComponents() {
    // Bootstrap 5 tooltip'lerini etkinleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Bootstrap 5 popover'larını etkinleştir
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
        
        // Kollapsleri etkinleştir
        var collapseElementList = [].slice.call(document.querySelectorAll('.collapse'));
        collapseElementList.map(function (collapseEl) {
            return new bootstrap.Collapse(collapseEl, {
                toggle: false
            });
        });
        
        // Dropdown menüleri etkinleştir
        var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    } else {
        console.warn('Bootstrap JS kütüphanesi yüklenemedi!');
    }
}

// Alert mesajlarını otomatik kapatma
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

// Form gönderimlerini güçlendirme
function enhanceFormSubmissions() {
    const forms = document.querySelectorAll('form:not(.no-enhance)');
    
    forms.forEach(form => {
        // Form gönderildiğinde gönder düğmesini devre dışı bırak
        form.addEventListener('submit', function() {
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            submitButtons.forEach(button => {
                button.disabled = true;
                if (button.tagName === 'BUTTON') {
                    const originalText = button.innerHTML;
                    button.setAttribute('data-original-text', originalText);
                    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> İşleniyor...';
                }
            });
        });
    });
} 