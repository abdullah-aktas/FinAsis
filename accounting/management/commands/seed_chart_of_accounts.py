from django.core.management.base import BaseCommand
from accounting.models import GLAccount, Company

CORE_ACCOUNTS = [
    ("100", "Kasa", "ASSET"),
    ("102", "Banka", "ASSET"),
    ("120", "Alıcılar", "ASSET"),
    ("191", "İndirilecek KDV", "ASSET"),
    ("320", "Satıcılar", "LIAB"),
    ("391", "Hesaplanan KDV", "LIAB"),
    ("500", "Sermaye", "EQUITY"),
    ("570", "Geçmiş Yıl Kar/Zararı", "EQUITY"),
    ("600", "Yurtiçi Satışlar", "INCOME"),
    ("610", "Satış İskontoları", "INCOME"),
    ("620", "Satılan Malın Maliyeti", "EXPENSE"),
    ("630", "Araştırma ve Geliştirme Giderleri", "EXPENSE"),
    ("770", "Genel Yönetim Giderleri", "EXPENSE"),
]

class Command(BaseCommand):
    help = "Şirketler için temel Tek Düzen hesap planı subset'i oluşturur."

    def add_arguments(self, parser):
        parser.add_argument('--company-id', type=int, help='Sadece belirtilen company id için çalıştır')

    def handle(self, *args, **options):
        qs = Company.objects.all()
        if options.get('company_id'):
            qs = qs.filter(id=options['company_id'])
        created_total = 0
        for company in qs:
            for code, name, cat in CORE_ACCOUNTS:
                obj, created = GLAccount.objects.get_or_create(company=company, code=code, defaults={
                    'name': name,
                    'category': cat,
                    'currency': company.base_currency,
                })
                if created:
                    created_total += 1
        self.stdout.write(self.style.SUCCESS(f"Tamamlandı. Oluşturulan yeni hesap sayısı: {created_total}"))
