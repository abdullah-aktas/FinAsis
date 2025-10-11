from django.core.management.base import BaseCommand
from decimal import Decimal
from src.apps.billing.models import Plan, Price, Module, PlanModule

BASE_MODULES = {
    'reporting': 'Temel Raporlama',
    'budgeting': 'Bütçe Planlama',
    'cashflow': 'Nakit Akışı',
    'efatura': 'e-Fatura / e-Arşiv',
    'ai': 'AI Destekli Analiz',
    'priority_support': 'Öncelikli Destek',
    'integrations': 'Entegrasyonlar',
}

PLANS = [
    {
        'code': 'starter',
        'name': 'Starter',
        'audience': 'sme',
        'description': 'Küçük işletmeler için temel finansal yönetim ve başlangıç özellikleri.',
        'prices': {
            'month': Decimal('499.00'),
            'year': Decimal('499.00') * 12 * Decimal('0.85'),  # ~%15 indirim
        },
        'modules': ['reporting', 'budgeting', 'cashflow'],
    },
    {
        'code': 'sme_pro',
        'name': 'KOBİ Profesyonel',
        'audience': 'sme',
        'description': 'Büyüyen işletmeler için e-dönüşüm ve AI analizleri.',
        'prices': {
            'month': Decimal('899.00'),
            'year': Decimal('899.00') * 12 * Decimal('0.82'),  # ~%18 indirim
        },
        'modules': ['reporting', 'budgeting', 'cashflow', 'efatura', 'ai', 'integrations'],
    },
    {
        'code': 'sme_enterprise',
        'name': 'Kurumsal',
        'audience': 'sme',
        'description': 'Gelişmiş entegrasyonlar ve özel destek.',
        'prices': {
            'month': Decimal('1799.00'),
            'year': Decimal('1799.00') * 12 * Decimal('0.80'),  # ~%20 indirim
        },
        'modules': ['reporting', 'budgeting', 'cashflow', 'efatura', 'ai', 'priority_support', 'integrations'],
    },
]

class Command(BaseCommand):
    help = 'Billing planlarını ve modüllerini seed eder'

    def handle(self, *args, **options):
        # Modülleri oluştur
        for code, name in BASE_MODULES.items():
            Module.objects.get_or_create(code=code, defaults={'name': name, 'description': name})

        for data in PLANS:
            plan, _ = Plan.objects.get_or_create(code=data['code'], defaults={
                'name': data['name'], 'audience': data['audience'], 'description': data['description'], 'is_active': True,
            })
            # Plan modülleri
            for mcode in data['modules']:
                mod = Module.objects.get(code=mcode)
                PlanModule.objects.get_or_create(plan=plan, module=mod)
            # Fiyatlar
            for period, amount in data['prices'].items():
                Price.objects.update_or_create(
                    plan=plan, period=period, currency='TRY',
                    defaults={'amount': amount, 'is_active': True}
                )
        self.stdout.write(self.style.SUCCESS('Planlar ve fiyatlar güncellendi.'))
# Removed a duplicate Command implementation to avoid class redefinition conflict.
