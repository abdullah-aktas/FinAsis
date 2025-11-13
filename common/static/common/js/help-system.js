/**
 * FinAsis Help System
 * Tooltip, Guided Tour ve Contextual Help
 */

class FinAsisHelpSystem {
    constructor() {
        this.currentTour = null;
        this.currentStep = 0;
        this.init();
    }
    
    init() {
        this.initTooltips();
        this.initKeyboardShortcuts();
        this.checkFirstTimeUser();
    }
    
    // ========================================================================
    // TOOLTIPS
    // ========================================================================
    
    initTooltips() {
        // Bootstrap tooltip'lerini aktifleştir
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Custom tooltip'ler için
        document.querySelectorAll('[data-help-key]').forEach(element => {
            const helpKey = element.getAttribute('data-help-key');
            this.loadTooltip(element, helpKey);
        });
    }
    
    async loadTooltip(element, helpKey) {
        try {
            const response = await fetch(`/help/api/tooltip/${helpKey}/`);
            const data = await response.json();
            
            if (data.success && data.tooltip) {
                element.setAttribute('data-bs-toggle', 'tooltip');
                element.setAttribute('title', data.tooltip);
                new bootstrap.Tooltip(element);
            }
        } catch (error) {
            console.error('Tooltip load error:', error);
        }
    }
    
    // ========================================================================
    // GUIDED TOUR
    // ========================================================================
    
    async startTour(tourName) {
        try {
            const response = await fetch(`/help/api/tour/${tourName}/`);
            const data = await response.json();
            
            if (data.success && data.tour) {
                this.currentTour = data.tour;
                this.currentStep = 0;
                this.showTourStep();
            }
        } catch (error) {
            console.error('Tour load error:', error);
        }
    }
    
    showTourStep() {
        if (!this.currentTour || !this.currentTour.steps) return;
        
        const step = this.currentTour.steps[this.currentStep];
        if (!step) return;
        
        // Hedef elementi bul
        const target = document.querySelector(step.target);
        if (!target) {
            console.warn('Tour target not found:', step.target);
            this.nextStep();
            return;
        }
        
        // Overlay oluştur
        this.createTourOverlay(target, step);
        
        // Elementi highlight et
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        target.classList.add('help-tour-highlight');
    }
    
