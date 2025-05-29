from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"[Signal] Yeni kullanıcı oluşturuldu: {instance.username}")
        # Burada kullanıcı oluşturulduğunda yapılacak işlemleri ekleyebilirsiniz.
        # Örneğin, kullanıcıya varsayılan bir profil oluşturma işlemi yapılabilir.