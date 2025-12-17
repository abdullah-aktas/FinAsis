from django.core.management.base import BaseCommand
from decimal import Decimal
from billing.models import Plan, Price, Module, PlanModule

BASE_MODULES = {
    # Finans ve muhasebe temel
    "reporting": {
        "name": "Temel Raporlama",
        "description": "Gelir-gider, kar-zarar, bilanço ve hızlı özet panolar.",
    },
    "budgeting": {
        "name": "Bütçe Planlama",
        "description": "Aylık bütçe hedefleri, sapma analizi ve senaryo çalışmaları.",
    },
    "cashflow": {
        "name": "Nakit Akışı",
        "description": "Günlük/aylık nakit akış projeksiyonları ve tahsilat/ödeme takibi.",
    },
    "accounting": {
        "name": "Muhasebe",
        "description": "Fiş/fatura girişleri, defterler ve temel muhasebe işlemleri.",
    },
    "banking": {
        "name": "Banka İşlemleri",
        "description": "Banka hareketleri, hesap ekstreleri ve cari entegrasyon.",
    },
    "bank_integration": {
        "name": "Banka Entegrasyonları",
        "description": "API ile otomatik banka entegrasyonu, mutabakat kolaylığı.",
    },
    # e-Dönüşüm (e-belge / e-defter)
    "efatura": {
        "name": "e-Fatura",
        "description": "GİB uyumlu e-Fatura oluşturma, gönderim ve arşivleme.",
    },
    "earsiv": {
        "name": "e-Arşiv",
        "description": "e-Arşiv fatura kesme, saklama ve alıcı paylaşım linkleri.",
    },
    "eirsaliye": {
        "name": "e-İrsaliye",
        "description": "e-İrsaliye düzenleme ve sevk süreçlerinin dijital takibi.",
    },
    "edefter": {
        "name": "e-Defter",
        "description": "Yevmiye/Kebir üretimi, berat oluşturma ve paketleme.",
    },
    # Analitik ve AI
    "analytics": {
        "name": "Analitik & Gelişmiş Raporlama",
        "description": "Gelişmiş kırılımlar, KPI panoları ve karşılaştırmalı analizler.",
    },
    "ai": {
        "name": "AI Destekli Analiz",
        "description": "AI ile tahmin, anomalilerin tespiti ve karar destek.",
    },
    # Operasyonel
    "inventory": {
        "name": "Stok/Envanter",
        "description": "Stok giriş/çıkış, ortalama maliyet ve envanter raporları.",
    },
    "reconciliation": {
        "name": "Mutabakat",
        "description": "BA/BS, cari ve banka mutabakat süreçlerinin yönetimi.",
    },
    "payroll": {
        "name": "Bordro",
        "description": "Maaş hesaplama, bordro raporu ve yasal kesintiler.",
    },
    # Kurumsal
    "audit": {
        "name": "Denetim",
        "description": "Kontrol testleri, risk değerlendirme ve denetim izleri.",
    },
    "blockchain": {
        "name": "Blockchain Doğrulama",
        "description": "Kayıtların bütünlüğünü blockchain ile damgalama/doğrulama.",
    },
    "multi_company": {
        "name": "Çoklu Şirket",
        "description": "Tek hesap altında birden fazla şirket yönetimi.",
    },
    "consolidation": {
        "name": "Konsolidasyon",
        "description": "Grup şirketlerinde konsolide raporlar ve eliminasyon.",
    },
    "priority_support": {
        "name": "Öncelikli Destek",
        "description": "Hızlı destek hattı, SLA ve atanan danışman.",
    },
    "integrations": {
        "name": "Entegrasyonlar",
        "description": "Muhasebe/CRM/e-ticaret ve dış sistem entegrasyonları.",
    },
    "webhooks_api": {
        "name": "Webhook & API",
        "description": "Webhook bildirimleri ve geliştirici dostu REST API.",
    },
    # Eğitim/LMS
    "lms": {
        "name": "Eğitim/LMS",
        "description": "Ders içerikleri, sınavlar ve ilerleme takibi.",
    },
    "advisors": {
        "name": "Danışman/Koç Modülü",
        "description": "Danışman eşleşmesi, görevler ve geri bildirim döngüsü.",
    },
    "kobi_analysis": {
        "name": "KOBİ Analizi",
        "description": "KOBİ’lere özel finansal sağlık ve gelişim raporları.",
    },
}

