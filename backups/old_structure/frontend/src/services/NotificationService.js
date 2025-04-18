class NotificationService {
  static async requestPermission() {
    try {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    } catch (error) {
      console.error('Bildirim izni alınamadı:', error);
      return false;
    }
  }

  static async subscribeToPushNotifications() {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: process.env.REACT_APP_VAPID_PUBLIC_KEY
      });

      // Backend'e subscription bilgisini gönder
      await fetch('/api/notifications/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subscription)
      });

      return subscription;
    } catch (error) {
      console.error('Push notification aboneliği başarısız:', error);
      throw error;
    }
  }

  static async unsubscribeFromPushNotifications() {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      
      if (subscription) {
        await subscription.unsubscribe();
        
        // Backend'e unsubscribe bilgisini gönder
        await fetch('/api/notifications/unsubscribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(subscription)
        });
      }
    } catch (error) {
      console.error('Push notification aboneliği iptal edilemedi:', error);
      throw error;
    }
  }
}

export default NotificationService; 