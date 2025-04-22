from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from virtual_company.models import VirtualCompany

User = get_user_model()

@receiver(post_save, sender=User)
def create_virtual_company(sender, instance, created, **kwargs):
    """
    Kullanıcı oluşturulduğunda, eğer öğrenci veya öğretmen rolündeyse
    otomatik olarak sanal şirket oluşturur.
    """
    if created and instance.role in ['student', 'teacher']:
        # Kullanıcıyı sanal şirket kullanıcısı olarak işaretle
        instance.is_virtual_company_user = True
        instance.save(update_fields=['is_virtual_company_user'])
        
        # Sanal şirket oluştur
        VirtualCompany.objects.create(
            name=f"{instance.get_full_name() or instance.username} Ltd. Şti.",
            description="Sanal şirket açıklaması",
            industry="Teknoloji",
            founded_date="2024-01-01",
            email=instance.email,
            phone="5555555555",
            address="Sanal adres",
            tax_number="1234567890",
            tax_office="Sanal Vergi Dairesi",
            created_by=instance
        )

"""
Kullanıcı kimlik doğrulama ve hesap işlemleri için sinyaller.
"""
import logging
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('security')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Yeni bir kullanıcı oluşturulduğunda çağrılır.
    İlgili kullanıcı profili veya diğer bağlantılı kayıtları oluşturmak için kullanılabilir.
    """
    if created:
        # Örnek: Kullanıcıya bağlı bir profil, ayarlar vb. oluşturma
        logger.info(f"Yeni kullanıcı oluşturuldu: {instance.username}")


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Kullanıcı başarıyla giriş yaptığında çağrılır.
    
    IP adresi kaydedilir ve başarısız giriş denemeleri sıfırlanır.
    """
    if not user or not request:
        return
    
    # IP adresini kaydet
    if hasattr(user, 'last_login_ip'):
        ip_address = get_client_ip(request)
        user.last_login_ip = ip_address
    
    # Başarısız giriş denemelerini sıfırla
    if hasattr(user, 'failed_login_attempts'):
        user.failed_login_attempts = 0
        user.account_locked_until = None
    
    # Değişiklikleri kaydet
    user.save(update_fields=['last_login_ip', 'failed_login_attempts', 'account_locked_until'])
    
    logger.info(f"Kullanıcı giriş yaptı: {user.username} (IP: {get_client_ip(request)})")


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    Kullanıcı giriş denemesi başarısız olduğunda çağrılır.
    
    Başarısız giriş denemelerini izler ve gerekirse hesabı kilitler.
    """
    if not request:
        return
        
    # IP bilgisini al
    ip_address = get_client_ip(request)
    
    # Kullanıcı adı veya e-posta ile kullanıcıyı bul
    username = credentials.get('username', None)
    if not username:
        logger.warning(f"Başarısız giriş denemesi: Bilinmeyen kullanıcı (IP: {ip_address})")
        return
        
    # Kullanıcı modeli
    User = sender
    
    try:
        # Kullanıcı adı veya e-posta ile kullanıcıyı bul 
        user = User.objects.filter(username=username).first() or User.objects.filter(email=username).first()
        
        if user:
            # Kullanıcı kilitli mi kontrol et
            if hasattr(user, 'account_locked_until') and user.account_locked_until and user.account_locked_until > timezone.now():
                logger.warning(f"Kilitli hesaba giriş denemesi: {user.username} (IP: {ip_address})")
                return
                
            # Başarısız giriş denemelerini artır
            if hasattr(user, 'failed_login_attempts'):
                user.failed_login_attempts += 1
                
                # Maksimum deneme sayısını aştıysa hesabı kilitle
                max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
                if user.failed_login_attempts >= max_attempts:
                    block_time = getattr(settings, 'LOGIN_BLOCK_TIME_MINUTES', 15)
                    user.account_locked_until = timezone.now() + timedelta(minutes=block_time)
                    logger.warning(f"Hesap kilitlendi: {user.username} (IP: {ip_address})")
                
                user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
            
            logger.warning(f"Başarısız giriş denemesi: {user.username} (IP: {ip_address})")
        else:
            logger.warning(f"Başarısız giriş denemesi: Kullanıcı bulunamadı - {username} (IP: {ip_address})")
    
    except Exception as e:
        logger.error(f"Giriş denemesi izlenirken hata: {str(e)}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    Kullanıcı çıkış yaptığında çağrılır.
    """
    if user and request:
        logger.info(f"Kullanıcı çıkış yaptı: {user.username} (IP: {get_client_ip(request)})")


def get_client_ip(request):
    """
    İstemci IP adresini alır.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip 