"""
FinAsis test ortamı bootstrap komutu.

Sağladıkları:
- Temel kullanıcı tiplerini ve grupları hazırlar
- Demo şirketler ve örnek finans verileri oluşturur
- Çok rollü test kullanıcıları üretir ve parolaları sabitler
- Yardım merkezi, dokümantasyon ve AI asistanı için feature flag'leri aktifleştirir
- AI modelleri ve bilgi indeksleri için sağlıklı varsayılanlar hazırlar
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.utils import timezone

from accounting.models import Company, Customer, Invoice, Expense
from accounts.models import UserType, UserSettings
from ai_assistant.models import (
    AIModel,
    AIInsight,
    Notification,
    Recommendation,
    UserInteraction,
    UserPreference,
)
from ai_assistant.services.ml_service import RiskScoringService
from common.auto_role_assignment import assign_roles_to_user
from management.models import FeatureFlag


User = get_user_model()


class Command(BaseCommand):
    help = "Test kullanıcıları, örnek veriler, feature flag'ler ve AI varlıklarını oluşturur."

    DEFAULT_PASSWORD = "FinAsis!2025"

    USER_TYPES = [
        ("kobi_owner", "KOBİ Sahibi"),
        ("kobi_employee", "KOBİ Çalışanı"),
        ("finance_manager", "Finans Yöneticisi"),
        ("accountant", "Muhasebeci"),
        ("financial_advisor", "Finansal Danışman"),
        ("auditor", "Denetçi"),
        ("teacher", "Eğitimci"),
        ("student", "Öğrenci"),
        ("ai_specialist", "AI Analist"),
    ]

    COMPANIES = [
        {
            "name": "FinAsis Demo Holding",
            "trade_name": "FinAsis Holding A.Ş.",
            "tax_number": "1000000001",
            "sector": "Holding",
            "address": "İstanbul Finans Merkezi",
            "phone": "+90 850 000 00 01",
            "email": "demo@finasis.com",
        },
        {
            "name": "Anadolu Üretim Sanayi",
            "trade_name": "Anadolu Üretim Sanayi Tic. Ltd. Şti.",
            "tax_number": "1000000002",
            "sector": "Üretim",
            "address": "Organize Sanayi Bölgesi, Bursa",
            "phone": "+90 224 000 00 00",
            "email": "info@anadoluuretimsanayi.com",
        },
        {
            "name": "EduFin Akademi",
            "trade_name": "EduFin Eğitim ve Danışmanlık A.Ş.",
            "tax_number": "1000000003",
            "sector": "Eğitim",
            "address": "Teknopark İstanbul, İstanbul",
            "phone": "+90 212 000 00 00",
            "email": "bilgi@edufin.com",
        },
    ]

    TEST_USERS = [
        {
            "username": "demo_superadmin",
            "email": "superadmin@finasis.com",
            "first_name": "Demo",
            "last_name": "SuperAdmin",
            "is_staff": True,
            "is_superuser": True,
            "role": "admin",
            "user_type_code": None,
            "company_key": 0,
        },
        {
            "username": "demo_owner",
            "email": "owner@finasis.com",
            "first_name": "Demo",
            "last_name": "Owner",
            "user_type_code": "kobi_owner",
            "company_key": 0,
        },
        {
            "username": "demo_finance_manager",
            "email": "finance.manager@finasis.com",
            "first_name": "Finance",
            "last_name": "Manager",
            "user_type_code": "finance_manager",
            "company_key": 1,
        },
        {
            "username": "demo_accountant",
            "email": "accountant@finasis.com",
            "first_name": "Demo",
            "last_name": "Accountant",
            "user_type_code": "accountant",
            "company_key": 1,
        },
        {
            "username": "demo_advisor",
            "email": "advisor@finasis.com",
            "first_name": "Demo",
            "last_name": "Advisor",
            "user_type_code": "financial_advisor",
            "company_key": 0,
        },
        {
            "username": "demo_auditor",
            "email": "auditor@finasis.com",
            "first_name": "Demo",
            "last_name": "Auditor",
            "user_type_code": "auditor",
            "company_key": 0,
        },
        {
            "username": "demo_teacher",
            "email": "teacher@edufin.com",
            "first_name": "Demo",
            "last_name": "Teacher",
            "user_type_code": "teacher",
            "company_key": 2,
        },
        {
            "username": "demo_student",
            "email": "student@edufin.com",
            "first_name": "Demo",
            "last_name": "Student",
            "user_type_code": "student",
            "company_key": 2,
        },
        {
            "username": "demo_employee",
            "email": "employee@anadoluuretimsanayi.com",
            "first_name": "Demo",
            "last_name": "Employee",
            "user_type_code": "kobi_employee",
            "company_key": 1,
        },
        {
            "username": "demo_ai_specialist",
            "email": "ai.specialist@finasis.com",
            "first_name": "AI",
            "last_name": "Specialist",
            "user_type_code": "ai_specialist",
            "company_key": 0,
        },
    ]

    FEATURE_FLAGS = [
        {
            "name": "Yardım Merkezi",
            "key": "help_center",
            "description": "Yardım merkezi ve rehber içeriklerinin tamamını aktif eder.",
            "module": "common",
        },
        {
            "name": "Kılavuzlu Turlar",
            "key": "guided_tours",
            "description": "Arayüz içi adım adım rehberleri gösterir.",
            "module": "common",
        },
        {
            "name": "Dokümantasyon Portalı",
            "key": "documentation_portal",
            "description": "Platform içinden erişilen dökümantasyon bağlantılarını aktif eder.",
            "module": "docs",
        },
        {
            "name": "AI Asistan Tam Paket",
            "key": "ai_assistant_full_suite",
            "description": "AI Asistan, risk analizi, OCR ve raporlama önerilerini açar.",
            "module": "ai_assistant",
        },
    ]

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write(self.style.WARNING("> Test ortami kurulumu basliyor..."))
            self._run_prerequisite_commands()
            user_types = self._ensure_user_types()
            companies = self._ensure_companies()
            users = self._ensure_users(user_types, companies)
            self._seed_accounting_data(companies, users)
            self._ensure_feature_flags(users)
            self._ensure_ai_assets(users)
            self.stdout.write(self.style.SUCCESS("OK Test ortami hazir!"))
            self._print_summary(users)

    # ------------------------------------------------------------------ helpers

    def _run_prerequisite_commands(self):
        """
        Mevcut yönetim komutlarını çağırarak temel yapı taşlarını hazırla.
        """
        try:
            call_command("setup_user_types")
        except Exception:
            # command may not exist or already satisfied; ignore
            pass

        for cmd in ["create_default_roles_and_plans", "create_groups", "seed_roles"]:
            try:
                call_command(cmd, verbosity=0)
            except Exception:
                continue

    def _ensure_user_types(self) -> dict[str, UserType]:
        mapping: dict[str, UserType] = {}
        for code, name in self.USER_TYPES:
            user_type, _ = UserType.objects.update_or_create(
                code=code,
                defaults={"name": name},
            )
            mapping[code] = user_type
        return mapping

    def _ensure_companies(self) -> list[Company]:
        companies: list[Company] = []
        for company_data in self.COMPANIES:
            company, _ = Company.objects.update_or_create(
                tax_number=company_data["tax_number"],
                defaults=company_data,
            )
            companies.append(company)
        return companies

    def _ensure_users(
        self,
        user_types: dict[str, UserType],
        companies: list[Company],
    ) -> dict[str, User]:
        created_users: dict[str, User] = {}
        for user_info in self.TEST_USERS:
            attrs = {
                "email": user_info["email"],
                "first_name": user_info.get("first_name", ""),
                "last_name": user_info.get("last_name", ""),
                "is_active": True,
            }
            if user_info.get("is_staff"):
                attrs["is_staff"] = True
            if user_info.get("is_superuser"):
                attrs["is_superuser"] = True
            if user_info.get("role"):
                attrs["role"] = user_info["role"]

            company = companies[user_info["company_key"]] if user_info.get("company_key") is not None else None

            user, created = User.objects.update_or_create(
                username=user_info["username"],
                defaults={**attrs, "company": company},
            )

            if created or not user.check_password(self.DEFAULT_PASSWORD):
                user.set_password(self.DEFAULT_PASSWORD)
                user.save()

            # user_type bağla
            user_type_code = user_info.get("user_type_code")
            if user_type_code:
                user.user_type = user_types.get(user_type_code)
                user.save(update_fields=["user_type"])

            # kullanıcı ayarları
            UserSettings.objects.get_or_create(
                user=user,
                defaults={
                    "email_notifications": True,
                    "dark_mode": False,
                },
            )

            # roller
            assign_roles_to_user(user, force=True)

            created_users[user.username] = user
            status = "olusturuldu" if created else "guncellendi"
            self.stdout.write(
                self.style.SUCCESS(f"  - Kullanici {user.username} ({status})")
            )
        return created_users

    def _seed_accounting_data(
        self,
        companies: list[Company],
        users: dict[str, User],
    ):
        """
        Muhasebe modülü için temel müşteri, fatura ve gider verilerini ekler.
        """
        today = date.today()
        currencies = ["TRY", "USD", "EUR"]

        for company in companies:
            finance_owner = users.get("demo_finance_manager") or users.get("demo_accountant")

            customers_data = [
                {
                    "first_name": "ABC",
                    "last_name": "Tekstil",
                    "email": "satinalma@abctekstil.com",
                    "phone": "+90 212 123 45 67",
                },
                {
                    "first_name": "Delta",
                    "last_name": "Bilişim",
                    "email": "finans@deltabilisim.com",
                    "phone": "+90 216 987 65 43",
                },
                {
                    "first_name": "Eko",
                    "last_name": "Market",
                    "email": "muhasebe@ekomarket.com",
                    "phone": "+90 312 555 55 55",
                },
            ]

            customers: list[Customer] = []
            for data in customers_data:
                customer, _ = Customer.objects.update_or_create(
                    company=company,
                    email=data["email"],
                    defaults={
                        **data,
                        "company": company,
                    },
                )
                customers.append(customer)

            # örnek faturalar
            for index, customer in enumerate(customers, start=1):
                invoice_number = f"{company.tax_number}-{today.year}-{index:03d}"
                issue_date = today - timedelta(days=30 * index)
                due_date = issue_date + timedelta(days=15)
                total_amount = random.randint(10_000, 45_000)
                currency = random.choice(currencies)

                invoice_defaults = {
                    "company": company,
                    "customer": customer,
                    "issue_date": issue_date,
                    "due_date": due_date,
                    "total_amount": total_amount,
                    "currency": currency,
                    "description": f"{customer.first_name} {customer.last_name} için demo fatura",
                    "created_by": finance_owner,
                }

                Invoice.objects.update_or_create(
                    company=company,
                    invoice_number=invoice_number,
                    defaults=invoice_defaults,
                )

            # örnek giderler
            expense_categories = ["KIRA", "MAAS", "OFIS", "YOL"]
            for idx in range(1, 5):
                expense_date = today - timedelta(days=7 * idx)
                Expense.objects.update_or_create(
                    company=company,
                    description=f"{company.trade_name} için demo gider {idx}",
                    defaults={
                        "category": random.choice(expense_categories),
                        "amount": random.randint(5_000, 20_000),
                        "expense_date": expense_date,
                        "paid": idx % 2 == 0,
                        "created_by": finance_owner,
                    },
                )

    def _ensure_feature_flags(self, users: dict[str, User]):
        creator = users.get("demo_superadmin") or User.objects.filter(is_superuser=True).first()
        if not creator:
            raise RuntimeError("Feature flag oluşturmak için en az bir süper kullanıcı gerekli.")

        for payload in self.FEATURE_FLAGS:
            flag, _ = FeatureFlag.objects.update_or_create(
                key=payload["key"],
                defaults={
                    "name": payload["name"],
                    "description": payload["description"],
                    "module": payload["module"],
                    "is_enabled": True,
                    "enabled_for_all": True,
                    "created_by": creator,
                },
            )
            # rollout yüzde 100
            if flag.rollout_percentage != 100:
                flag.rollout_percentage = 100
                flag.save(update_fields=["rollout_percentage"])
            self.stdout.write(self.style.SUCCESS(f"  - Feature flag aktif: {flag.key}"))

    def _ensure_ai_assets(self, users: dict[str, User]):
        """
        AI servislerinin sağlıklı çalışması için gerekli model ve bilgi tabanı dosyalarını hazırlayın.
        """
        base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd()))
        model_path = base_dir / "risk_model.pkl"
        service = RiskScoringService(model_path=str(model_path))

        # Model dosyası yoksa küçük bir demo veri seti ile eğit
        if service.model is None or not model_path.exists():
            X = np.array(
                [
                    [0.5, 1, 1500.0, 12, 10, 0.2],
                    [0.7, 3, 2200.0, 15, 20, 0.4],
                    [0.1, 0, 4800.0, 30, 5, 0.1],
                    [0.9, 5, 1200.0, 9, 35, 0.6],
                    [0.2, 1, 5100.0, 21, 7, 0.15],
                    [0.3, 0, 4500.0, 18, 8, 0.12],
                    [1.2, 6, 900.0, 8, 45, 0.75],
                    [0.4, 2, 2000.0, 14, 16, 0.28],
                    [0.8, 4, 1300.0, 10, 28, 0.52],
                    [0.6, 1, 3200.0, 17, 9, 0.24],
                ],
                dtype=float,
            )
            y = np.array([0, 0, 0, 1, 0, 0, 1, 0, 1, 0], dtype=int)
            owner = users.get("demo_superadmin") or next(iter(users.values()), None)
            service.train(X, y, user=owner)
            self.stdout.write(self.style.SUCCESS(f"  - Risk modeli hazirlandi ({model_path.name})"))

        # Bilgi tabanı (ChatAIService için) - minimal içerik
        knowledge_dir = base_dir / "var"
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        knowledge_file = knowledge_dir / "ai_knowledge.json"
        if not knowledge_file.exists():
            doc_excerpt = ""
            guide_path = base_dir / "ai_assistant" / "AI_ASSISTANT_GUIDE_TR.md"
            try:
                doc_excerpt = guide_path.read_text(encoding="utf-8")[:2000]
            except Exception:
                doc_excerpt = ""
            sample_chunks = {
                "chunks": [
                    {
                        "id": 1,
                        "path": "docs/finasis_ai_overview",
                        "title": "FinAsis AI Asistan Genel Bakış",
                        "content": (
                            "FinAsis AI Asistan, finansal raporlama, nakit akışı analizi ve e-fatura otomasyonu alanlarında rehberlik sağlar. "
                            "Kullanıcılar nakit akışı, gelir tablosu, bilanço ve tahmin modüllerini doğal dilde sorgulayabilir."
                        ),
                    },
                    {
                        "id": 2,
                        "path": "docs/finasis_cashflow_tips",
                        "title": "Nakit Akışı İpuçları",
                        "content": (
                            "Net nakit akışı negatif olduğunda tahsilat süreçlerini hızlandırın, opsiyonel harcamaları erteleyin ve kısa vadeli finansman seçeneklerini değerlendirin. "
                            "Cari oran 1.2'nin altına düştüğünde dönen varlıkları artırmak için stok optimizasyonu yapın."
                        ),
                    },
                    {
                        "id": 3,
                        "path": str(guide_path.relative_to(base_dir)) if guide_path.exists() else "docs/ai_assistant_guide",
                        "title": "AI Asistan Kullanım Kılavuzu (Özet)",
                        "content": doc_excerpt or "FinAsis AI Asistan sesli komut, grounded QA ve muhasebe fiş otomasyonu özellikleri sunar.",
                    },
                ]
            }
            knowledge_file.write_text(json.dumps(sample_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"  - AI bilgi indeksi olusturuldu ({knowledge_file.relative_to(base_dir)})"))

        self._seed_ai_demo_records(users)

    def _print_summary(self, users: dict[str, User]):
        self.stdout.write("\nTest kullanıcı oturum bilgileri:")
        for username in sorted(users.keys()):
            self.stdout.write(f"  - {username} / {self.DEFAULT_PASSWORD}")
        self.stdout.write("")

    # ------------------------------------------------------------------ AI helpers

    def _seed_ai_demo_records(self, users: dict[str, User]):
        owner: Optional[User] = users.get("demo_owner") or users.get("demo_finance_manager") or users.get("demo_superadmin")
        if not owner:
            return

        now = timezone.now()

        risk_model, _ = AIModel.objects.update_or_create(
            name="RiskScoringModel",
            model_type="financial",
            defaults={
                "version": now.strftime("%Y%m%d"),
                "description": "Demo logistic regression risk modeli.",
                "accuracy": 0.88,
                "parameters": {"model": "logistic_regression", "features": 6},
                "last_trained": now,
                "is_active": True,
            },
        )
        chat_model, _ = AIModel.objects.update_or_create(
            name="ChatAssistantModel",
            model_type="chat",
            defaults={
                "version": "v2-mock",
                "description": "Yerel mock modda çalışan sohbet modeli.",
                "accuracy": 0.0,
                "parameters": {"mock_mode": True},
                "last_trained": now,
                "is_active": True,
            },
        )
        forecast_model, _ = AIModel.objects.update_or_create(
            name="FinancialForecastModel",
            model_type="prediction",
            defaults={
                "version": now.strftime("%Y%m%d"),
                "description": "Prophet tabanlı nakit akışı tahmin modeli.",
                "accuracy": 0.0,
                "parameters": {"seasonality": "auto"},
                "last_trained": now,
                "is_active": True,
            },
        )

        # Kullanıcı tercihleri
        UserPreference.objects.update_or_create(
            user=owner,
            defaults={
                "language": "tr",
                "risk_tolerance": "medium",
                "investment_horizon": "medium",
                "notification_preferences": {"email": True, "push": True},
                "ai_interaction_history": ["cash_flow_summary", "risk_alert"],
                "preferred_model": risk_model,
                "settings": {"voice_commands": True, "auto_insights": True},
            },
        )

        # Demo etkileşimler
        UserInteraction.objects.get_or_create(
            user=owner,
            interaction_type="chat",
            content="Bu ayki nakit akışım nasıl?",
            defaults={
                "ai_response": "Net nakit akışınız pozitife dönüyor; tahsilatlarınızı hızlandırmaya devam edin.",
                "processing_time": 0.35,
            },
        )

        # Demo içgörüler
        AIInsight.objects.get_or_create(
            user=owner,
            title="Likidite Uyarısı",
            defaults={
                "insight_type": "risk",
                "content": "Cari oranın 1.3 seviyesinde. Kısa vadeli yükümlülükler için ek nakit planlayın.",
                "priority": "high",
                "action_required": True,
                "action_description": "Tahsilatı gecikmiş müşterileri arayın ve ödeme planlarını hızlandırın.",
                "model": risk_model,
                "insight_data": {"current_ratio": 1.3, "target": 1.5},
                "expires_at": now + timezone.timedelta(days=14),
            },
        )

        # Demo öneriler
        Recommendation.objects.get_or_create(
            user=owner,
            title="FinAsis AI Önerileri",
            defaults={
                "recommendations": [
                    {"title": "Tahsilat Takibi", "details": "Geciken 3 müşteriyi arayın ve ödeme planı yapın."},
                    {"title": "Nakit Rezervi", "details": "Operasyon giderleri için 30 günlük nakit rezervi ayırın."},
                ],
                "category": "cash_flow",
                "priority": "medium",
                "action_required": True,
            },
        )

        Notification.objects.get_or_create(
            user=owner,
            title="AI Asistan Hazır",
            defaults={"message": "Yeni AI içgörüleri ve risk skorları hazır. Dashboard üzerinden inceleyebilirsiniz."},
        )


