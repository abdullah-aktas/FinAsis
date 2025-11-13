from django.core.management.base import BaseCommand
from decimal import Decimal
from billing.models import Plan, Price, Module, PlanModule

BASE_MODULES = {
    # Finans ve muhasebe temel
    'reporting': {
        'name': 'Temel Raporlama',
        'description': 'Gelir-gider, kar-zarar, bilanço ve hızlı özet panolar.'
    },
    'budgeting': {
        'name': 'Bütçe Planlama',
        'description': 'Aylık bütçe hedefleri, sapma analizi ve senaryo çalışmaları.'
    },
    'cashflow': {
        'name': 'Nakit Akışı',
        'description': 'Günlük/aylık nakit akış projeksiyonları ve tahsilat/ödeme takibi.'
    },
    'accounting': {
        'name': 'Muhasebe',
        'description': 'Fiş/fatura girişleri, defterler ve temel muhasebe işlemleri.'
    },
    'banking': {
        'name': 'Banka İşlemleri',
        'description': 'Banka hareketleri, hesap ekstreleri ve cari entegrasyon.'
    },
    'bank_integration': {
        'name': 'Banka Entegrasyonları',
        'description': 'API ile otomatik banka entegrasyonu, mutabakat kolaylığı.'
    },

    # e-Dönüşüm (e-belge / e-defter)
    'efatura': {
        'name': 'e-Fatura',
        'description': 'GİB uyumlu e-Fatura oluşturma, gönderim ve arşivleme.'
    },
    'earsiv': {
        'name': 'e-Arşiv',
        'description': 'e-Arşiv fatura kesme, saklama ve alıcı paylaşım linkleri.'
    },
    'eirsaliye': {
        'name': 'e-İrsaliye',
        'description': 'e-İrsaliye düzenleme ve sevk süreçlerinin dijital takibi.'
    },
    'edefter': {
        'name': 'e-Defter',
        'description': 'Yevmiye/Kebir üretimi, berat oluşturma ve paketleme.'
    },

    # Analitik ve AI
    'analytics': {
        'name': 'Analitik & Gelişmiş Raporlama',
        'description': 'Gelişmiş kırılımlar, KPI panoları ve karşılaştırmalı analizler.'
    },
    'ai': {
        'name': 'AI Destekli Analiz',
        'description': 'AI ile tahmin, anomalilerin tespiti ve karar destek.'
    },

    # Operasyonel
    'inventory': {
        'name': 'Stok/Envanter',
        'description': 'Stok giriş/çıkış, ortalama maliyet ve envanter raporları.'
    },
    'reconciliation': {
        'name': 'Mutabakat',
        'description': 'BA/BS, cari ve banka mutabakat süreçlerinin yönetimi.'
    },
    'payroll': {
        'name': 'Bordro',
        'description': 'Maaş hesaplama, bordro raporu ve yasal kesintiler.'
    },

    # Kurumsal
    'audit': {
        'name': 'Denetim',
        'description': 'Kontrol testleri, risk değerlendirme ve denetim izleri.'
    },
    'blockchain': {
        'name': 'Blockchain Doğrulama',
        'description': 'Kayıtların bütünlüğünü blockchain ile damgalama/doğrulama.'
    },
    'multi_company': {
        'name': 'Çoklu Şirket',
        'description': 'Tek hesap altında birden fazla şirket yönetimi.'
    },
    'consolidation': {
        'name': 'Konsolidasyon',
        'description': 'Grup şirketlerinde konsolide raporlar ve eliminasyon.'
    },
    'priority_support': {
        'name': 'Öncelikli Destek',
        'description': 'Hızlı destek hattı, SLA ve atanan danışman.'
    },
    'integrations': {
        'name': 'Entegrasyonlar',
        'description': 'Muhasebe/CRM/e-ticaret ve dış sistem entegrasyonları.'
    },
    'webhooks_api': {
        'name': 'Webhook & API',
        'description': 'Webhook bildirimleri ve geliştirici dostu REST API.'
    },

    # Eğitim/LMS
    'lms': {
        'name': 'Eğitim/LMS',
        'description': 'Ders içerikleri, sınavlar ve ilerleme takibi.'
    },
    'advisors': {
        'name': 'Danışman/Koç Modülü',
        'description': 'Danışman eşleşmesi, görevler ve geri bildirim döngüsü.'
    },
    'kobi_analysis': {
        'name': 'KOBİ Analizi',
        'description': 'KOBİ’lere özel finansal sağlık ve gelişim raporları.'
    },
}

