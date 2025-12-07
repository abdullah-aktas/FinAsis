# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission as DjangoPermission

from .models import Permission, Role, UserRole

User = get_user_model()


@receiver(post_save, sender=Permission)
def permission_post_save(sender, instance, created, **kwargs):
    """
    Yetki oluşturulduğunda veya güncellendiğinde çalışır.
    Django native Permission ile otomatik eşleştirme sağlar.
    """
    if not instance.django_permission:
        django_perm, _ = DjangoPermission.objects.get_or_create(
            codename=instance.codename,
            content_type=instance.content_type,
            defaults={"name": instance.name},
        )
        instance.django_permission = django_perm
        instance.save(update_fields=["django_permission"])
    else:
        # İsim güncellendiyse native permission'ı da güncelle
        if instance.django_permission.name != instance.name:
            instance.django_permission.name = instance.name
            instance.django_permission.save()


@receiver(post_delete, sender=Permission)
def permission_post_delete(sender, instance, **kwargs):
    """
    Yetki silindiğinde çalışır.
    Django native Permission'ı da siler.
    """
    if instance.django_permission:
        instance.django_permission.delete()


@receiver(post_save, sender=Role)
def role_post_save(sender, instance, created, **kwargs):
    """
    Rol oluşturulduğunda veya güncellendiğinde çalışır.
    """
    if created:
        # Yeni rol oluşturulduğunda yapılacak işlemler
        pass
    else:
        # Rol güncellendiğinde yapılacak işlemler
        pass


@receiver(post_delete, sender=Role)
def role_post_delete(sender, instance, **kwargs):
    """
    Rol silindiğinde çalışır.
    """
    # Rol silindiğinde yapılacak işlemler
    pass


@receiver(post_save, sender=UserRole)
def user_role_post_save(sender, instance, created, **kwargs):
    """
    Kullanıcı rolü oluşturulduğunda veya güncellendiğinde çalışır.
    """
    if created:
        # Yeni kullanıcı rolü oluşturulduğunda yapılacak işlemler
        pass
    else:
        # Kullanıcı rolü güncellendiğinde yapılacak işlemler
        pass


@receiver(post_delete, sender=UserRole)
def user_role_post_delete(sender, instance, **kwargs):
    """
    Kullanıcı rolü silindiğinde çalışır.
    """
    # Kullanıcı rolü silindiğinde yapılacak işlemler
    pass
