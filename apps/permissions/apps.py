# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permissions'
    verbose_name = 'İzin Yönetimi'

    def ready(self):
        """
        Uygulama başlatıldığında çalışacak kodlar
        """
        # Sinyalleri kaydet
        from . import signals

        # Varsayılan rolleri oluştur
        post_migrate.connect(self.create_default_roles, sender=self)
        
        # Cache'i temizle
        self.clear_cache()
        
        logger.info("İzin yönetimi uygulaması başlatıldı")

    def create_default_roles(self, sender, **kwargs):
        """
        Varsayılan rolleri oluştur
        """
        from .models import Role, Permission
        from django.contrib.auth.models import Group

        # Varsayılan roller
        default_roles = [
            {
                'name': 'Sistem Yöneticisi',
                'code': 'admin',
                'description': 'Sistem yöneticisi rolü',
                'role_type': 'system'
            },
            {
                'name': 'İçerik Yöneticisi',
                'code': 'content_manager',
                'description': 'İçerik yönetimi rolü',
                'role_type': 'content'
            },
            {
                'name': 'Kullanıcı Yöneticisi',
                'code': 'user_manager',
                'description': 'Kullanıcı yönetimi rolü',
                'role_type': 'user'
            },
            {
                'name': 'Rapor Yöneticisi',
                'code': 'report_manager',
                'description': 'Rapor yönetimi rolü',
                'role_type': 'report'
            }
        ]

        # Her rol için izinleri oluştur
        for role_data in default_roles:
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults=role_data
            )
            
            if created:
                logger.info(f"Varsayılan rol oluşturuldu: {role.name}")
                
                # Rol için varsayılan izinleri ata
                permissions = self.get_default_permissions(role_data['code'])
                role.permissions.set(permissions)
                
                # Django Group oluştur
                group, _ = Group.objects.get_or_create(name=role_data['code'])
                group.permissions.set(permissions)

    def get_default_permissions(self, role_code):
        """
        Rol koduna göre varsayılan izinleri döndür
        """
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        # Tüm izinleri al
        all_permissions = Permission.objects.all()
        
        # Rol bazlı izin filtreleme
        if role_code == 'admin':
            return all_permissions
        elif role_code == 'content_manager':
            content_types = ContentType.objects.filter(
                app_label__in=['content', 'blog', 'pages']
            )
            return Permission.objects.filter(content_type__in=content_types)
        elif role_code == 'user_manager':
            content_types = ContentType.objects.filter(
                app_label__in=['auth', 'users']
            )
            return Permission.objects.filter(content_type__in=content_types)
        elif role_code == 'report_manager':
            content_types = ContentType.objects.filter(
                app_label__in=['reports', 'analytics']
            )
            return Permission.objects.filter(content_type__in=content_types)
        
        return Permission.objects.none()

    def clear_cache(self):
        """
        Uygulama başlatıldığında cache'i temizle
        """
        cache.delete_pattern('role:*')
        cache.delete_pattern('user_roles:*')
        cache.delete_pattern('user_permissions:*')
        cache.delete_pattern('delegation:*')
        cache.delete_pattern('2fa_status:*')
        cache.delete_pattern('ip_whitelist:*')
        
        logger.info("İzin yönetimi cache'i temizlendi") 