PLANS = [
    # KOBİ (SME) aile - GERÇEK FİYATLAR (Beta döneminde indirimli)
    {
        "code": "starter",
        "name": "KOBİ Başlangıç",
        "audience": "sme",
        "description": "Küçük işletmeler için temel finansal yönetim ve başlangıç özellikleri. Beta döneminde özel fiyat!",
        "prices": {
            "month": Decimal("199.00"),  # Beta: 499 → 199 (%60 indirim)
            "year": Decimal("1910.40"),  # 199 * 12 * 0.80 = ~%20 ek indirim
        },
        "modules": ["reporting", "budgeting", "cashflow", "accounting", "banking"],
        "trial_days": 14,
        "beta_discount_percent": Decimal("0.00"),  # Fiyat zaten beta fiyatı
        "is_beta_plan": True,
        "is_popular": False,
        "order": 1,
    },
    {
        "code": "sme_pro",
        "name": "KOBİ Profesyonel",
        "audience": "sme",
        "description": "Büyüyen işletmeler için e-dönüşüm, bankacılık entegrasyonları ve AI analizleri. Beta döneminde en popüler plan!",
        "prices": {
            "month": Decimal("599.00"),  # Beta: 1599 → 599 (%62 indirim)
            "year": Decimal("5391.00"),  # 599 * 12 * 0.75 = ~%25 ek indirim
        },
        "modules": [
            "reporting",
            "budgeting",
            "cashflow",
            "accounting",
            "banking",
            "bank_integration",
            "efatura",
            "earsiv",
            "eirsaliye",
            "edefter",
            "inventory",
            "reconciliation",
            "analytics",
            "ai",
            "integrations",
            "kobi_analysis",
        ],
        "trial_days": 30,
        "beta_discount_percent": Decimal("0.00"),
        "is_beta_plan": True,
        "is_popular": True,
        "order": 2,
    },
    {
        "code": "sme_enterprise",
        "name": "Kurumsal",
        "audience": "sme",
        "description": "Gelişmiş entegrasyonlar, denetim, çoklu şirket ve özel destek. Beta döneminde özel fiyat!",
        "prices": {
            "month": Decimal("1999.00"),  # Beta: 5999 → 1999 (%67 indirim)
            "year": Decimal("16791.60"),  # 1999 * 12 * 0.70 = ~%30 ek indirim
        },
        "modules": [
            "reporting",
            "budgeting",
            "cashflow",
            "accounting",
            "banking",
            "bank_integration",
            "efatura",
            "earsiv",
            "eirsaliye",
            "edefter",
            "inventory",
            "reconciliation",
            "analytics",
            "ai",
            "integrations",
            "kobi_analysis",
            "audit",
            "multi_company",
            "consolidation",
            "blockchain",
            "webhooks_api",
            "priority_support",
            "advisors",
        ],
        "trial_days": 30,
        "beta_discount_percent": Decimal("0.00"),
        "is_beta_plan": True,
        "is_popular": False,
        "order": 3,
    },
    # Eğitim (EDU) aile - BETA DÖNEMİ FİYATLARI
    {
        "code": "edu_student",
        "name": "Eğitim Öğrenci",
        "audience": "edu",
        "description": "Öğrenciler için temel LMS ve raporlama. Beta döneminde ücretsiz!",
        "prices": {
            "month": Decimal("0.00"),  # Beta: 49 → 0 (ücretsiz)
            "year": Decimal("0.00"),
        },
        "modules": ["lms", "reporting", "analytics"],
        "trial_days": 999,  # Beta döneminde sınırsız
        "beta_discount_percent": Decimal("100.00"),
        "is_beta_plan": True,
        "is_popular": False,
        "order": 4,
    },
    {
        "code": "edu_teacher",
        "name": "Eğitim Eğitmen",
        "audience": "edu",
        "description": "Eğitmenler için LMS, analitik ve AI destekli içerik. Beta döneminde özel fiyat!",
        "prices": {
            "month": Decimal("99.00"),  # Beta: 199 → 99 (%50 indirim)
            "year": Decimal("950.40"),  # 99 * 12 * 0.80 = ~%20 ek indirim
        },
        "modules": ["lms", "reporting", "analytics", "ai"],
        "trial_days": 30,
        "beta_discount_percent": Decimal("0.00"),
        "is_beta_plan": True,
        "is_popular": True,
        "order": 5,
    },
    {
        "code": "edu_campus",
        "name": "Eğitim Kampüs",
        "audience": "edu",
        "description": "Kurumsal eğitim yönetimi, entegrasyonlar ve çoklu organizasyon. Beta döneminde özel fiyat!",
        "prices": {
            "month": Decimal("999.00"),  # Beta: 4999/yıl → 999/ay (yıllık %76 indirim)
            "year": Decimal("8391.60"),  # 999 * 12 * 0.70 = ~%30 ek indirim
        },
        "modules": [
            "lms",
            "reporting",
            "analytics",
            "integrations",
            "multi_company",
            "priority_support",
        ],
        "trial_days": 30,
        "beta_discount_percent": Decimal("0.00"),
        "is_beta_plan": True,
        "is_popular": False,
        "order": 6,
    },
    # Oyuncu (GAMES) aile - BETA DÖNEMİ FİYATLARI
    {
        "code": "games_starter",
        "name": "Oyuncu Başlangıç",
        "audience": "games",
        "description": "Oyun modülleri ve temel özellikler. Beta döneminde ücretsiz!",
        "prices": {
            "month": Decimal("0.00"),  # Beta: ücretsiz
            "year": Decimal("0.00"),
        },
        "modules": ["lms", "reporting", "analytics"],
        "trial_days": 999,  # Beta döneminde sınırsız
        "beta_discount_percent": Decimal("100.00"),
        "is_beta_plan": True,
        "is_popular": False,
        "order": 7,
    },
    {
        "code": "games_pro",
        "name": "Oyuncu Pro",
        "audience": "games",
        "description": "Gelişmiş oyun özellikleri, turnuvalar ve rozetler. Beta döneminde özel fiyat!",
        "prices": {
            "month": Decimal("49.00"),  # Beta: özel fiyat
            "year": Decimal("470.40"),  # 49 * 12 * 0.80 = ~%20 ek indirim
        },
        "modules": ["lms", "reporting", "analytics", "ai"],
        "trial_days": 14,
        "beta_discount_percent": Decimal("0.00"),
        "is_beta_plan": True,
        "is_popular": True,
        "order": 8,
    },
]