PLANS = [
    # KOBİ (SME) aile
    {
        'code': 'starter',
    'name': 'KOBİ Başlangıç',
        'audience': 'sme',
        'description': 'Küçük işletmeler için temel finansal yönetim ve başlangıç özellikleri.',
        'prices': {
            'month': Decimal('499.00'),
            'year': Decimal('499.00') * 12 * Decimal('0.85'),  # ~%15 indirim
        },
        'modules': [
            'reporting', 'budgeting', 'cashflow', 'accounting', 'banking'
        ],
    },
    {
        'code': 'sme_pro',
        'name': 'KOBİ Profesyonel',
        'audience': 'sme',
        'description': 'Büyüyen işletmeler için e-dönüşüm, bankacılık entegrasyonları ve AI analizleri.',
        'prices': {
            'month': Decimal('1599.00'),
            'year': Decimal('1599.00') * 12 * Decimal('0.82'),  # ~%18 indirim
        },
        'modules': [
            'reporting', 'budgeting', 'cashflow', 'accounting', 'banking', 'bank_integration',
            'efatura', 'earsiv', 'eirsaliye', 'edefter',
            'inventory', 'reconciliation', 'analytics', 'ai', 'integrations', 'kobi_analysis'
        ],
    },
    {
        'code': 'sme_enterprise',
        'name': 'Kurumsal',
        'audience': 'sme',
        'description': 'Gelişmiş entegrasyonlar, denetim, çoklu şirket ve özel destek.',
        'prices': {
            'month': Decimal('5999.00'),
            'year': Decimal('5999.00') * 12 * Decimal('0.80'),  # ~%20 indirim
        },
        'modules': [
            'reporting', 'budgeting', 'cashflow', 'accounting', 'banking', 'bank_integration',
            'efatura', 'earsiv', 'eirsaliye', 'edefter',
            'inventory', 'reconciliation', 'analytics', 'ai', 'integrations', 'kobi_analysis',
            'audit', 'multi_company', 'consolidation', 'blockchain', 'webhooks_api', 'priority_support', 'advisors'
        ],
    },

    # Eğitim (EDU) aile
    {
        'code': 'edu_student',
        'name': 'Eğitim Öğrenci',
        'audience': 'edu',
        'description': 'Öğrenciler için temel LMS ve raporlama.',
        'prices': {
            'month': Decimal('49.00'),
        },
        'modules': ['lms', 'reporting', 'analytics']
    },
    {
        'code': 'edu_teacher',
        'name': 'Eğitim Eğitmen',
        'audience': 'edu',
        'description': 'Eğitmenler için LMS, analitik ve AI destekli içerik.',
        'prices': {
            'month': Decimal('199.00'),
        },
        'modules': ['lms', 'reporting', 'analytics', 'ai']
    },
    {
        'code': 'edu_campus',
        'name': 'Eğitim Kampüs',
        'audience': 'edu',
        'description': 'Kurumsal eğitim yönetimi, entegrasyonlar ve çoklu organizasyon.',
        'prices': {
            'year': Decimal('4999.00'),
        },
        'modules': ['lms', 'reporting', 'analytics', 'integrations', 'multi_company', 'priority_support']
    },
]

class Command(BaseCommand):
    help = 'Billing planlarını ve modüllerini seed eder'

    def handle(self, *args, **options):
        # Modülleri oluştur
        for code, meta in BASE_MODULES.items():
            if isinstance(meta, dict):
                Module.objects.update_or_create(
                    code=code,
                    defaults={'name': meta.get('name', code), 'description': meta.get('description', meta.get('name', code))}
                )
            else:
                # Geriye dönük uyumluluk: eski string format
                Module.objects.update_or_create(
                    code=code,
                    defaults={'name': str(meta), 'description': str(meta)}
                )

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
        # Eski/taşınan plan kodlarını pasife al (ör. sme_basic)
        DEPRECATED_CODES = ['sme_basic', 'sme_starter']
        Plan.objects.filter(code__in=DEPRECATED_CODES).update(is_active=False)

        # Maksimum 3 SME planı aktif kalsın: starter, sme_pro, sme_enterprise
        ALLOWED_SME = ['starter', 'sme_pro', 'sme_enterprise']
        Plan.objects.filter(audience='sme').exclude(code__in=ALLOWED_SME).update(is_active=False)

        # EDU planları için izinli liste
        ALLOWED_EDU = ['edu_student', 'edu_teacher', 'edu_campus']
        Plan.objects.filter(audience='edu').exclude(code__in=ALLOWED_EDU).update(is_active=False)

        self.stdout.write(self.style.SUCCESS('Planlar ve fiyatlar güncellendi.'))
# Removed a duplicate Command implementation to avoid class redefinition conflict.
