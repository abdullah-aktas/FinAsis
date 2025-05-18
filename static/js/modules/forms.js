/*
 * Form modülü
 * Form doğrulama ve AJAX işlemleri
 */

export async function initForms() {
    try {
        // Form doğrulama
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', handleFormSubmit);
        });
        
        // Dosya yükleme işlemleri
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', handleFileUpload);
        });
        
        return true;
    } catch (error) {
        console.error('Form modülü başlatma hatası:', error);
        return false;
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    try {
        // Form verilerini topla
        const formData = new FormData(form);
        
        // Submit butonunu devre dışı bırak
        submitButton.disabled = true;
        submitButton.textContent = 'İşleniyor...';
        
        // AJAX isteği gönder
        const response = await fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Başarılı yanıt
            showSuccessMessage(data.message || 'İşlem başarılı');
            
            // Form temizleme
            if (data.clear_form) {
                form.reset();
            }
            
            // Yönlendirme
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        } else {
            // Hata yanıtı
            showErrorMessage(data.message || 'Bir hata oluştu');
        }
    } catch (error) {
        console.error('Form gönderme hatası:', error);
        showErrorMessage('Bir hata oluştu');
    } finally {
        // Submit butonunu tekrar etkinleştir
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
}

async function handleFileUpload(event) {
    const input = event.target;
    const file = input.files[0];
    const maxSize = input.dataset.maxSize || 5 * 1024 * 1024; // 5MB varsayılan
    
    if (file.size > maxSize) {
        showErrorMessage(`Dosya boyutu çok büyük. Maksimum ${maxSize / 1024 / 1024}MB olmalıdır.`);
        input.value = '';
        return;
    }
    
    // Dosya önizleme
    if (file.type.startsWith('image/')) {
        const preview = document.createElement('img');
        preview.style.maxWidth = '200px';
        preview.style.maxHeight = '200px';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            input.parentNode.appendChild(preview);
        };
        reader.readAsDataURL(file);
    }
}

function showSuccessMessage(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-success';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showErrorMessage(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-error';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
} 