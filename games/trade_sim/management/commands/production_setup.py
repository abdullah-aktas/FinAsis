# -*- coding: utf-8 -*-
"""
Production Setup Command for TradeSim
Canlı ortam için TradeSim verilerini hazırlar
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from ...models import City, Product, CityMarket, Character


class Command(BaseCommand):
    help = "Canlı ortam için TradeSim verilerini hazırlar"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Mevcut verileri sıfırla ve yeniden oluştur",
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 TradeSim Production Setup başlatılıyor...")

        with transaction.atomic():
            if options["reset"]:
                self.stdout.write("🗑️ Mevcut veriler temizleniyor...")
                CityMarket.objects.all().delete()
                City.objects.all().delete()
                Product.objects.all().delete()

            # Şehirleri oluştur
            self.create_cities()

            # Ürünleri oluştur
            self.create_products()

            # Pazarları oluştur
            self.create_markets()

            # Demo kullanıcısı oluştur (sadece development)
            if options.get("create_demo", False):
                self.create_demo_user()

        self.stdout.write(self.style.SUCCESS("✅ TradeSim Production Setup tamamlandı!"))

    def create_cities(self):
        """Türkiye şehirlerini oluştur"""
        cities_data = [
            {
                "name": "İstanbul",
                "description": "Türkiye'nin ticaret merkezi",
                "coordinates": {"lat": 41.0082, "lng": 28.9784},
                "market_size": 5000,  # Çok büyük
                "sectors": ["teknoloji", "finans", "turizm", "tekstil"],
            },
            {
                "name": "Ankara",
                "description": "Başkent ve yönetim merkezi",
                "coordinates": {"lat": 39.9334, "lng": 32.8597},
                "market_size": 3000,  # Büyük
                "sectors": ["kamu", "savunma", "eğitim", "sağlık"],
            },
            {
                "name": "İzmir",
                "description": "Ege'nin incisi",
                "coordinates": {"lat": 38.4192, "lng": 27.1287},
                "market_size": 2500,  # Büyük
                "sectors": ["tarım", "turizm", "liman", "kimya"],
            },
            {
                "name": "Bursa",
                "description": "Otomotiv ve tekstil merkezi",
                "coordinates": {"lat": 40.1826, "lng": 29.0665},
                "market_size": 1500,  # Orta
                "sectors": ["otomotiv", "tekstil", "makine", "gıda"],
            },
            {
                "name": "Antalya",
                "description": "Akdeniz'in turizm başkenti",
                "coordinates": {"lat": 36.8969, "lng": 30.7133},
                "market_size": 1200,  # Orta
                "sectors": ["turizm", "tarım", "sera", "hizmet"],
            },
            {
                "name": "Adana",
                "description": "Çukurova'nın tarım merkezi",
                "coordinates": {"lat": 37.0000, "lng": 35.3213},
                "market_size": 1000,  # Orta
                "sectors": ["tarım", "tekstil", "gıda", "petrokimya"],
            },
        ]

        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data["name"], defaults=city_data
            )
            if created:
                self.stdout.write(f"📍 {city.name} şehri oluşturuldu")

        # Komşuluk ilişkilerini kur
        self.setup_city_neighbors()

    def setup_city_neighbors(self):
        """Şehirler arasında komşuluk ilişkileri kur"""
        try:
            istanbul = City.objects.get(name="İstanbul")
            ankara = City.objects.get(name="Ankara")
            izmir = City.objects.get(name="İzmir")
            bursa = City.objects.get(name="Bursa")
            antalya = City.objects.get(name="Antalya")
            adana = City.objects.get(name="Adana")

            # İstanbul komşuları
            istanbul.neighbors.set([ankara, bursa])

            # Ankara komşuları
            ankara.neighbors.set([istanbul, adana])

            # İzmir komşuları
            izmir.neighbors.set([antalya])

            # Bursa komşuları
            bursa.neighbors.set([istanbul, ankara])

            # Antalya komşuları
            antalya.neighbors.set([izmir, adana])

            # Adana komşuları
            adana.neighbors.set([ankara, antalya])

            self.stdout.write("🤝 Şehir komşulukları kuruldu")

        except City.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️ Bazı şehirler bulunamadı, komşuluklar kurulamadı"
                )
            )

    def create_products(self):
        """Ticaret ürünlerini oluştur"""
        products_data = [
            {
                "name": "Buğday",
                "description": "Temel gıda ürünü",
                "base_price": 150.0,
                "unit": "ton",
                "category": "tarım",
            },
            {
                "name": "Pamuk",
                "description": "Tekstil hammaddesi",
                "base_price": 800.0,
                "unit": "ton",
                "category": "tarım",
            },
            {
                "name": "Otomobil",
                "description": "Binek araç",
                "base_price": 450000.0,
                "unit": "adet",
                "category": "otomotiv",
            },
            {
                "name": "Tekstil",
                "description": "Hazır giyim ürünleri",
                "base_price": 50.0,
                "unit": "kg",
                "category": "tekstil",
            },
            {
                "name": "Bilgisayar",
                "description": "Masaüstü bilgisayar",
                "base_price": 15000.0,
                "unit": "adet",
                "category": "teknoloji",
            },
            {
                "name": "Turizm Hizmeti",
                "description": "Otel ve tatil hizmetleri",
                "base_price": 200.0,
                "unit": "gece",
                "category": "turizm",
            },
            {
                "name": "Zeytinyağı",
                "description": "Natürel sızma zeytinyağı",
                "base_price": 120.0,
                "unit": "litre",
                "category": "gıda",
            },
            {
                "name": "Makine",
                "description": "Endüstriyel makineler",
                "base_price": 75000.0,
                "unit": "adet",
                "category": "makine",
            },
            {
                "name": "İlaç",
                "description": "Tıbbi ilaçlar",
                "base_price": 25.0,
                "unit": "kutu",
                "category": "sağlık",
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"], defaults=product_data
            )
            if created:
                self.stdout.write(f"📦 {product.name} ürünü oluşturuldu")

    def create_markets(self):
        """Şehir pazarlarını oluştur"""
        import random
        from decimal import Decimal

        cities = City.objects.all()
        products = Product.objects.all()

        for city in cities:
            self.stdout.write(f"🏪 {city.name} pazarları oluşturuluyor...")

            for product in products:
                # Şehrin sektörlerine göre fiyat ve arz-talep ayarla
                price_multiplier = 1.0
                supply_base = 100
                demand_base = 100

                if product.category in city.sectors:
                    # Bu üründe uzman şehir - daha ucuz, fazla arz
                    price_multiplier = 0.8
                    supply_base = 150
                    demand_base = 80
                else:
                    # Bu üründe uzman değil - daha pahalı, az arz
                    price_multiplier = 1.2
                    supply_base = 70
                    demand_base = 120

                # Rastgele varyasyon ekle
                price = Decimal(
                    str(
                        product.base_price * price_multiplier * random.uniform(0.9, 1.1)
                    )
                )
                supply = supply_base + random.randint(-20, 20)
                demand = demand_base + random.randint(-20, 20)

                market, created = CityMarket.objects.get_or_create(
                    city=city,
                    product=product,
                    defaults={
                        "price": price,
                        "supply": max(supply, 10),  # Minimum 10
                        "demand": max(demand, 10),  # Minimum 10
                    },
                )

                if created:
                    self.stdout.write(f"  💰 {product.name}: {market.price}₺")

    def create_demo_user(self):
        """Demo kullanıcısı oluştur (sadece development)"""
        User = get_user_model()

        demo_user, created = User.objects.get_or_create(
            username="demo_trader",
            defaults={
                "email": "demo@finasis.com",
                "first_name": "Demo",
                "last_name": "Trader",
                "is_active": True,
            },
        )

        if created:
            demo_user.set_password("demo123")
            demo_user.save()
            self.stdout.write("👤 Demo kullanıcısı oluşturuldu: demo_trader / demo123")

            # Demo karakteri oluştur
            default_city = City.objects.first()
            character, char_created = Character.objects.get_or_create(
                user=demo_user,
                defaults={
                    "name": "Demo Trader",
                    "city": default_city,
                    "score": 50000,  # Başlangıç parası
                    "level": 1,
                    "choices": {
                        "inventory": {},
                        "badges": [],
                    },
                },
            )

            if char_created:
                self.stdout.write(f"🎮 Demo karakteri oluşturuldu: {character.name}")
