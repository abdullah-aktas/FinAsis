# accounts/management/commands/create_default_roles_and_plans.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.role_models import UserRole, SubscriptionPlan
from accounts.services.role_profiles import backfill_role_profiles

User = get_user_model()


class Command(BaseCommand):
    help = "FinAsis için varsayılan rolleri ve planları oluşturur"

    def handle(self, *args, **options):
        self.create_user_roles()
        self.create_subscription_plans()
        self.ensure_role_profiles()
        self.stdout.write(
            self.style.SUCCESS("Roller ve planlar başarıyla oluşturuldu!")
        )

    def create_user_roles(self):
        """Kullanıcı rollerini oluştur"""
        roles_data = [
            {
                "name": "super_admin",
                "display_name": "Süper Yönetici",
                "description": "Sistem genelinde tam yetki",
                "hierarchy_level": 0,
                "can_manage_users": True,
                "can_manage_companies": True,
                "can_view_all_finances": True,
                "can_edit_finances": True,
                "can_approve_transactions": True,
                "can_generate_reports": True,
                "can_access_ai": True,
                "can_use_education": True,
                "can_play_games": True,
                "can_use_blockchain": True,
                "max_companies": -1,
                "max_transactions_per_month": -1,
            },
            {
                "name": "admin",
                "display_name": "Sistem Yöneticisi",
                "description": "Şirket düzeyinde yönetici yetkisi",
                "hierarchy_level": 1,
                "can_manage_users": True,
                "can_manage_companies": True,
                "can_view_all_finances": True,
                "can_edit_finances": True,
                "can_approve_transactions": True,
                "can_generate_reports": True,
                "can_access_ai": True,
                "can_use_education": True,
                "can_play_games": True,
                "can_use_blockchain": True,
                "max_companies": 10,
                "max_transactions_per_month": -1,
            },
            {
                "name": "finance_manager",
                "display_name": "Finans Müdürü",
                "description": "Finans operasyonlarını yönetme ve onaylama yetkisi",
                "hierarchy_level": 2,
                "can_manage_users": False,
                "can_manage_companies": True,
                "can_view_all_finances": True,
                "can_edit_finances": True,
                "can_approve_transactions": True,
                "can_generate_reports": True,
                "can_access_ai": True,
                "can_use_education": False,
                "can_play_games": False,
                "can_use_blockchain": True,
                "max_companies": 10,
                "max_transactions_per_month": -1,
            },
            {
                "name": "kobi_owner",
                "display_name": "KOBİ Sahibi",
                "description": "Kendi işletmesini uçtan uca yönetme yetkisi",
                "hierarchy_level": 3,
                "can_manage_users": True,
                "can_manage_companies": True,
                "can_view_all_finances": True,
                "can_edit_finances": True,
                "can_approve_transactions": True,
                "can_generate_reports": True,
                "can_access_ai": True,
                "can_use_education": True,
                "can_play_games": True,
                "can_use_blockchain": False,
                "max_companies": 3,
                "max_transactions_per_month": 500,
            },
            {
                "name": "financial_advisor",
                "display_name": "Mali Müşavir",
                "description": "Müşteri şirketlerini yönetme ve finansal danışmanlık",
                "hierarchy_level": 4,
                "can_manage_users": False,
                "can_manage_companies": True,
                "can_view_all_finances": True,
                "can_edit_finances": True,
                "can_approve_transactions": True,
                "can_generate_reports": True,
                "can_access_ai": True,
                "can_use_education": True,
                "can_play_games": False,
                "can_use_blockchain": True,
                "max_companies": 50,
                "max_transactions_per_month": -1,
            },
            {
                "name": "accountant",
                "display_name": "Muhasebeci",
                "description": "Muhasebe işlemlerini yürütme yetkisi",
                "hierarchy_level": 5,
                "can_manage_users": False,
                "can_manage_companies": False,
                "can_view_all_finances": True,
                "can_edit_finances": True,
                "can_approve_transactions": False,
                "can_generate_reports": True,
                "can_access_ai": True,
                "can_use_education": True,
                "can_play_games": False,
                "can_use_blockchain": False,
                "max_companies": 5,
                "max_transactions_per_month": 1000,
            },
            {
                "name": "auditor",
                "display_name": "Denetçi",
                "description": "Denetim ve kontrol yetkisi (sadece görüntüleme)",
                "hierarchy_level": 6,
                "can_manage_users": False,
                "can_manage_companies": False,
                "can_view_all_finances": True,
                "can_edit_finances": False,
                "can_approve_transactions": False,
                "can_generate_reports": True,
                "can_access_ai": True,
                "can_use_education": False,
                "can_play_games": False,
                "can_use_blockchain": True,
                "max_companies": 10,
                "max_transactions_per_month": 0,  # Sadece görüntüleme
            },
            {
                "name": "kobi_employee",
                "display_name": "KOBİ Çalışanı",
                "description": "Sınırlı işlem yetkisi",
                "hierarchy_level": 7,
                "can_manage_users": False,
                "can_manage_companies": False,
                "can_view_all_finances": False,
                "can_edit_finances": True,
                "can_approve_transactions": False,
                "can_generate_reports": False,
                "can_access_ai": True,
                "can_use_education": True,
                "can_play_games": True,
                "can_use_blockchain": False,
                "max_companies": 1,
                "max_transactions_per_month": 100,
            },
            {
                "name": "teacher",
                "display_name": "Eğitimci",
                "description": "Eğitim içeriklerini yönetme ve değerlendirme yetkisi",
                "hierarchy_level": 7,
                "can_manage_users": False,
                "can_manage_companies": False,
                "can_view_all_finances": False,
                "can_edit_finances": False,
                "can_approve_transactions": False,
                "can_generate_reports": False,
                "can_access_ai": True,
                "can_use_education": True,
                "can_play_games": True,
                "can_use_blockchain": False,
                "max_companies": 0,
                "max_transactions_per_month": 0,
            },
            {
                "name": "student",
                "display_name": "Öğrenci",
                "description": "Eğitim amaçlı sınırlı erişim",
                "hierarchy_level": 8,
                "can_manage_users": False,
                "can_manage_companies": False,
                "can_view_all_finances": False,
                "can_edit_finances": False,
                "can_approve_transactions": False,
                "can_generate_reports": False,
                "can_access_ai": False,
                "can_use_education": True,
                "can_play_games": True,
                "can_use_blockchain": False,
                "max_companies": 0,
                "max_transactions_per_month": 0,
            },
            {
                "name": "player",
                "display_name": "Oyuncu",
                "description": "Gamification senaryolarına erişim",
                "hierarchy_level": 8,
                "can_manage_users": False,
                "can_manage_companies": False,
                "can_view_all_finances": False,
                "can_edit_finances": False,
                "can_approve_transactions": False,
                "can_generate_reports": False,
                "can_access_ai": False,
                "can_use_education": False,
                "can_play_games": True,
                "can_use_blockchain": False,
                "max_companies": 0,
                "max_transactions_per_month": 0,
            },
            {
                "name": "viewer",
                "display_name": "Görüntüleyici",
                "description": "Sadece görüntüleme yetkisi",
                "hierarchy_level": 9,
                "can_manage_users": False,
                "can_manage_companies": False,
                "can_view_all_finances": False,
                "can_edit_finances": False,
                "can_approve_transactions": False,
                "can_generate_reports": False,
                "can_access_ai": False,
                "can_use_education": True,
                "can_play_games": True,
                "can_use_blockchain": False,
                "max_companies": 0,
                "max_transactions_per_month": 0,
            },
        ]

        for role_data in roles_data:
            role, created = UserRole.objects.get_or_create(
                name=role_data["name"], defaults=role_data
            )
            if created:
                self.stdout.write(f"✓ {role.display_name} rolü oluşturuldu")
            else:
                self.stdout.write(f"→ {role.display_name} rolü zaten mevcut")

    def create_subscription_plans(self):
        """Abonelik planlarını oluştur"""
        plans_data = [
            {
                "name": "free",
                "display_name": "Ücretsiz Plan",
                "description": "Temel özelliklerle başlayın. Küçük işletmeler ve bireysel kullanıcılar için ideal.",
                "price_monthly": 0.00,
                "price_yearly": 0.00,
                "max_users": 1,
                "max_companies": 1,
                "max_transactions": 50,
                "storage_gb": 1,
                "has_accounting": True,
                "has_finance": False,
                "has_ai_assistant": False,
                "has_education": True,
                "has_games": True,
                "has_blockchain": False,
                "has_api_access": False,
                "has_priority_support": False,
                "is_active": True,
                "order": 1,
            },
            {
                "name": "basic",
                "display_name": "Temel Plan",
                "description": "Küçük işletmeler için gelişmiş özellikler. AI asistan ve genişletilmiş limitler.",
                "price_monthly": 99.00,
                "price_yearly": 990.00,  # %17 indirim
                "max_users": 3,
                "max_companies": 2,
                "max_transactions": 250,
                "storage_gb": 5,
                "has_accounting": True,
                "has_finance": True,
                "has_ai_assistant": True,
                "has_education": True,
                "has_games": True,
                "has_blockchain": False,
                "has_api_access": False,
                "has_priority_support": False,
                "is_active": True,
                "is_popular": True,
                "order": 2,
            },
            {
                "name": "professional",
                "display_name": "Profesyonel Plan",
                "description": "Orta ölçekli işletmeler ve mali müşavirler için. Tam özellik seti ve API erişimi.",
                "price_monthly": 299.00,
                "price_yearly": 2990.00,  # %17 indirim
                "max_users": 10,
                "max_companies": 10,
                "max_transactions": 1000,
                "storage_gb": 20,
                "has_accounting": True,
                "has_finance": True,
                "has_ai_assistant": True,
                "has_education": True,
                "has_games": True,
                "has_blockchain": True,
                "has_api_access": True,
                "has_priority_support": True,
                "is_active": True,
                "order": 3,
            },
            {
                "name": "enterprise",
                "display_name": "Kurumsal Plan",
                "description": "Büyük işletmeler ve muhasebe ofisleri için. Sınırsız erişim ve öncelikli destek.",
                "price_monthly": 799.00,
                "price_yearly": 7990.00,  # %17 indirim
                "max_users": -1,  # Sınırsız
                "max_companies": -1,  # Sınırsız
                "max_transactions": -1,  # Sınırsız
                "storage_gb": 100,
                "has_accounting": True,
                "has_finance": True,
                "has_ai_assistant": True,
                "has_education": True,
                "has_games": True,
                "has_blockchain": True,
                "has_api_access": True,
                "has_priority_support": True,
                "is_active": True,
                "order": 4,
            },
            {
                "name": "custom",
                "display_name": "Özel Plan",
                "description": "Özel ihtiyaçlarınız için kişiselleştirilmiş çözümler. Fiyatlandırma için iletişime geçin.",
                "price_monthly": 0.00,  # Özel fiyatlandırma
                "price_yearly": 0.00,
                "max_users": -1,
                "max_companies": -1,
                "max_transactions": -1,
                "storage_gb": 500,
                "has_accounting": True,
                "has_finance": True,
                "has_ai_assistant": True,
                "has_education": True,
                "has_games": True,
                "has_blockchain": True,
                "has_api_access": True,
                "has_priority_support": True,
                "is_active": True,
                "order": 5,
            },
        ]

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data["name"], defaults=plan_data
            )
            if created:
                self.stdout.write(f"✓ {plan.display_name} oluşturuldu")
            else:
                self.stdout.write(f"→ {plan.display_name} zaten mevcut")

    def ensure_role_profiles(self):
        """Mevcut kullanıcıların rol profillerini oluştur/güncelle."""
        summary = backfill_role_profiles()
        self.stdout.write(
            self.style.SUCCESS(
                f"Rol profilleri güncellendi. Yeni: {summary['created']}, Güncellenen: {summary['updated']}, Hata: {summary['errors']}"
            )
        )
