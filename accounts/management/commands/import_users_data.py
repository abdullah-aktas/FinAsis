"""
Export edilmiş kullanıcı verilerini canlı ortama import eder.
Çakışmaları handle eder ve mevcut verileri günceller.
"""
import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import UserType, SubscriptionType
from accounting.models import Company

User = get_user_model()


class Command(BaseCommand):
    help = "Export edilmiş kullanıcı verilerini canlı ortama import eder"

    def add_arguments(self, parser):
        parser.add_argument(
            "input_file", type=str, help="Import edilecek JSON dosyasının yolu"
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Mevcut kullanıcıları güncelle (varsayılan: sadece yeni kullanıcılar eklenir)",
        )
        parser.add_argument(
            "--skip-passwords",
            action="store_true",
            help="Şifreleri import etme (kullanıcılar şifre sıfırlama yapmalı)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Sadece ne yapılacağını göster, gerçek import yapma",
        )

    def handle(self, *args, **options):
        input_file = options["input_file"]
        update_existing = options["update_existing"]
        skip_passwords = options["skip_passwords"]
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN modu - değişiklik yapılmayacak\n")
            )

        # JSON dosyasını oku
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                export_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ Dosya bulunamadı: {input_file}"))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"❌ JSON parse hatası: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("📥 Kullanıcı verileri import ediliyor..."))
        self.stdout.write(
            f'   Export tarihi: {export_data.get("export_date", "Bilinmiyor")}\n'
        )

        stats = {
            "user_types_created": 0,
            "user_types_updated": 0,
            "subscription_types_created": 0,
            "subscription_types_updated": 0,
            "users_created": 0,
            "users_updated": 0,
            "users_skipped": 0,
            "companies_created": 0,
            "companies_updated": 0,
            "errors": [],
        }

        with transaction.atomic():
            # 1. SubscriptionType'ları import et (önce bunlar, çünkü UserType bunlara bağlı)
            if "subscription_types" in export_data:
                self.stdout.write("  → SubscriptionType'lar import ediliyor...")
                for st_data in export_data["subscription_types"]:
                    try:
                        st, created = SubscriptionType.objects.update_or_create(
                            code=st_data["code"],
                            defaults={
                                "name": st_data["name"],
                                "description": st_data.get("description", ""),
                                "audience": st_data.get("audience", "sme"),
                                "period_options": st_data.get(
                                    "period_options", "monthly"
                                ),
                                "monthly_price": st_data.get("monthly_price"),
                                "yearly_price": st_data.get("yearly_price"),
                                "user_limit": st_data.get("user_limit"),
                                "features": st_data.get("features", []),
                            },
                        )
                        if created:
                            stats["subscription_types_created"] += 1
                            if not dry_run:
                                self.stdout.write(
                                    f"    ✓ Oluşturuldu: {st.name} ({st.code})"
                                )
                        else:
                            stats["subscription_types_updated"] += 1
                            if not dry_run:
                                self.stdout.write(
                                    f"    ↻ Güncellendi: {st.name} ({st.code})"
                                )
                    except Exception as e:
                        error_msg = f"SubscriptionType {st_data.get('code')}: {str(e)}"
                        stats["errors"].append(error_msg)
                        self.stdout.write(self.style.ERROR(f"    ✗ Hata: {error_msg}"))

            # 2. UserType'ları import et
            if "user_types" in export_data:
                self.stdout.write("  → UserType'lar import ediliyor...")
                for ut_data in export_data["user_types"]:
                    try:
                        default_subscription = None
                        if ut_data.get("default_subscription_code"):
                            try:
                                default_subscription = SubscriptionType.objects.get(
                                    code=ut_data["default_subscription_code"]
                                )
                            except SubscriptionType.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'    ⚠ SubscriptionType bulunamadı: {ut_data["default_subscription_code"]}'
                                    )
                                )

                        ut, created = UserType.objects.update_or_create(
                            code=ut_data["code"],
                            defaults={
                                "name": ut_data["name"],
                                "default_subscription": default_subscription,
                            },
                        )
                        if created:
                            stats["user_types_created"] += 1
                            if not dry_run:
                                self.stdout.write(
                                    f"    ✓ Oluşturuldu: {ut.name} ({ut.code})"
                                )
                        else:
                            stats["user_types_updated"] += 1
                            if not dry_run:
                                self.stdout.write(
                                    f"    ↻ Güncellendi: {ut.name} ({ut.code})"
                                )
                    except Exception as e:
                        error_msg = f"UserType {ut_data.get('code')}: {str(e)}"
                        stats["errors"].append(error_msg)
                        self.stdout.write(self.style.ERROR(f"    ✗ Hata: {error_msg}"))

            # 3. Şirketleri import et (opsiyonel)
            if "companies" in export_data and export_data["companies"]:
                self.stdout.write("  → Şirketler import ediliyor...")
                for company_data in export_data["companies"]:
                    try:
                        company, created = Company.objects.update_or_create(
                            id=company_data.get("id"),
                            defaults={
                                "name": company_data["name"],
                                "tax_number": company_data.get("tax_number"),
                                "tax_office": company_data.get("tax_office"),
                                "address": company_data.get("address"),
                                "phone": company_data.get("phone"),
                                "email": company_data.get("email"),
                            },
                        )
                        if created:
                            stats["companies_created"] += 1
                        else:
                            stats["companies_updated"] += 1
                    except Exception as e:
                        error_msg = f"Company {company_data.get('name')}: {str(e)}"
                        stats["errors"].append(error_msg)
                        self.stdout.write(self.style.ERROR(f"    ✗ Hata: {error_msg}"))

            # 4. Kullanıcıları import et
            if "users" in export_data:
                self.stdout.write("  → Kullanıcılar import ediliyor...")
                for user_data in export_data["users"]:
                    try:
                        username = user_data["username"]
                        existing_user = User.objects.filter(username=username).first()

                        if existing_user and not update_existing:
                            stats["users_skipped"] += 1
                            if not dry_run:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"    ⊘ Atlanıldı (zaten var): {username}"
                                    )
                                )
                            continue

                        # UserType'ı al
                        user_type = None
                        if user_data.get("user_type_code"):
                            try:
                                user_type = UserType.objects.get(
                                    code=user_data["user_type_code"]
                                )
                            except UserType.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'    ⚠ UserType bulunamadı: {user_data["user_type_code"]}'
                                    )
                                )

                        # Company'yi al
                        company = None
                        if user_data.get("company_id"):
                            try:
                                company = Company.objects.get(
                                    id=user_data["company_id"]
                                )
                            except Company.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'    ⚠ Şirket bulunamadı: {user_data["company_id"]}'
                                    )
                                )

                        # Kullanıcıyı oluştur veya güncelle
                        user_defaults = {
                            "email": user_data.get("email", ""),
                            "first_name": user_data.get("first_name", ""),
                            "last_name": user_data.get("last_name", ""),
                            "is_active": user_data.get("is_active", True),
                            "is_staff": user_data.get("is_staff", False),
                            "is_superuser": user_data.get("is_superuser", False),
                            "role": user_data.get("role", "staff"),
                            "user_type": user_type,
                            "company": company,
                        }

                        if not skip_passwords and user_data.get("password"):
                            user_defaults["password"] = user_data["password"]

                        if existing_user:
                            # Mevcut kullanıcıyı güncelle
                            if not skip_passwords and user_data.get("password"):
                                existing_user.set_password(user_data["password"])
                            for key, value in user_defaults.items():
                                if key != "password":
                                    setattr(existing_user, key, value)
                            if not dry_run:
                                existing_user.save()
                            stats["users_updated"] += 1
                            if not dry_run:
                                self.stdout.write(f"    ↻ Güncellendi: {username}")
                            user = existing_user
                        else:
                            # Yeni kullanıcı oluştur
                            if skip_passwords or not user_data.get("password"):
                                # Şifre yoksa geçici bir şifre oluştur
                                if not dry_run:
                                    user = User.objects.create_user(
                                        username=username,
                                        password="TempPassword123!",  # Kullanıcı şifre sıfırlamalı
                                        **{
                                            k: v
                                            for k, v in user_defaults.items()
                                            if k != "password"
                                        },
                                    )
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f"    ⚠ Geçici şifre atandı: {username} (şifre sıfırlama gerekli)"
                                        )
                                    )
                                else:
                                    user = None
                            else:
                                if not dry_run:
                                    user = User.objects.create_user(
                                        username=username,
                                        password=user_data["password"],
                                        **{
                                            k: v
                                            for k, v in user_defaults.items()
                                            if k != "password"
                                        },
                                    )
                                else:
                                    user = None
                            stats["users_created"] += 1
                            if not dry_run and user:
                                self.stdout.write(f"    ✓ Oluşturuldu: {username}")

                        # Grupları ata
                        if user and user_data.get("groups") and not dry_run:
                            user.groups.clear()
                            for group_name in user_data["groups"]:
                                try:
                                    from django.contrib.auth.models import Group

                                    group = Group.objects.get(name=group_name)
                                    user.groups.add(group)
                                except Group.DoesNotExist:
                                    pass

                    except Exception as e:
                        error_msg = f"User {user_data.get('username')}: {str(e)}"
                        stats["errors"].append(error_msg)
                        self.stdout.write(self.style.ERROR(f"    ✗ Hata: {error_msg}"))

            if dry_run:
                self.stdout.write(
                    self.style.WARNING("\n⚠️  DRY RUN - değişiklikler yapılmadı")
                )
                transaction.set_rollback(True)

        # Özet
        self.stdout.write(self.style.SUCCESS("\n✅ Import tamamlandı!"))
        self.stdout.write("   📊 Özet:")
        self.stdout.write(
            f'      - UserType: +{stats["user_types_created"]} / ↻{stats["user_types_updated"]}'
        )
        self.stdout.write(
            f'      - SubscriptionType: +{stats["subscription_types_created"]} / ↻{stats["subscription_types_updated"]}'
        )
        self.stdout.write(
            f'      - Kullanıcı: +{stats["users_created"]} / ↻{stats["users_updated"]} / ⊘{stats["users_skipped"]}'
        )
        if stats.get("companies_created") or stats.get("companies_updated"):
            self.stdout.write(
                f'      - Şirket: +{stats["companies_created"]} / ↻{stats["companies_updated"]}'
            )
        if stats["errors"]:
            self.stdout.write(
                self.style.ERROR(f'\n   ❌ Hatalar: {len(stats["errors"])}')
            )
            for error in stats["errors"][:10]:  # İlk 10 hatayı göster
                self.stdout.write(self.style.ERROR(f"      - {error}"))
