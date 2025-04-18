from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.virtual_company.models import VirtualCompany

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