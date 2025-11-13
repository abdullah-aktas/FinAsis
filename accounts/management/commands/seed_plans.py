from django.core.management.base import BaseCommand
from accounts.models import SubscriptionType

class Command(BaseCommand):
    help = "Seed predefined subscription plans for SME and Education audiences"

    def handle(self, *args, **options):
        plans = [
            # KOBİ - Starter
            dict(
                code='sme_starter', name='Başlangıç', description='KOBİ - Başlangıç Planı',
                audience='sme', period_options='monthly', monthly_price=299.00, yearly_price=None,
                user_limit=1,
                features=[
                    'Fatura giriş/çıkış',
                    'Cari hesap takibi',
                    'Temel raporlar (Gelir-Gider, Nakit Akışı)'
                ]
            ),
            # KOBİ - Pro
            dict(
                code='sme_pro', name='Profesyonel', description='KOBİ - Pro Plan',
                audience='sme', period_options='monthly_yearly', monthly_price=799.00, yearly_price=799.00*12,
                user_limit=5,
                features=[
                    'Başlangıç planındaki tüm özellikler',
                    'E-defter ve e-fatura entegrasyonu',
                    'Banka entegrasyonu',
                    'Yapay Zeka Destekli Finansal Analiz',
                    '5 kullanıcıya kadar destek'
                ]
            ),
            # KOBİ - Enterprise
            dict(
                code='sme_enterprise', name='Kurumsal', description='KOBİ - Enterprise Plan',
                audience='sme', period_options='yearly', monthly_price=1999.00, yearly_price=1999.00*12,
                user_limit=None,
                features=[
                    'Pro planındaki tüm özellikler',
                    'Gelişmiş raporlama (Dashboard, KPI, Yatırım Analizi)',
                    'Blockchain ile belge doğrulama',
                    'Sınırsız kullanıcı',
                    'Öncelikli destek & danışmanlık'
                ]
            ),
            # Eğitim - Öğrenci
            dict(
                code='edu_student', name='Öğrenci', description='Eğitim - Öğrenci Planı',
                audience='edu_student', period_options='monthly', monthly_price=49.00, yearly_price=None,
                user_limit=1,
                features=[
                    'Sanal şirket kurma',
                    'Temel muhasebe modülleri',
                    'Oyunlaştırılmış öğrenme',
                    'Kişisel ilerleme grafikleri'
                ]
            ),
            # Eğitim - Öğretmen
            dict(
                code='edu_teacher', name='Öğretmen', description='Eğitim - Öğretmen Planı',
                audience='edu_teacher', period_options='monthly', monthly_price=199.00, yearly_price=None,
                user_limit=None,
                features=[
                    'Öğrencilerin ilerlemesini takip etme',
                    'Ödev ve sınav oluşturma',
                    'Raporlama & değerlendirme',
                    'Sınırsız öğrenci yönetimi'
                ]
            ),
            # Eğitim - Kampüs/Okul
            dict(
                code='edu_campus', name='Kampüs/Okul', description='Eğitim - Kampüs Planı',
                audience='edu_campus', period_options='yearly', monthly_price=None, yearly_price=4999.00,
                user_limit=None,
                features=[
                    'Tüm öğretmen ve öğrencilere sınırsız erişim',
                    'Okula özel raporlama paneli',
                    'Ortak veri tabanı',
                    'Eğitim kurumuna özel AI destekli analizler'
                ]
            ),
        ]
        for p in plans:
            obj, created = SubscriptionType.objects.update_or_create(
                code=p['code'],
                defaults=p
            )
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'}: {obj.code}"))
        self.stdout.write(self.style.SUCCESS('Plan seeding completed.'))
