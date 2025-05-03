/*
 * Bildirim modülü
 * WebSocket ve bildirim yönetimi
 */

export async function initNotifications() {
    try {
        // WebSocket bağlantısı
        const socket = new WebSocket(`ws://${window.location.host}/ws/notifications/`);
        
        // WebSocket olayları
        socket.onopen = () => {
            console.log('WebSocket bağlantısı kuruldu');
        };
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleNotification(data);
        };
        
        socket.onclose = () => {
            console.log('WebSocket bağlantısı kapandı');
            // Yeniden bağlanma denemesi
            setTimeout(initNotifications, 5000);
        };
        
        // Bildirim izinlerini kontrol et
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('Bildirim izni verildi');
            }
        }
        
        return true;
    } catch (error) {
        console.error('Bildirim modülü başlatma hatası:', error);
        return false;
    }
}

function handleNotification(data) {
    // Bildirim türüne göre işlem yap
    switch (data.type) {
        case 'new_post':
            showNewPostNotification(data);
            break;
        case 'like':
            showLikeNotification(data);
            break;
        case 'comment':
            showCommentNotification(data);
            break;
        case 'follow':
            showFollowNotification(data);
            break;
        default:
            console.warn('Bilinmeyen bildirim türü:', data.type);
    }
}

function showNewPostNotification(data) {
    const notification = new Notification('Yeni Gönderi', {
        body: `${data.sender} yeni bir gönderi paylaştı`,
        icon: '/static/img/notification.png'
    });
    
    notification.onclick = () => {
        window.location.href = `/post/${data.post_id}/`;
    };
}

function showLikeNotification(data) {
    const notification = new Notification('Beğeni', {
        body: `${data.sender} gönderinizi beğendi`,
        icon: '/static/img/like.png'
    });
    
    notification.onclick = () => {
        window.location.href = `/post/${data.post_id}/`;
    };
}

function showCommentNotification(data) {
    const notification = new Notification('Yorum', {
        body: `${data.sender} gönderinize yorum yaptı`,
        icon: '/static/img/comment.png'
    });
    
    notification.onclick = () => {
        window.location.href = `/post/${data.post_id}/`;
    };
}

function showFollowNotification(data) {
    const notification = new Notification('Takip', {
        body: `${data.sender} sizi takip etmeye başladı`,
        icon: '/static/img/follow.png'
    });
    
    notification.onclick = () => {
        window.location.href = `/profile/${data.sender}/`;
    };
} 