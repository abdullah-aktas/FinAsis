from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from virtual_company.models import VirtualCompany

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
            user=instance,
            company_name=f"{instance.get_full_name() or instance.username} Ltd. Şti."
        ) 