"""
Yerel ortamdaki kullanıcı türleri ve kullanıcı bilgilerini JSON formatında export eder.
Canlı ortama aktarım için hazırlanmıştır.
"""
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserType, SubscriptionType
from accounting.models import Company

User = get_user_model()


class Command(BaseCommand):
    help = "Kullanıcı türleri ve kullanıcı bilgilerini JSON formatında export eder"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="users_export.json",
            help="Export dosyasının yolu (varsayılan: users_export.json)",
        )
        parser.add_argument(
            "--include-passwords",
            action="store_true",
            help="Kullanıcı şifrelerini de export et (hash'lenmiş şekilde)",
        )
        parser.add_argument(
            "--include-companies",
            action="store_true",
            help="Şirket bilgilerini de export et",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        include_passwords = options["include_passwords"]
        include_companies = options["include_companies"]

        self.stdout.write(self.style.SUCCESS("📦 Kullanıcı verileri export ediliyor..."))

        export_data = {
            "export_date": datetime.now().isoformat(),
            "version": "1.0",
            "user_types": [],
            "subscription_types": [],
            "users": [],
            "companies": [] if include_companies else None,
        }

        # 1. UserType'ları export et
        self.stdout.write("  → UserType'lar export ediliyor...")
        user_types = UserType.objects.select_related("default_subscription").all()
        for ut in user_types:
            export_data["user_types"].append(
                {
                    "code": ut.code,
                    "name": ut.name,
                    "default_subscription_code": ut.default_subscription.code
                    if ut.default_subscription
                    else None,
                }
            )
        self.stdout.write(
            self.style.SUCCESS(
                f'    ✓ {len(export_data["user_types"])} UserType export edildi'
            )
        )

        # 2. SubscriptionType'ları export et
        self.stdout.write("  → SubscriptionType'lar export ediliyor...")
        subscription_types = SubscriptionType.objects.all()
        for st in subscription_types:
            export_data["subscription_types"].append(
                {
                    "code": st.code,
                    "name": st.name,
                    "description": st.description,
                    "audience": st.audience,
                    "period_options": st.period_options,
                    "monthly_price": str(st.monthly_price)
                    if st.monthly_price
                    else None,
                    "yearly_price": str(st.yearly_price) if st.yearly_price else None,
                    "user_limit": st.user_limit,
                    "features": st.features,
                }
            )
        self.stdout.write(
            self.style.SUCCESS(
                f'    ✓ {len(export_data["subscription_types"])} SubscriptionType export edildi'
            )
        )

        # 3. Şirketleri export et (opsiyonel)
        if include_companies:
            self.stdout.write("  → Şirketler export ediliyor...")
            companies = Company.objects.all()
            for company in companies:
                export_data["companies"].append(
                    {
                        "id": company.id,
                        "name": company.name,
                        "tax_number": company.tax_number,
                        "tax_office": company.tax_office,
                        "address": company.address,
                        "phone": company.phone,
                        "email": company.email,
                    }
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f'    ✓ {len(export_data["companies"])} şirket export edildi'
                )
            )

        # 4. Kullanıcıları export et
        self.stdout.write("  → Kullanıcılar export ediliyor...")
        users = (
            User.objects.select_related("user_type", "company")
            .prefetch_related("groups")
            .all()
        )

        for user in users:
            user_data = {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "date_joined": user.date_joined.isoformat()
                if user.date_joined
                else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "role": user.role,
                "user_type_code": user.user_type.code if user.user_type else None,
                "company_id": user.company.id if user.company else None,
                "groups": [g.name for g in user.groups.all()],
            }

            # Şifre hash'ini export et (opsiyonel)
            if include_passwords:
                user_data["password"] = user.password  # Hash'lenmiş şifre

            export_data["users"].append(user_data)

        self.stdout.write(
            self.style.SUCCESS(
                f'    ✓ {len(export_data["users"])} kullanıcı export edildi'
            )
        )

        # JSON dosyasına yaz
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"\n✅ Export tamamlandı: {output_file}"))
        self.stdout.write("   📊 Özet:")
        self.stdout.write(f'      - UserType: {len(export_data["user_types"])}')
        self.stdout.write(
            f'      - SubscriptionType: {len(export_data["subscription_types"])}'
        )
        self.stdout.write(f'      - Kullanıcı: {len(export_data["users"])}')
        if include_companies:
            self.stdout.write(f'      - Şirket: {len(export_data["companies"])}')
