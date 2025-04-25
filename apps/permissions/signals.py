from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User, Permission
from .models import (
    Role, UserRole, Resource, ResourcePermission,
    PermissionDelegation, AuditLog, TwoFactorAuth, IPWhitelist
)
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Role)
def role_post_save(sender, instance, created, **kwargs):
    """
    Rol kaydedildikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern('role:*')
    cache.delete_pattern('user_roles:*')
    
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        user=instance.created_by,
        action=action,
        model='Role',
        object_id=instance.id,
        details=f'Role {action.lower()}d: {instance.name}'
    )
    logger.info(f'Role {action.lower()}d: {instance.name}')

@receiver(post_delete, sender=Role)
def role_post_delete(sender, instance, **kwargs):
    """
    Rol silindikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern('role:*')
    cache.delete_pattern('user_roles:*')
    
    AuditLog.objects.create(
        user=instance.created_by,
        action='DELETE',
        model='Role',
        object_id=instance.id,
        details=f'Role deleted: {instance.name}'
    )
    logger.info(f'Role deleted: {instance.name}')

@receiver(post_save, sender=UserRole)
def user_role_post_save(sender, instance, created, **kwargs):
    """
    Kullanıcı rolü kaydedildikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern(f'user_roles:{instance.user.id}:*')
    cache.delete_pattern(f'user_permissions:{instance.user.id}:*')
    
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        user=instance.assigned_by,
        action=action,
        model='UserRole',
        object_id=instance.id,
        details=f'User role {action.lower()}d: {instance.user.username} - {instance.role.name}'
    )
    logger.info(f'User role {action.lower()}d: {instance.user.username} - {instance.role.name}')

@receiver(post_delete, sender=UserRole)
def user_role_post_delete(sender, instance, **kwargs):
    """
    Kullanıcı rolü silindikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern(f'user_roles:{instance.user.id}:*')
    cache.delete_pattern(f'user_permissions:{instance.user.id}:*')
    
    AuditLog.objects.create(
        user=instance.assigned_by,
        action='DELETE',
        model='UserRole',
        object_id=instance.id,
        details=f'User role deleted: {instance.user.username} - {instance.role.name}'
    )
    logger.info(f'User role deleted: {instance.user.username} - {instance.role.name}')

@receiver(post_save, sender=PermissionDelegation)
def permission_delegation_post_save(sender, instance, created, **kwargs):
    """
    İzin devri kaydedildikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern(f'delegation:{instance.delegatee.id}:*')
    cache.delete_pattern(f'user_permissions:{instance.delegatee.id}:*')
    
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        user=instance.delegator,
        action=action,
        model='PermissionDelegation',
        object_id=instance.id,
        details=f'Permission delegation {action.lower()}d: {instance.delegator.username} -> {instance.delegatee.username}'
    )
    logger.info(f'Permission delegation {action.lower()}d: {instance.delegator.username} -> {instance.delegatee.username}')

@receiver(post_delete, sender=PermissionDelegation)
def permission_delegation_post_delete(sender, instance, **kwargs):
    """
    İzin devri silindikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern(f'delegation:{instance.delegatee.id}:*')
    cache.delete_pattern(f'user_permissions:{instance.delegatee.id}:*')
    
    AuditLog.objects.create(
        user=instance.delegator,
        action='DELETE',
        model='PermissionDelegation',
        object_id=instance.id,
        details=f'Permission delegation deleted: {instance.delegator.username} -> {instance.delegatee.username}'
    )
    logger.info(f'Permission delegation deleted: {instance.delegator.username} -> {instance.delegatee.username}')

@receiver(post_save, sender=TwoFactorAuth)
def two_factor_auth_post_save(sender, instance, created, **kwargs):
    """
    İki faktörlü kimlik doğrulama kaydedildikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern(f'2fa_status:{instance.user.id}:*')
    
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        user=instance.user,
        action=action,
        model='TwoFactorAuth',
        object_id=instance.id,
        details=f'2FA {action.lower()}d for user: {instance.user.username}'
    )
    logger.info(f'2FA {action.lower()}d for user: {instance.user.username}')

@receiver(post_delete, sender=TwoFactorAuth)
def two_factor_auth_post_delete(sender, instance, **kwargs):
    """
    İki faktörlü kimlik doğrulama silindikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern(f'2fa_status:{instance.user.id}:*')
    
    AuditLog.objects.create(
        user=instance.user,
        action='DELETE',
        model='TwoFactorAuth',
        object_id=instance.id,
        details=f'2FA deleted for user: {instance.user.username}'
    )
    logger.info(f'2FA deleted for user: {instance.user.username}')

@receiver(post_save, sender=IPWhitelist)
def ip_whitelist_post_save(sender, instance, created, **kwargs):
    """
    IP beyaz listesi kaydedildikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern('ip_whitelist:*')
    
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        user=instance.created_by,
        action=action,
        model='IPWhitelist',
        object_id=instance.id,
        details=f'IP whitelist {action.lower()}d: {instance.ip_address}'
    )
    logger.info(f'IP whitelist {action.lower()}d: {instance.ip_address}')

@receiver(post_delete, sender=IPWhitelist)
def ip_whitelist_post_delete(sender, instance, **kwargs):
    """
    IP beyaz listesi silindikten sonra cache'i temizle ve denetim kaydı oluştur.
    """
    cache.delete_pattern('ip_whitelist:*')
    
    AuditLog.objects.create(
        user=instance.created_by,
        action='DELETE',
        model='IPWhitelist',
        object_id=instance.id,
        details=f'IP whitelist deleted: {instance.ip_address}'
    )
    logger.info(f'IP whitelist deleted: {instance.ip_address}')

@receiver(pre_save, sender=PermissionDelegation)
def check_permission_delegation_expiry(sender, instance, **kwargs):
    """
    İzin devrinin süresi dolmuşsa otomatik olarak devre dışı bırak.
    """
    if instance.expires_at and instance.expires_at < timezone.now():
        instance.is_active = False
        logger.info(f'Permission delegation expired: {instance.delegator.username} -> {instance.delegatee.username}') 