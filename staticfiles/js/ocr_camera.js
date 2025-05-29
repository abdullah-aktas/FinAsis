class OCRCamera {
    constructor(options = {}) {
        this.videoElement = options.videoElement || document.createElement('video');
        this.canvasElement = options.canvasElement || document.createElement('canvas');
        this.captureButton = options.captureButton;
        this.uploadButton = options.uploadButton;
        this.previewContainer = options.previewContainer;
        this.statusElement = options.statusElement;
        
        this.stream = null;
        this.initialized = false;
        
        this.bindEvents();
    }
    
    async initialize() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                }
            });
            
            this.videoElement.srcObject = this.stream;
            this.videoElement.play();
            
            this.initialized = true;
            this.updateStatus('Kamera hazır');
            
            return true;
        } catch (error) {
            this.updateStatus('Kamera erişimi hatası: ' + error.message);
            return false;
        }
    }
    
    bindEvents() {
        if (this.captureButton) {
            this.captureButton.addEventListener('click', () => this.captureImage());
        }
        
        if (this.uploadButton) {
            this.uploadButton.addEventListener('click', () => this.uploadImage());
        }
    }
    
    updateStatus(message) {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
    }
    
    async captureImage() {
        if (!this.initialized) {
            this.updateStatus('Kamera başlatılmadı');
            return;
        }
        
        try {
            // Canvas boyutlarını video boyutlarına ayarla
            this.canvasElement.width = this.videoElement.videoWidth;
            this.canvasElement.height = this.videoElement.videoHeight;
            
            // Video görüntüsünü canvas'a çiz
            const context = this.canvasElement.getContext('2d');
            context.drawImage(this.videoElement, 0, 0);
            
            // Önizleme göster
            if (this.previewContainer) {
                const previewImage = document.createElement('img');
                previewImage.src = this.canvasElement.toDataURL('image/jpeg');
                this.previewContainer.innerHTML = '';
                this.previewContainer.appendChild(previewImage);
            }
            
            this.updateStatus('Görüntü yakalandı');
            return true;
        } catch (error) {
            this.updateStatus('Görüntü yakalama hatası: ' + error.message);
            return false;
        }
    }
    
    async uploadImage() {
        if (!this.canvasElement.width) {
            this.updateStatus('Yüklenecek görüntü yok');
            return;
        }
        
        try {
            this.updateStatus('Görüntü yükleniyor...');
            
            // Canvas'ı blob'a dönüştür
            const blob = await new Promise(resolve => 
                this.canvasElement.toBlob(resolve, 'image/jpeg', 0.95)
            );
            
            // FormData oluştur
            const formData = new FormData();
            formData.append('file', blob, 'capture.jpg');
            
            // OCR API'sine gönder
            const response = await fetch('/api/ocr/process/', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateStatus('OCR işlemi tamamlandı');
                this.onOCRComplete(result.data);
            } else {
                this.updateStatus('OCR hatası: ' + result.error);
            }
            
            return result;
        } catch (error) {
            this.updateStatus('Yükleme hatası: ' + error.message);
            return null;
        }
    }
    
    onOCRComplete(data) {
        // Bu metod alt sınıflar tarafından override edilebilir
        console.log('OCR Sonuçları:', data);
    }
    
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.initialized = false;
            this.updateStatus('Kamera kapatıldı');
        }
    }
}

// Kullanım örneği:
document.addEventListener('DOMContentLoaded', () => {
    const camera = new OCRCamera({
        videoElement: document.getElementById('camera-preview'),
        captureButton: document.getElementById('capture-button'),
        uploadButton: document.getElementById('upload-button'),
        previewContainer: document.getElementById('preview-container'),
        statusElement: document.getElementById('camera-status')
    });
    
    // Kamera başlat
    camera.initialize();
    
    // OCR sonuçlarını işle
    camera.onOCRComplete = (data) => {
        // Form alanlarını doldur
        if (data.invoice_number) {
            document.getElementById('invoice-number').value = data.invoice_number;
        }
        if (data.date) {
            document.getElementById('invoice-date').value = data.date;
        }
        if (data.total) {
            document.getElementById('invoice-total').value = data.total;
        }
        if (data.tax_rate) {
            document.getElementById('invoice-tax-rate').value = data.tax_rate;
        }
        if (data.company_name) {
            document.getElementById('company-name').value = data.company_name;
        }
    };
}); 