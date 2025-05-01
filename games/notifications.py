# -*- coding: utf-8 -*-
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
from enum import Enum

class NotificationType(Enum):
    ACHIEVEMENT = "achievement"
    QUEST = "quest"
    FRIEND = "friend"
    CLAN = "clan"
    SYSTEM = "system"
    TRADE = "trade"
    EVENT = "event"
    SECURITY = "security"
    TOURNAMENT = "tournament"
    TRAINING = "training"
    COMMUNITY = "community"
    PERFORMANCE = "performance"
    CLOUD_SAVE = "cloud_save"

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Notification:
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    timestamp: datetime
    read: bool
    data: Dict
    player_id: str

class NotificationSystem:
    def __init__(self):
        self.notifications: Dict[str, List[Notification]] = {}
        self.unread_counts: Dict[str, int] = {}
        
    def send_notification(self, player_id: str, notification_type: NotificationType,
                         title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM,
                         data: Optional[Dict] = None) -> Notification:
        """Bildirim gönderir"""
        notification = Notification(
            id=str(uuid.uuid4()),
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            timestamp=datetime.now(),
            read=False,
            data=data if data is not None else {},
            player_id=player_id
        )
        
        if player_id not in self.notifications:
            self.notifications[player_id] = []
            self.unread_counts[player_id] = 0
            
        self.notifications[player_id].append(notification)
        self.unread_counts[player_id] += 1
        
        return notification
        
    def get_player_notifications(self, player_id: str,
                               unread_only: bool = False,
                               limit: int = 50) -> List[Notification]:
        """Oyuncunun bildirimlerini getirir"""
        if player_id not in self.notifications:
            return []
            
        notifications = self.notifications[player_id]
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
            
        return sorted(notifications, key=lambda x: x.timestamp, reverse=True)[:limit]
        
    def mark_as_read(self, player_id: str, notification_id: str) -> bool:
        """Bildirimi okundu olarak işaretler"""
        if player_id in self.notifications:
            for notification in self.notifications[player_id]:
                if notification.id == notification_id and not notification.read:
                    notification.read = True
                    self.unread_counts[player_id] -= 1
                    return True
        return False
        
    def mark_all_as_read(self, player_id: str) -> bool:
        """Tüm bildirimleri okundu olarak işaretler"""
        if player_id in self.notifications:
            for notification in self.notifications[player_id]:
                if not notification.read:
                    notification.read = True
            self.unread_counts[player_id] = 0
            return True
        return False
        
    def delete_notification(self, player_id: str, notification_id: str) -> bool:
        """Bildirimi siler"""
        if player_id in self.notifications:
            for i, notification in enumerate(self.notifications[player_id]):
                if notification.id == notification_id:
                    if not notification.read:
                        self.unread_counts[player_id] -= 1
                    del self.notifications[player_id][i]
                    return True
        return False
        
    def clear_old_notifications(self, player_id: str, days: int = 30) -> int:
        """Eski bildirimleri temizler"""
        if player_id not in self.notifications:
            return 0
            
        cutoff_date = datetime.now() - timedelta(days=days)
        old_count = len(self.notifications[player_id])
        
        self.notifications[player_id] = [
            n for n in self.notifications[player_id]
            if n.timestamp > cutoff_date
        ]
        
        # Okunmamış sayısını güncelle
        self.unread_counts[player_id] = len([
            n for n in self.notifications[player_id]
            if not n.read
        ])
        
        return old_count - len(self.notifications[player_id])
        
    def get_unread_count(self, player_id: str) -> int:
        """Okunmamış bildirim sayısını getirir"""
        return self.unread_counts.get(player_id, 0)
        
    def send_achievement_notification(self, player_id: str, achievement_name: str):
        """Başarı bildirimi gönderir"""
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.ACHIEVEMENT,
            title="Yeni Başarı",
            message=f"'{achievement_name}' başarımını kazandın!",
            priority=NotificationPriority.HIGH
        )
        
    def send_quest_notification(self, player_id: str, quest_name: str, completed: bool):
        """Görev bildirimi gönderir"""
        status = "tamamladın" if completed else "başladın"
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.QUEST,
            title="Görev Güncellemesi",
            message=f"'{quest_name}' görevini {status}!",
            priority=NotificationPriority.MEDIUM
        )
        
    def send_friend_notification(self, player_id: str, friend_name: str, action: str):
        """Arkadaş bildirimi gönderir"""
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.FRIEND,
            title="Arkadaş Güncellemesi",
            message=f"{friend_name} seni {action}!",
            priority=NotificationPriority.LOW
        )
        
    def send_security_notification(self, player_id: str, message: str,
                                 priority: NotificationPriority = NotificationPriority.HIGH):
        """Güvenlik bildirimi gönderir"""
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.SECURITY,
            title="Güvenlik Uyarısı",
            message=message,
            priority=priority
        )
        
    def send_tournament_notification(self, player_id: str, tournament_name: str, event_type: str):
        """Turnuva bildirimi gönderir"""
        messages = {
            "start": f"'{tournament_name}' turnuvası başladı!",
            "join": f"'{tournament_name}' turnuvasına katıldın!",
            "win": f"'{tournament_name}' turnuvasını kazandın!",
            "end": f"'{tournament_name}' turnuvası sona erdi!"
        }
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.TOURNAMENT,
            title="Turnuva Güncellemesi",
            message=messages.get(event_type, "Turnuva güncellemesi"),
            priority=NotificationPriority.HIGH
        )
        
    def send_training_notification(self, player_id: str, module_name: str, progress: int):
        """Eğitim modülü bildirimi gönderir"""
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.TRAINING,
            title="Eğitim Güncellemesi",
            message=f"'{module_name}' modülünde %{progress} ilerleme kaydettin!",
            priority=NotificationPriority.MEDIUM
        )
        
    def send_community_notification(self, player_id: str, content_name: str, status: str):
        """Topluluk içeriği bildirimi gönderir"""
        messages = {
            "approved": f"'{content_name}' içeriğin onaylandı!",
            "rejected": f"'{content_name}' içeriğin reddedildi.",
            "featured": f"'{content_name}' içeriğin öne çıkanlar arasına seçildi!"
        }
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.COMMUNITY,
            title="Topluluk Güncellemesi",
            message=messages.get(status, "Topluluk güncellemesi"),
            priority=NotificationPriority.MEDIUM
        )
        
    def send_performance_notification(self, player_id: str, metric: str, value: float):
        """Performans bildirimi gönderir"""
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.PERFORMANCE,
            title="Performans Uyarısı",
            message=f"{metric} değeri {value} seviyesine ulaştı!",
            priority=NotificationPriority.LOW
        )
        
    def send_cloud_save_notification(self, player_id: str, status: str):
        """Bulut kayıt bildirimi gönderir"""
        messages = {
            "success": "Oyun durumun başarıyla kaydedildi!",
            "error": "Oyun durumu kaydedilirken bir hata oluştu!",
            "sync": "Oyun durumun diğer cihazlarla senkronize edildi!"
        }
        return self.send_notification(
            player_id=player_id,
            notification_type=NotificationType.CLOUD_SAVE,
            title="Bulut Kayıt Güncellemesi",
            message=messages.get(status, "Bulut kayıt güncellemesi"),
            priority=NotificationPriority.LOW
        ) 