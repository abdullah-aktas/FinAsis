"""
Otomatik Rol Atama Yönetim Komutu
Kullanıcılara otomatik rol atama işlemlerini yönetir
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from common.auto_role_assignment import (
    assign_roles_to_user,
    bulk_assign_roles,
    create_required_groups,
    get_role_assignment_summary,
    AUTO_ROLE_RULES,
    ADMIN_USER_RULES,
    EMAIL_DOMAIN_RULES
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Kullanıcılara otomatik rol atama işlemlerini yönetir'

    def add_arguments(self, parser):
        parser.add_argument(
            '--assign',
            action='store_true',
            help='Tüm kullanıcılara rol atar',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut rolleri siler ve yeniden atar',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Belirli bir kullanıcıya rol atar (username)',
        )
        parser.add_argument(
            '--user-type',
            type=str,
            help='Belirli user_type sahip kullanıcılara rol atar',
        )
        parser.add_argument(
            '--create-groups',
            action='store_true',
            help='Gerekli grupları oluşturur',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Rol atama durumunun özetini gösterir',
        )
        parser.add_argument(
            '--list-rules',
            action='store_true',
            help='Otomatik rol atama kurallarını listeler',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Sadece simülasyon yapar, değişiklik yapmaz',
        )

    def handle(self, *args, **options):
        if options['list_rules']:
            self.list_rules()
            return

        if options['summary']:
            self.show_summary()
            return

        if options['create_groups']:
            self.create_groups(options['dry_run'])
            return

        if options['assign']:
            self.assign_all_users(options['force'], options['dry_run'])
            return

        if options['user']:
            self.assign_single_user(options['user'], options['force'], options['dry_run'])
            return

        if options['user_type']:
            self.assign_by_user_type(options['user_type'], options['force'], options['dry_run'])
            return

        # Hiçbir argüman verilmemişse help göster
        self.print_help(prog_name='manage.py', subcommand='auto_assign_roles')

    def list_rules(self):
        """Otomatik rol atama kurallarını listeler"""
        self.stdout.write(
            self.style.SUCCESS('\n🔧 Otomatik Rol Atama Kuralları')
        )
        self.stdout.write('=' * 60)

        self.stdout.write(
            self.style.WARNING('\n📋 UserType Bazlı Kurallar:')
        )
        for user_type, rule in AUTO_ROLE_RULES.items():
            self.stdout.write(f"\n  • {user_type}:")
            self.stdout.write(f"    Rol: {rule['role']}")
            self.stdout.write(f"    Gruplar: {', '.join(rule['groups'])}")
            self.stdout.write(f"    Açıklama: {rule['description']}")

        self.stdout.write(
            self.style.WARNING('\n👤 Admin Kullanıcı Kuralları:')
        )
        for admin_type, rule in ADMIN_USER_RULES.items():
            self.stdout.write(f"\n  • {admin_type}:")
            self.stdout.write(f"    Rol: {rule['role']}")
            self.stdout.write(f"    Gruplar: {', '.join(rule['groups'])}")
            self.stdout.write(f"    Açıklama: {rule['description']}")

        self.stdout.write(
            self.style.WARNING('\n📧 Email Domain Kuralları:')
        )
        for domain, rule in EMAIL_DOMAIN_RULES.items():
            self.stdout.write(f"\n  • {domain}:")
            self.stdout.write(f"    Rol: {rule['role']}")
            self.stdout.write(f"    Gruplar: {', '.join(rule['groups'])}")
            self.stdout.write(f"    Açıklama: {rule['description']}")

    def show_summary(self):
        """Rol atama durumu özetini gösterir"""
        summary = get_role_assignment_summary()
        
        self.stdout.write(
            self.style.SUCCESS('\n📊 Rol Atama Durumu Özeti')
        )
        self.stdout.write('=' * 50)
        
        self.stdout.write(f"\n👥 Toplam Kullanıcı: {summary['total_users']}")
        self.stdout.write(f"✅ Gruplu Kullanıcı: {summary['users_with_groups']}")
        self.stdout.write(f"❌ Grupsuz Kullanıcı: {summary['users_without_groups']}")
        self.stdout.write(f"📈 Kapsama Oranı: %{summary['coverage_percentage']}")
        self.stdout.write(f"🏷️  Toplam Grup: {summary['total_groups']}")
        
        if summary['group_stats']:
            self.stdout.write(
                self.style.WARNING('\n📋 Grup İstatistikleri:')
            )
            for group_stat in summary['group_stats']:
                self.stdout.write(f"  • {group_stat['name']}: {group_stat['user_count']} kullanıcı")

    def create_groups(self, dry_run=False):
        """Gerekli grupları oluşturur"""
        self.stdout.write(
            self.style.SUCCESS('\n🏗️  Grup Oluşturma İşlemi')
        )
        self.stdout.write('=' * 40)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n⚠️  DRY RUN - Değişiklik yapılmayacak\n')
            )
        
        if not dry_run:
            created_count = create_required_groups()
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {created_count} grup oluşturuldu/kontrol edildi')
            )
        else:
            # Dry run için sadece hangi grupların oluşturulacağını göster
            from common.auto_role_assignment import get_required_groups
            required_groups = get_required_groups()
            existing_groups = set(Group.objects.values_list('name', flat=True))
            new_groups = set(required_groups) - existing_groups
            
            self.stdout.write(f"📋 Kontrol edilecek gruplar: {len(required_groups)}")
            self.stdout.write(f"🆕 Oluşturulacak yeni gruplar: {len(new_groups)}")
            
            if new_groups:
                self.stdout.write("\nYeni gruplar:")
                for group in sorted(new_groups):
                    self.stdout.write(f"  + {group}")

    def assign_all_users(self, force=False, dry_run=False):
        """Tüm kullanıcılara rol atar"""
        users = User.objects.all()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎯 Toplu Rol Atama İşlemi')
        )
        self.stdout.write('=' * 40)
        self.stdout.write(f"📊 Toplam kullanıcı: {users.count()}")
        
        if force:
            self.stdout.write(
                self.style.WARNING('⚠️  FORCE modu - mevcut roller silinecek')
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  DRY RUN - değişiklik yapılmayacak\n')
            )
            return
        
        # Onay iste
        if not dry_run and users.count() > 10:
            confirm = input(f"\n{users.count()} kullanıcı için rol atama yapılacak. Devam edilsin mi? (y/N): ")
            if confirm.lower() not in ['y', 'yes', 'evet']:
                self.stdout.write(
                    self.style.ERROR('❌ İşlem iptal edildi')
                )
                return
        
        result = bulk_assign_roles(users=users, force=force)
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Toplu rol atama tamamlandı:')
        )
        self.stdout.write(f"  📈 Başarılı: {result['success']}")
        self.stdout.write(f"  ❌ Hatalı: {result['errors']}")
        self.stdout.write(f"  📊 Toplam: {result['total']}")

    def assign_single_user(self, username, force=False, dry_run=False):
        """Belirli bir kullanıcıya rol atar"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Kullanıcı bulunamadı: {username}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 Tek Kullanıcı Rol Atama: {username}')
        )
        self.stdout.write('=' * 50)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  DRY RUN - değişiklik yapılmayacak\n')
            )
            # Mevcut durumu göster
            self.stdout.write(f"Mevcut rol: {getattr(user, 'role', 'None')}")
            self.stdout.write(f"Mevcut gruplar: {list(user.groups.values_list('name', flat=True))}")
            user_type_obj = getattr(user, 'user_type', None)
            self.stdout.write(f"UserType: {user_type_obj.code if user_type_obj else 'None'}")
            self.stdout.write(f"is_staff: {user.is_staff}")
            self.stdout.write(f"is_superuser: {user.is_superuser}")
            return
        
        result = assign_roles_to_user(user, force=force)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('✅ Rol atama başarılı:')
            )
            self.stdout.write(f"  👤 Kullanıcı: {result['username']}")
            self.stdout.write(f"  🎭 Atanan rol: {result['assigned_role']}")
            self.stdout.write(f"  🏷️  Atanan gruplar: {', '.join(result['assigned_groups'])}")
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Rol atama hatası: {result["error"]}')
            )

    def assign_by_user_type(self, user_type_code, force=False, dry_run=False):
        """Belirli user_type'a sahip kullanıcılara rol atar"""
        users = User.objects.filter(user_type__code=user_type_code)
        
        if not users.exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️  {user_type_code} user_type\'ına sahip kullanıcı bulunamadı')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 UserType Bazlı Rol Atama: {user_type_code}')
        )
        self.stdout.write('=' * 50)
        self.stdout.write(f"📊 Etkilenecek kullanıcı sayısı: {users.count()}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  DRY RUN - değişiklik yapılmayacak\n')
            )
            for user in users[:10]:  # İlk 10'unu göster
                self.stdout.write(f"  👤 {user.username} ({user.email})")
            if users.count() > 10:
                self.stdout.write(f"  ... ve {users.count() - 10} kullanıcı daha")
            return
        
        result = bulk_assign_roles(users=users, force=force)
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ UserType bazlı rol atama tamamlandı:')
        )
        self.stdout.write(f"  📈 Başarılı: {result['success']}")
        self.stdout.write(f"  ❌ Hatalı: {result['errors']}")
        self.stdout.write(f"  📊 Toplam: {result['total']}")

    def print_help(self, prog_name, subcommand):
        """Kullanım örneklerini gösterir"""
        super().print_help(prog_name, subcommand)
        self.stdout.write(
            self.style.SUCCESS('\n🔧 Otomatik Rol Atama Yönetimi')
        )
        self.stdout.write('=' * 50)
        
        examples = [
            ('Kuralları listele', 'python manage.py auto_assign_roles --list-rules'),
            ('Durumu görüntüle', 'python manage.py auto_assign_roles --summary'),
            ('Grupları oluştur', 'python manage.py auto_assign_roles --create-groups'),
            ('Tüm kullanıcılara rol ata', 'python manage.py auto_assign_roles --assign'),
            ('Tüm rolleri sıfırla ve yeniden ata', 'python manage.py auto_assign_roles --assign --force'),
            ('Belirli kullanıcıya rol ata', 'python manage.py auto_assign_roles --user admin'),
            ('UserType bazlı rol ata', 'python manage.py auto_assign_roles --user-type kobi_owner'),
            ('Dry run (simülasyon)', 'python manage.py auto_assign_roles --assign --dry-run'),
        ]
        
        self.stdout.write('\n📋 Kullanım Örnekleri:')
        for desc, cmd in examples:
            self.stdout.write(f"\n  {desc}:")
            self.stdout.write(f"    {cmd}")