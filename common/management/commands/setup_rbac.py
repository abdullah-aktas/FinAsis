# -*- coding: utf-8 -*-
"""
RBAC Setup Management Command
Rol tabanlı yetki sistemini kurar ve yapılandırır
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from common.permissions import ROLE_CATEGORIES, APP_PERMISSIONS
from common.auto_role_assignment import create_required_groups, assign_roles_to_user
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'RBAC sistemini kurar ve yapılandırır'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Mevcut izinleri sıfırla ve yeniden oluştur',
        )
        parser.add_argument(
            '--assign-users',
            action='store_true',
            help='Tüm kullanıcılara otomatik rol ata',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Detaylı çıktı göster',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('FinAsis RBAC (Role-Based Access Control) Kurulumu'))
        self.stdout.write(self.style.SUCCESS('='*80))
        
        verbose = options['verbose']
        
        # 1. Grupları oluştur
        self.stdout.write('\n[1] Adim 1: Gruplar olusturuluyor...')
        created_count = create_required_groups()
        self.stdout.write(self.style.SUCCESS(f'   OK: {created_count} yeni grup olusturuldu'))
        
        # 2. Grup izinlerini ayarla
        self.stdout.write('\n[2] Adim 2: Grup izinleri ayarlaniyor...')
        self._setup_group_permissions(verbose)
        
        # 3. Kullanıcılara rol ata (eğer istenirse)
        if options['assign_users']:
            self.stdout.write('\n[3] Adim 3: Kullanicilara rol ataniyor...')
            self._assign_roles_to_users(verbose)
        
        # 4. Özet bilgi
        self.stdout.write('\n' + '='*80)
        self._print_summary()
        
        self.stdout.write(self.style.SUCCESS('\nSUCCESS: RBAC kurulumu basariyla tamamlandi!'))
        self.stdout.write(self.style.WARNING('\nIPUCU: python manage.py setup_rbac --assign-users ile tum kullanicilara rol atayabilirsiniz'))
    
    def _setup_group_permissions(self, verbose):
        """Gruplara izinleri atar"""
        # Her app için izinleri ayarla
        for app_name, permissions in APP_PERMISSIONS.items():
            if verbose:
                self.stdout.write(f'\n   [APP] {app_name} app izinleri ayarlaniyor...')
            
            try:
                # ContentType'ı al (varsa)
                ct = ContentType.objects.filter(app_label=app_name).first()
                if not ct:
                    if verbose:
                        self.stdout.write(self.style.WARNING(f'      WARNING: ContentType bulunamadi: {app_name}'))
                    continue
                
                # Her permission için
                for perm_name, roles in permissions.items():
                    # Django permission koduna çevir
                    django_perm_codename = f'{perm_name}_{ct.model}'
                    
                    # Permission'ı al veya oluştur
                    perm, created = Permission.objects.get_or_create(
                        codename=django_perm_codename,
                        defaults={
                            'name': f'Can {perm_name} {ct.model}',
                            'content_type': ct
                        }
                    )
                    
                    # Her role için grubu bul ve izni ekle
                    for role in roles:
                        if role not in ROLE_CATEGORIES:
                            continue
                        
                        for group_name in ROLE_CATEGORIES[role]['groups']:
                            try:
                                group = Group.objects.get(name=group_name)
                                group.permissions.add(perm)
                                
                                if verbose:
                                    self.stdout.write(f'      OK: {group_name} -> {perm_name}')
                            except Group.DoesNotExist:
                                if verbose:
                                    self.stdout.write(self.style.WARNING(f'      WARNING: Grup bulunamadi: {group_name}'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'      ERROR: {e}'))
        
        self.stdout.write(self.style.SUCCESS('   OK: Grup izinleri ayarlandi'))
    
    def _assign_roles_to_users(self, verbose):
        """Tüm kullanıcılara otomatik rol atar"""
        users = User.objects.all()
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                assign_roles_to_user(user, force=True)
                success_count += 1
                
                if verbose:
                    groups = user.groups.values_list('name', flat=True)
                    self.stdout.write(f'   OK: {user.username}: {", ".join(groups)}')
            except Exception as e:
                error_count += 1
                if verbose:
                    self.stdout.write(self.style.ERROR(f'   ERROR: {user.username}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'   OK: {success_count} kullaniciya rol atandi'))
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING: {error_count} kullanicida hata olustu'))
    
    def _print_summary(self):
        """Ozet bilgi yazdir"""
        # Grup sayisi
        total_groups = Group.objects.count()
        self.stdout.write(f'[STATS] Toplam Grup: {total_groups}')
        
        # Kullanici sayisi
        total_users = User.objects.count()
        users_with_groups = User.objects.filter(groups__isnull=False).distinct().count()
        users_without_groups = total_users - users_with_groups
        coverage = (users_with_groups / total_users * 100) if total_users > 0 else 0
        
        self.stdout.write(f'[USERS] Toplam Kullanici: {total_users}')
        self.stdout.write(f'   OK: Gruplu: {users_with_groups} ({coverage:.1f}%)')
        if users_without_groups > 0:
            self.stdout.write(self.style.WARNING(f'   WARNING: Grupsuz: {users_without_groups}'))
        
        # Rol kategorileri
        self.stdout.write(f'\n[ROLES] Rol Kategorileri: {len(ROLE_CATEGORIES)}')
        for role_name, role_info in ROLE_CATEGORIES.items():
            self.stdout.write(f'   - {role_name} (Level {role_info["level"]}) - {role_info["description"]}')
        
        # App permissions
        self.stdout.write(f'\n[APPS] Korunan Appler: {len(APP_PERMISSIONS)}')
        for app_name in APP_PERMISSIONS.keys():
            self.stdout.write(f'   - {app_name}')

