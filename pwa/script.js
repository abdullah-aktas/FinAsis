// DOM Elementleri
const fileInput = document.getElementById('fileInput');
const uploadQueue = document.getElementById('uploadQueue');
const shareQueue = document.getElementById('shareQueue');
const shareTitle = document.getElementById('shareTitle');
const shareText = document.getElementById('shareText');
const shareUrl = document.getElementById('shareUrl');

// Kuyruk Yönetimi
let uploadQueueItems = [];
let shareQueueItems = [];

// Dosya Yükleme İşlemleri
fileInput.addEventListener('change', handleFileSelect);

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    files.forEach(file => {
        if (isValidFileType(file)) {
            addToUploadQueue(file);
        } else {
            showNotification('Desteklenmeyen dosya tipi. Lütfen PDF veya Excel dosyası yükleyin.', 'error');
        }
    });
}

function isValidFileType(file) {
    const validTypes = [
        'application/pdf',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    return validTypes.includes(file.type);
}

function addToUploadQueue(file) {
    uploadQueueItems.push(file);
    updateUploadQueueDisplay();
    showNotification(`${file.name} yükleme kuyruğuna eklendi`, 'success');
}

function removeFromUploadQueue(index) {
    uploadQueueItems.splice(index, 1);
    updateUploadQueueDisplay();
}

function updateUploadQueueDisplay() {
    uploadQueue.innerHTML = uploadQueueItems.map((file, index) => `
        <div class="queue-item">
            <span>${file.name}</span>
            <button onclick="removeFromUploadQueue(${index})" class="btn btn-sm btn-danger">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

// Paylaşım İşlemleri
function queueShare() {
    const title = shareTitle.value.trim();
    const text = shareText.value.trim();
    const url = shareUrl.value.trim();

    if (title || text || url) {
        const shareItem = { title, text, url };
        addToShareQueue(shareItem);
        clearShareForm();
    } else {
        showNotification('Lütfen en az bir alan doldurun', 'warning');
    }
}

function addToShareQueue(shareItem) {
    shareQueueItems.push(shareItem);
    updateShareQueueDisplay();
    showNotification('Paylaşım kuyruğa eklendi', 'success');
}

function removeFromShareQueue(index) {
    shareQueueItems.splice(index, 1);
    updateShareQueueDisplay();
}

function updateShareQueueDisplay() {
    shareQueue.innerHTML = shareQueueItems.map((item, index) => `
        <div class="queue-item">
            <div class="share-details">
                ${item.title ? `<strong>${item.title}</strong><br>` : ''}
                ${item.text ? `<span>${item.text}</span><br>` : ''}
                ${item.url ? `<a href="${item.url}" target="_blank">${item.url}</a>` : ''}
            </div>
            <button onclick="removeFromShareQueue(${index})" class="btn btn-sm btn-danger">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

function clearShareForm() {
    shareTitle.value = '';
    shareText.value = '';
    shareUrl.value = '';
}

// Bağlantı Yönetimi
window.addEventListener('online', handleOnline);
window.addEventListener('offline', handleOffline);

function handleOnline() {
    showNotification('Bağlantı sağlandı', 'success');
    processQueues();
}

function handleOffline() {
    showNotification('Çevrimdışı moda geçildi', 'warning');
}

function processQueues() {
    processUploadQueue();
    processShareQueue();
}

async function processUploadQueue() {
    if (uploadQueueItems.length === 0) return;

    for (const file of uploadQueueItems) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('type', getFileType(file));

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                removeFromUploadQueue(uploadQueueItems.indexOf(file));
                showNotification(`${file.name} başarıyla yüklendi`, 'success');
            } else {
                showNotification(`${file.name} yüklenirken hata oluştu`, 'error');
            }
        } catch (error) {
            console.error('Yükleme hatası:', error);
            showNotification(`${file.name} yüklenirken hata oluştu`, 'error');
        }
    }
}

async function processShareQueue() {
    if (shareQueueItems.length === 0) return;

    for (const item of shareQueueItems) {
        try {
            const response = await fetch('/share', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(item)
            });

            if (response.ok) {
                removeFromShareQueue(shareQueueItems.indexOf(item));
                showNotification('Paylaşım başarılı', 'success');
            } else {
                showNotification('Paylaşım sırasında hata oluştu', 'error');
            }
        } catch (error) {
            console.error('Paylaşım hatası:', error);
            showNotification('Paylaşım sırasında hata oluştu', 'error');
        }
    }
}

function getFileType(file) {
    if (file.type === 'application/pdf') return 'pdf';
    if (file.type === 'application/vnd.ms-excel') return 'excel';
    if (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') return 'excel';
    return 'unknown';
}

// Bildirim Sistemi
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle';
        case 'error':
            return 'fa-exclamation-circle';
        case 'warning':
            return 'fa-exclamation-triangle';
        default:
            return 'fa-info-circle';
    }
}

// Sayfa Yüklendiğinde
document.addEventListener('DOMContentLoaded', () => {
    if (navigator.onLine) {
        window.location.href = '/';
    }
}); 