class Command(BaseCommand):
    help = "Billing planlarını ve modüllerini seed eder"

    def handle(self, *args, **options):
        # Modülleri oluştur
        for code, meta in BASE_MODULES.items():
            if isinstance(meta, dict):
                Module.objects.update_or_create(
                    code=code,
                    defaults={
                        "name": meta.get("name", code),
                        "description": meta.get("description", meta.get("name", code)),
                    },
                )
            else:
                # Geriye dönük uyumluluk: eski string format
                Module.objects.update_or_create(
                    code=code, defaults={"name": str(meta), "description": str(meta)}
                )

        for data in PLANS:
            plan, _ = Plan.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "audience": data["audience"],
                    "description": data["description"],
                    "is_active": True,
                    "trial_days": data.get("trial_days", 14),
                    "beta_discount_percent": data.get(
                        "beta_discount_percent", Decimal("0.00")
                    ),
                    "is_beta_plan": data.get("is_beta_plan", False),
                    "is_popular": data.get("is_popular", False),
                    "order": data.get("order", 0),
                },
            )
            # Mevcut planı güncelle
            if not _:
                plan.name = data["name"]
                plan.description = data["description"]
                plan.trial_days = data.get("trial_days", 14)
                plan.beta_discount_percent = data.get(
                    "beta_discount_percent", Decimal("0.00")
                )
                plan.is_beta_plan = data.get("is_beta_plan", False)
                plan.is_popular = data.get("is_popular", False)
                plan.order = data.get("order", 0)
                plan.is_active = True
                plan.save()

            # Plan modülleri
            for mcode in data["modules"]:
                mod = Module.objects.get(code=mcode)
                PlanModule.objects.get_or_create(plan=plan, module=mod)
            # Fiyatlar
            for period, amount in data["prices"].items():
                Price.objects.update_or_create(
                    plan=plan,
                    period=period,
                    currency="TRY",
                    defaults={"amount": amount, "is_active": True},
                )
        # Eski/taşınan plan kodlarını pasife al (ör. sme_basic)
        DEPRECATED_CODES = ["sme_basic"]
        Plan.objects.filter(code__in=DEPRECATED_CODES).update(is_active=False)

        # Beta döneminde aktif planlar
        ALLOWED_SME = ["starter", "sme_pro", "sme_enterprise"]
        ALLOWED_EDU = ["edu_student", "edu_teacher", "edu_campus"]
        ALLOWED_GAMES = ["games_starter", "games_pro"]

        # Diğer planları pasife al
        Plan.objects.filter(audience="sme").exclude(code__in=ALLOWED_SME).update(
            is_active=False
        )
        Plan.objects.filter(audience="edu").exclude(code__in=ALLOWED_EDU).update(
            is_active=False
        )
        Plan.objects.filter(audience="games").exclude(code__in=ALLOWED_GAMES).update(
            is_active=False
        )

        # Beta indirim kuponları oluştur
        self._create_beta_discounts()

        self.stdout.write(
            self.style.SUCCESS("✅ Beta dönemine uygun planlar ve fiyatlar güncellendi.")
        )
        self.stdout.write(
            self.style.SUCCESS(
                "📊 KOBİ planları: Başlangıç (₺199), Profesyonel (₺599), Kurumsal (₺1999)"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "🎓 Eğitim planları: Öğrenci (Ücretsiz), Eğitmen (₺99), Kampüs (₺999)"
            )
        )
        self.stdout.write(
            self.style.SUCCESS("🎮 Oyuncu planları: Başlangıç (Ücretsiz), Pro (₺49)")
        )
        self.stdout.write(self.style.SUCCESS("🎁 Beta indirim kuponları oluşturuldu!"))

    def _create_beta_discounts(self):
        """Beta dönemine özel indirim kuponları oluştur"""
        from billing.models import Discount
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from datetime import timedelta

        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            return

        # Beta dönemi bitiş tarihi (6 ay sonra)
        beta_end = timezone.now() + timedelta(days=180)

        beta_coupons = [
            {
                "code": "BETA50",
                "name": "Beta Dönemi %50 İndirim",
                "description": "Beta dönemine özel %50 indirim kuponu. Tüm planlarda geçerli.",
                "discount_type": "PERCENTAGE",
                "discount_value": Decimal("50.00"),
                "valid_from": timezone.now(),
                "valid_until": beta_end,
                "max_uses": 1000,
                "max_uses_per_user": 1,
            },
            {
                "code": "BETA30",
                "name": "Beta Dönemi %30 İndirim",
                "description": "Beta dönemine özel %30 indirim kuponu. Tüm planlarda geçerli.",
                "discount_type": "PERCENTAGE",
                "discount_value": Decimal("30.00"),
                "valid_from": timezone.now(),
                "valid_until": beta_end,
                "max_uses": 5000,
                "max_uses_per_user": 1,
            },
            {
                "code": "BETAPIONEER",
                "name": "Beta Pioneer Özel İndirim",
                "description": "İlk 100 beta kullanıcısına özel %60 indirim. Sadece yıllık planlarda geçerli.",
                "discount_type": "PERCENTAGE",
                "discount_value": Decimal("60.00"),
                "valid_from": timezone.now(),
                "valid_until": beta_end,
                "max_uses": 100,
                "max_uses_per_user": 1,
            },
        ]

        for coupon_data in beta_coupons:
            discount, created = Discount.objects.get_or_create(
                code=coupon_data["code"],
                defaults={
                    **coupon_data,
                    "created_by": admin_user,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(
                    f"  ✓ İndirim kuponu oluşturuldu: {coupon_data['code']}"
                )
            else:
                # Mevcut kuponu güncelle
                for key, value in coupon_data.items():
                    if key != "code":
                        setattr(discount, key, value)
                discount.is_active = True
                discount.save()
                self.stdout.write(
                    f"  → İndirim kuponu güncellendi: {coupon_data['code']}"
                )


# Removed a duplicate Command implementation to avoid class redefinition conflict.