    createTourOverlay(target, step) {
        // Mevcut overlay'i kaldır
        this.closeTour();
        
        // Overlay div oluştur
        const overlay = document.createElement('div');
        overlay.id = 'tourOverlay';
        overlay.className = 'help-tour-overlay';
        
        // Popover oluştur
        const popover = document.createElement('div');
        popover.className = `help-tour-popover help-tour-${step.position || 'bottom'}`;
        
        popover.innerHTML = `
            <div class="help-tour-header">
                <h5>${step.title}</h5>
                <button class="btn btn-sm btn-link text-white" onclick="helpSystem.closeTour()">
                    <i class="bi-x-lg"></i>
                </button>
            </div>
            <div class="help-tour-body">
                ${step.content}
            </div>
            <div class="help-tour-footer">
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        ${this.currentStep + 1} / ${this.currentTour.steps.length}
                    </small>
                    <div>
                        ${this.currentStep > 0 ? 
                            '<button class="btn btn-sm btn-outline-secondary me-2" onclick="helpSystem.prevStep()">Geri</button>' : ''}
                        ${this.currentStep < this.currentTour.steps.length - 1 ?
                            '<button class="btn btn-sm btn-primary" onclick="helpSystem.nextStep()">İleri</button>' :
                            '<button class="btn btn-sm btn-success" onclick="helpSystem.closeTour()">Bitir</button>'}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Popover'ı target'ın yanına konumlandır
        this.positionPopover(target, popover, step.position || 'bottom');
        overlay.appendChild(popover);
    }
    
    positionPopover(target, popover, position) {
        const targetRect = target.getBoundingClientRect();
        
        // Offset değerleri
        const offset = 20;
        
        switch (position) {
            case 'top':
                popover.style.left = `${targetRect.left}px`;
                popover.style.top = `${targetRect.top - offset}px`;
                popover.style.transform = 'translateY(-100%)';
                break;
            case 'bottom':
                popover.style.left = `${targetRect.left}px`;
                popover.style.top = `${targetRect.bottom + offset}px`;
                break;
            case 'left':
                popover.style.left = `${targetRect.left - offset}px`;
                popover.style.top = `${targetRect.top}px`;
                popover.style.transform = 'translateX(-100%)';
                break;
            case 'right':
                popover.style.left = `${targetRect.right + offset}px`;
                popover.style.top = `${targetRect.top}px`;
                break;
        }
    }
    
    nextStep() {
        if (this.currentStep < this.currentTour.steps.length - 1) {
            this.currentStep++;
            this.showTourStep();
        }
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.showTourStep();
        }
    }
    
    closeTour() {
        const overlay = document.getElementById('tourOverlay');
        if (overlay) {
            overlay.remove();
        }
        
        // Highlight'ı kaldır
        document.querySelectorAll('.help-tour-highlight').forEach(el => {
            el.classList.remove('help-tour-highlight');
        });
        
        this.currentTour = null;
        this.currentStep = 0;
    }
    
    // ========================================================================
    // KEYBOARD SHORTCUTS
    // ========================================================================
    
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt+H: Help widget
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                this.toggleHelpWidget();
            }
            
            // Alt+S: Search
            if (e.altKey && e.key === 's') {
                e.preventDefault();
                document.getElementById('globalSearch')?.focus();
            }
            
            // Ctrl+K: Command palette
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.openCommandPalette();
            }
            
            // Esc: Close modals
            if (e.key === 'Escape') {
                this.closeTour();
            }
        });
    }
    
    toggleHelpWidget() {
        if (typeof toggleHelpWidget === 'function') {
            toggleHelpWidget();
        }
    }
    
    openCommandPalette() {
        // Command palette implementasyonu (opsiyonel)
        console.log('Command palette - Coming soon!');
    }
    
    // ========================================================================
    // FIRST TIME USER
    // ========================================================================
    
    checkFirstTimeUser() {
        const isFirstTime = !localStorage.getItem('finasis_toured');
        
        if (isFirstTime) {
            // İlk kez kullanıcıya hoş geldin mesajı
            setTimeout(() => {
                if (confirm('FinAsis\'e hoş geldiniz! Hızlı tur yapmak ister misiniz?')) {
                    this.startTour('first_time_user');
                    localStorage.setItem('finasis_toured', 'true');
                }
            }, 2000);
        }
    }
    
    // ========================================================================
    // CONTEXTUAL HELP
    // ========================================================================
    
    showContextualHelp(context) {
        const helpDiv = document.getElementById('contextualHelp');
        if (!helpDiv) return;
        
        // Context'e göre yardım içeriği göster
        const helpContent = {
            'invoice_form': `
                <div class="alert alert-info alert-sm">
                    <strong><i class="bi-lightbulb me-1"></i> İpucu:</strong>
                    Müşteri bulunamıyorsa "+" ile hızlıca ekleyebilirsiniz.
                </div>
            `,
            'dashboard': `
                <div class="alert alert-info alert-sm">
                    <strong><i class="bi-lightbulb me-1"></i> İpucu:</strong>
                    Widget'ları sürükle-bırak ile düzenleyebilirsiniz.
                </div>
            `
        };
        
        if (helpContent[context]) {
            helpDiv.innerHTML = helpContent[context];
        }
    }
}

// Global instance oluştur
const helpSystem = new FinAsisHelpSystem();

// Global fonksiyonlar
function startGuidedTour(tourName) {
    helpSystem.startTour(tourName);
}

function showHelp(context) {
    helpSystem.showContextualHelp(context);
}

