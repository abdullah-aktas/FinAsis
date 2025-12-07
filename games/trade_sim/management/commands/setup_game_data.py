# -*- coding: utf-8 -*-
"""
TradeSim oyunu için test verilerini oluşturur.
Kullanım: python manage.py setup_game_data
"""

from django.core.management.base import BaseCommand
import random
from games.trade_sim.models import City, Product, CityMarket, Character


class Command(BaseCommand):
    help = "TradeSim oyunu icin test verilerini olusturur"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🎮 TradeSim Test Verileri Oluşturuluyor...")
        )

        # 1. Şehirler Oluştur
        cities_data = [
            {
                "name": "Istanbul",
                "description": "Buyuk metropol sehir",
                "market_size": 1000,
                "coordinates": {"x": 0, "y": 0},
                "sectors": ["gida", "tekstil", "teknoloji"],
            },
            {
                "name": "Ankara",
                "description": "Baskent",
                "market_size": 850,
                "coordinates": {"x": 100, "y": 50},
                "sectors": ["gida", "tarim"],
            },
            {
                "name": "Izmir",
                "description": "Ege incisi",
                "market_size": 560,
                "coordinates": {"x": -50, "y": -30},
                "sectors": ["gida", "balikcilik"],
            },
            {
                "name": "Bursa",
                "description": "Yesil sehir",
                "market_size": 240,
                "coordinates": {"x": 20, "y": 20},
                "sectors": ["gida", "meyve"],
            },
            {
                "name": "Antalya",
                "description": "Turizm merkezi",
                "market_size": 720,
                "coordinates": {"x": -30, "y": -50},
                "sectors": ["gida", "meyve"],
            },
        ]

        self.stdout.write("📍 Sehirler olusturuluyor...")
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data["name"], defaults=city_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✅ {city.name} olusturuldu"))
            else:
                self.stdout.write(f"  ℹ️  {city.name} zaten mevcut")

        # 2. Ürünler Oluştur
        products_data = [
            {
                "name": "Bugday",
                "description": "Temel gida urunu",
                "base_price": 28,
                "unit": "kg",
                "category": "gida",
            },
            {
                "name": "Elma",
                "description": "Taze meyve",
                "base_price": 45,
                "unit": "kg",
                "category": "meyve",
            },
            {
                "name": "Ekmek",
                "description": "Gunluk ekmek",
                "base_price": 12,
                "unit": "adet",
                "category": "gida",
            },
            {
                "name": "Peynir",
                "description": "Sut urunu",
                "base_price": 180,
                "unit": "kg",
                "category": "sut",
            },
            {
                "name": "Kahve",
                "description": "Filtre kahve",
                "base_price": 320,
                "unit": "kg",
                "category": "icecek",
            },
            {
                "name": "Balik",
                "description": "Taze balik",
                "base_price": 95,
                "unit": "kg",
                "category": "protein",
            },
            {
                "name": "Zeytin",
                "description": "Yesil zeytin",
                "base_price": 85,
                "unit": "kg",
                "category": "gida",
            },
            {
                "name": "Domates",
                "description": "Taze domates",
                "base_price": 35,
                "unit": "kg",
                "category": "sebze",
            },
        ]

        self.stdout.write("\n🛒 Urunler olusturuluyor...")
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"], defaults=product_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {product.name} olusturuldu")
                )
            else:
                self.stdout.write(f"  ℹ️  {product.name} zaten mevcut")

        # 3. Her şehir için pazar oluştur
        self.stdout.write("\n🏪 Sehir pazarlari olusturuluyor...")
        created_count = 0
        for city in City.objects.all():
            for product in Product.objects.all():
                # Her şehirde farklı fiyatlar ve stok
                price_variation = random.uniform(0.8, 1.3)
                price = int(product.base_price * price_variation)
                supply = random.randint(100, 2500)
                demand = random.randint(50, 150)

                market, created = CityMarket.objects.get_or_create(
                    city=city,
                    product=product,
                    defaults={"price": price, "supply": supply, "demand": demand},
                )
                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"  ✅ {created_count} pazar kaydi olusturuldu")
        )

        # 4. Karakterlere başlangıç parası ver
        self.stdout.write("\n💰 Karakterlere baslangic parasi veriliyor...")
        characters = Character.objects.all()
        if characters.exists():
            updated = characters.update(score=10000)
            self.stdout.write(
                self.style.SUCCESS(f"  ✅ {updated} karakter guncellendi (10,000 lira)")
            )

            # İlk şehri ata
            default_city = City.objects.first()
            if default_city:
                for char in Character.objects.filter(city__isnull=True):
                    char.city = default_city
                    char.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✅ Karakterler {default_city.name} sehrine atandi"
                    )
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "  ⚠️  Henuz karakter yok. Ilk giris yapinca otomatik olusacak."
                )
            )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("✅ TAMAMLANDI!"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"📍 Sehir sayisi: {City.objects.count()}")
        self.stdout.write(f"🛒 Urun sayisi: {Product.objects.count()}")
        self.stdout.write(f"🏪 Pazar sayisi: {CityMarket.objects.count()}")
        self.stdout.write(f"👤 Karakter sayisi: {Character.objects.count()}")
        self.stdout.write("\n🎮 Simdi oyunu yenileyip test edebilirsiniz!")
        self.stdout.write("   http://127.0.0.1:8001/games/trade-sim/start/")
