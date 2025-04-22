from django.core.cache import cache
from django.utils import timezone
from .models import ChatSession, ChatMessage, AssistantPerformance
import logging
import time
import json

logger = logging.getLogger(__name__)

class AssistantService:
    def __init__(self):
        self.cache_timeout = 3600  # 1 saat

    def process_message(self, session, content, message_type='text'):
        """
        Kullanıcı mesajını işler ve yanıt oluşturur.
        """
        start_time = time.time()
        
        try:
            # Mesajı kaydet
            user_message = ChatMessage.objects.create(
                session=session,
                content=content,
                message_type=message_type,
                is_user=True
            )

            # Yanıt oluştur
            response = self._generate_response(session, content, message_type)
            
            # Asistan yanıtını kaydet
            assistant_message = ChatMessage.objects.create(
                session=session,
                content=response['content'],
                message_type=response['message_type'],
                is_user=False,
                metadata=response.get('metadata', {})
            )

            # Performans metriklerini kaydet
            response_time = (time.time() - start_time) * 1000  # milisaniye cinsinden
            self._save_performance_metrics(
                session=session,
                response_time=response_time,
                token_count=response.get('token_count', 0),
                capability_used=response.get('capability_used')
            )

            # Oturum durumunu güncelle
            session.last_activity = timezone.now()
            session.save()

            return {
                'message_id': assistant_message.id,
                'content': assistant_message.content,
                'message_type': assistant_message.message_type,
                'metadata': assistant_message.metadata,
                'created_at': assistant_message.created_at
            }

        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {str(e)}")
            raise

    def regenerate_response(self, message):
        """
        Belirli bir mesaj için yanıtı yeniden oluşturur.
        """
        try:
            session = message.session
            response = self._generate_response(
                session,
                message.content,
                message.message_type
            )

            # Mevcut mesajı güncelle
            message.content = response['content']
            message.message_type = response['message_type']
            message.metadata = response.get('metadata', {})
            message.save()

            return {
                'message_id': message.id,
                'content': message.content,
                'message_type': message.message_type,
                'metadata': message.metadata,
                'created_at': message.created_at
            }

        except Exception as e:
            logger.error(f"Yanıt yeniden oluşturma hatası: {str(e)}")
            raise

    def _generate_response(self, session, content, message_type):
        """
        Asistan yanıtını oluşturur.
        """
        # TODO: Gerçek yanıt oluşturma mantığı burada implemente edilecek
        # Şimdilik örnek bir yanıt döndürüyoruz
        return {
            'content': f"Örnek yanıt: {content}",
            'message_type': message_type,
            'token_count': len(content.split()),
            'capability_used': 'default'
        }

    def _save_performance_metrics(self, session, response_time, token_count, capability_used):
        """
        Performans metriklerini kaydeder.
        """
        AssistantPerformance.objects.create(
            session=session,
            response_time=response_time,
            token_count=token_count,
            capability_used=capability_used
        )

    def get_cached_data(self, key):
        """
        Önbellekten veri alır.
        """
        return cache.get(key)

    def set_cached_data(self, key, value):
        """
        Veriyi önbelleğe kaydeder.
        """
        cache.set(key, value, self.cache_timeout) 