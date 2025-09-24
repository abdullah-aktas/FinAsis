from django.core.management.base import BaseCommand
from src.apps.billing.models import Plan, Price, Module, PlanModule, PlanGroup
from django.contrib.auth.models import Group
from decimal import Decimal, ROUND_HALF_UP

class Command(BaseCommand):
    help = 'Seed billing plans and prices for SME and Education'

    def handle(self, *args, **options):
        plans = [
            # KOBİ
            dict(code='sme_starter', name='Starter', description='KOBİ - Başlangıç', audience='sme', prices=[('month', 299.00)]),
            dict(code='sme_pro', name='Pro', description='KOBİ - Pro', audience='sme', prices=[('month', 799.00), ('year', 799.00*12)]),
            dict(code='sme_enterprise', name='Enterprise', description='KOBİ - Kurumsal', audience='sme', prices=[('year', 1999.00*12)]),
            # Eğitim
            dict(code='edu_student', name='Öğrenci', description='Eğitim - Öğrenci', audience='edu', prices=[('month', 49.00)]),
            dict(code='edu_teacher', name='Öğretmen', description='Eğitim - Öğretmen', audience='edu', prices=[('month', 199.00)]),
            dict(code='edu_campus', name='Kampüs', description='Eğitim - Kampüs/Okul', audience='edu', prices=[('year', 4999.00)]),
        ]
        for p in plans:
            plan, _ = Plan.objects.update_or_create(code=p['code'], defaults={
                'name': p['name'], 'description': p['description'], 'audience': p['audience'], 'is_active': True
            })
            # Sağlanan fiyatlardan eksikleri tamamla: her plan için aylık ve yıllık olsun
            provided = {k: Decimal(str(v)) for (k, v) in p['prices']}
            month_amount = provided.get('month')
            year_amount = provided.get('year')
            if month_amount is None and year_amount is not None:
                # Aylık yoksa yıllığı 12'ye bölerek türet (2 hane)
                month_amount = (year_amount / Decimal('12')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if year_amount is None and month_amount is not None:
                # Yıllık yoksa 12x aylık olarak türet
                year_amount = (month_amount * Decimal('12')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            # En azından biri olmalı; aksi halde atla
            if month_amount is not None:
                Price.objects.update_or_create(
                    plan=plan, period='month', currency='TRY', defaults={'amount': month_amount, 'is_active': True}
                )
            if year_amount is not None:
                Price.objects.update_or_create(
                    plan=plan, period='year', currency='TRY', defaults={'amount': year_amount, 'is_active': True}
                )
            # Grupları oluştur ve bağla (PlanGroup)
            group, _ = Group.objects.get_or_create(name=p['code'])
            PlanGroup.objects.update_or_create(plan=plan, group=group)

        # Modüller
        modules = {
            'invoice': 'Fatura',
            'cariler': 'Cari Hesap',
            'reports_basic': 'Temel Raporlar',
            'einvoice': 'E-Fatura',
            'edefter': 'E-Defter',
            'bank': 'Banka Entegrasyonu',
            'ai_finance': 'Yapay Zeka Analiz',
            'reports_adv': 'Gelişmiş Raporlama',
            'blockchain': 'Blockchain Doğrulama',
            'unlimited_users': 'Sınırsız Kullanıcı',
            'edu_company': 'Sanal Şirket',
            'edu_gamify': 'Oyunlaştırma',
            'edu_progress': 'İlerleme Grafikleri',
            'edu_assign': 'Ödev/Sınav',
            'edu_manage': 'Sınırsız Öğrenci Yönetimi',
            # Projenin amacıyla uyumlu ek modüller
            'tradesim': 'TradeSim Oyun Modu',
            'lms_integration': 'LMS Entegrasyonu',
            'api_access': 'API Erişimi',
        }
        for code, name in modules.items():
            Module.objects.update_or_create(code=code, defaults={'name': name, 'is_active': True})

        # Plan → Modül eşlemesi
        mapping = {
            'sme_starter': ['invoice', 'cariler', 'reports_basic', 'tradesim'],
            'sme_pro': ['invoice', 'cariler', 'reports_basic', 'einvoice', 'edefter', 'bank', 'ai_finance', 'api_access', 'tradesim'],
            'sme_enterprise': ['invoice', 'cariler', 'reports_basic', 'einvoice', 'edefter', 'bank', 'ai_finance', 'reports_adv', 'blockchain', 'unlimited_users', 'api_access', 'lms_integration', 'tradesim'],
            'edu_student': ['edu_company', 'edu_gamify', 'edu_progress', 'tradesim'],
            'edu_teacher': ['edu_assign', 'edu_manage', 'reports_basic', 'tradesim'],
            'edu_campus': ['edu_assign', 'edu_manage', 'reports_adv', 'lms_integration', 'tradesim'],
        }
        for plan_code, module_codes in mapping.items():
            plan = Plan.objects.filter(code=plan_code).first()
            if not plan:
                continue
            for mcode in module_codes:
                mod = Module.objects.filter(code=mcode).first()
                if not mod:
                    continue
                PlanModule.objects.update_or_create(plan=plan, module=mod)
        self.stdout.write(self.style.SUCCESS('Billing plans and prices seeded.'))
