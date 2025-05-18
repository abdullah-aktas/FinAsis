/*
 * UI modülü
 * Kullanıcı arayüzü işlemleri
 */

export async function initUI() {
    try {
        // Tooltip ve Popover'ları etkinleştir
        enableTooltipsAndPopovers();
        
        // Navbar scroll efekti
        setupNavbarScroll();
        
        // Alert mesajlarını otomatik kapat
        initializeAlerts();
        
        // Dinamik form alanları
        initializeDynamicFormFields();
        
        return true;
    } catch (error) {
        console.error('UI modülü başlatma hatası:', error);
        return false;
    }
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

// Navbar scroll efekti
function setupNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
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