from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

class Command(BaseCommand):
    help = 'Gerekli grupları ve izinleri oluşturur'

    def handle(self, *args, **kwargs):
        # Grup ve izin tanımları
        groups = {
            'Finans Yöneticisi': ['add_invoice', 'change_invoice', 'delete_invoice', 'view_invoice'],
            'Destek': ['view_customuser'],
            'Rapor Görüntüleyici': ['view_invoice', 'view_report'],
        }
        # İzinlerin bağlı olduğu app_label'leri bul
        invoice_model = apps.get_model('accounting', 'Invoice')
        user_model = apps.get_model('accounts', 'CustomUser')
        for group_name, perms in groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for perm_codename in perms:
                # İzin hangi modele aitse ona göre app_label belirle
                if 'invoice' in perm_codename:
                    app_label = 'accounting'
                    model = 'invoice'
                elif 'customuser' in perm_codename:
                    app_label = 'accounts'
                    model = 'customuser'
                elif 'report' in perm_codename:
                    app_label = 'finance'
                    model = 'report'
                else:
                    continue
                try:
                    perm = Permission.objects.get(codename=perm_codename, content_type__app_label=app_label, content_type__model=model)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"İzin bulunamadı: {perm_codename} ({app_label}.{model})"))
        self.stdout.write(self.style.SUCCESS('Gruplar ve izinler oluşturuldu.')) 