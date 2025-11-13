from django.core.management.base import BaseCommand
from games.trade_sim.models import City, Product, CityMarket, Quest

class Command(BaseCommand):
    help = 'Seed default cities, products, markets, and a starter quest for Trade Sim'

    def handle(self, *args, **options):
        # Cities
        cities = [
            ('Başlangıç', 'Yeni oyuncular için başlangıç şehri', ['genel'], {'x': 0, 'y': 0}),
            ('İstanbul', 'Finans ve ticaret merkezi', ['finans', 'teknoloji', 'tarım'], {'x': 10, 'y': 5}),
        ]
        for name, desc, sectors, coords in cities:
            city, created = City.objects.get_or_create(name=name, defaults={
                'description': desc,
                'sectors': sectors,
                'market_size': 1000,
                'coordinates': coords,
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f'City created: {name}'))
        # Products
        products = [
            ('Buğday', 'Temel ürün', 100, 'kg', 'tarım'),
            ('Bakır', 'Sanayi girdisi', 200, 'kg', 'madencilik'),
        ]
        for name, desc, base_price, unit, category in products:
            product, created = Product.objects.get_or_create(name=name, defaults={
                'description': desc,
                'base_price': base_price,
                'unit': unit,
                'category': category,
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f'Product created: {name}'))
        # Markets
        for city in City.objects.all():
            for product in Product.objects.all():
                market, created = CityMarket.objects.get_or_create(
                    city=city, product=product,
                    defaults={'price': product.base_price, 'supply': 100, 'demand': 100}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Market created: {city.name} - {product.name}'))
        # Starter quest
        Quest.objects.get_or_create(
            name='İlk Ticaret',
            defaults={
                'description': 'İlk şehir ticaretini tamamla.',
                'quest_type': 'side',
                'requirements': {'trade_count': 1},
                'rewards': {'coins': 100, 'xp': 10},
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS('Trade Sim seeding completed.'))
