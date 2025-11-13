from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

ROLE_DEFINITIONS = {
    "Admin": {
        "description": "Tam yetki (şirket bazlı)",
        "permissions": ["add_", "change_", "delete_", "view_"]
    },
    "Accountant": {
        "description": "Muhasebe fişleri oluşturma, stok, rapor görüntüleme",
        "permissions": ["add_", "change_", "view_"]
    },
    "Auditor": {
        "description": "Sadece görüntüleme, rapor alma",
        "permissions": ["view_"]
    },
    "InventoryManager": {
        "description": "Stok hareketleri ve envanter yönetimi",
        "permissions": ["add_", "change_", "view_"]
    },
}

# Hangi app label ve model adları üzerinde roller çalışacak (çekirdek finans + stok)
TARGET_MODELS = [
    ("finance", "journalvoucher"),
    ("finance", "journalentry"),
    ("finance", "inventoryitem"),
    ("finance", "stockmovement"),
    ("finance", "chartofaccounts"),
    ("finance", "fiscalperiod"),
]

class Command(BaseCommand):
    help = "FinAsis rol gruplarını ve ilgili izinleri oluşturur/günceller"

    def handle(self, *args, **options):
        with transaction.atomic():
            for role_name, meta in ROLE_DEFINITIONS.items():
                group, _ = Group.objects.get_or_create(name=role_name)
                perms_to_set = []
                for app_label, model in TARGET_MODELS:
                    try:
                        ct = ContentType.objects.get(app_label=app_label, model=model)
                    except ContentType.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"ContentType bulunamadı: {app_label}.{model}"))
                        continue
                    for perm_prefix in meta["permissions"]:
                        qs = Permission.objects.filter(codename__startswith=perm_prefix, content_type=ct)
                        perms_to_set.extend(list(qs))
                group.permissions.set(perms_to_set)
                group.save()
                self.stdout.write(self.style.SUCCESS(f"Rol güncellendi: {role_name} (izin sayısı: {len(perms_to_set)})"))
        self.stdout.write(self.style.SUCCESS("Rol seed tamamlandı."))
