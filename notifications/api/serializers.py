from rest_framework import serializers
from notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """
    Bildirim modeli için serializer.
    """
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 
                 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_notification_type(self, value):
        """Bildirim tipinin geçerli olduğunu kontrol eder."""
        valid_types = ['info', 'success', 'warning', 'error']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Geçersiz bildirim tipi. Geçerli tipler: {', '.join(valid_types)}"
            )
        return value

    def validate(self, attrs):
        """
        Bildirim verilerini doğrula
        """
        if attrs.get('related_object_id') and not attrs.get('related_object_type'):
            raise serializers.ValidationError({
                'related_object_type': 'İlişkili nesne ID\'si verildiğinde nesne tipi de belirtilmelidir.'
            })
        return attrs 