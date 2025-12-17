# -*- coding: utf-8 -*-
"""
TradeSim oyunu için test verilerini oluşturur.
Kullanım: python manage.py setup_tradesim
"""

from django.core.management.base import BaseCommand
import random
from games.trade_sim.models import City, Product, CityMarket, Character, Quest


class Command(BaseCommand):
    help = "TradeSim oyunu icin test verilerini olusturur"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("==================================================")
        )
        self.stdout.write(
            self.style.SUCCESS("  TRADESIM TEST VERILERI OLUSTURULUYOR...")
        )
        self.stdout.write(
            self.style.SUCCESS("==================================================\n")
        )

        # 1. Şehirler Oluştur
        cities_data = [
            {
                "name": "Istanbul",
                "description": "Buyuk metropol sehir, finans ve ticaret merkezi",
                "market_size": 1000,
                "coordinates": {"x": 0, "y": 0},
                "sectors": ["gida", "tekstil", "teknoloji", "finans"],
                "neighbors": ["Ankara", "Trabzon", "Izmir"],
            },
            {
                "name": "Ankara",
                "description": "Baskent, idari ve sanayi merkezi",
                "market_size": 850,
                "coordinates": {"x": 100, "y": 50},
                "sectors": ["gida", "tarim", "sanayi"],
                "neighbors": ["Istanbul", "Konya", "Trabzon"],
            },
            {
                "name": "Izmir",
                "description": "Ege incisi, liman sehri",
                "market_size": 560,
                "coordinates": {"x": -50, "y": -30},
                "sectors": ["gida", "balikcilik", "tekstil"],
                "neighbors": ["Istanbul", "Antalya"],
            },
            {
                "name": "Antalya",
                "description": "Turizm merkezi, tarim sehri",
                "market_size": 720,
                "coordinates": {"x": -30, "y": -50},
                "sectors": ["gida", "meyve", "turizm"],
                "neighbors": ["Izmir", "Konya", "Mardin"],
            },
            {
                "name": "Konya",
                "description": "Tarim merkezi, geleneksel ticaret sehri",
                "market_size": 600,
                "coordinates": {"x": 80, "y": 80},
                "sectors": ["tarim", "gida", "hayvancilik"],
                "neighbors": ["Ankara", "Antalya", "Mardin"],
            },
            {
                "name": "Trabzon",
                "description": "Karadeniz liman sehri, cay ve fındık merkezi",
                "market_size": 650,
                "coordinates": {"x": 50, "y": 100},
                "sectors": ["gida", "cay", "findik", "balikcilik"],
                "neighbors": ["Istanbul", "Ankara"],
            },
            {
                "name": "Mardin",
                "description": "Guneydogu tarihi sehri, tarim ve el sanatlari merkezi",
                "market_size": 450,
                "coordinates": {"x": 180, "y": -10},
                "sectors": ["tarim", "gida", "el_sanatlari", "bakliyat"],
                "neighbors": ["Gaziantep", "Konya", "Antalya"],
            },
            {
                "name": "Gaziantep",
                "description": "Guneydogu ticaret merkezi",
                "market_size": 550,
                "coordinates": {"x": 150, "y": -20},
                "sectors": ["gida", "tekstil", "bakliyat"],
                "neighbors": ["Adana", "Mardin"],
            },
            {
                "name": "Adana",
                "description": "Cukurova tarim merkezi",
                "market_size": 500,
                "coordinates": {"x": 120, "y": -40},
                "sectors": ["tarim", "gida", "pamuk"],
                "neighbors": ["Gaziantep", "Antalya"],
            },
        ]

        self.stdout.write("[*] Sehirler olusturuluyor...")
        city_objects = {}
        city_neighbors = {}  # Şehir isimleri ve komşularını sakla
        for city_data in cities_data:
            # neighbors'ı sakla ama city_data'dan çıkar
            neighbors = city_data.get("neighbors", [])
            city_name = city_data["name"]
            city_neighbors[city_name] = neighbors

            # neighbors'ı city_data'dan çıkar çünkü City modelinde yok
            city_data_copy = city_data.copy()
            city_data_copy.pop("neighbors", None)

            city, created = City.objects.get_or_create(
                name=city_name, defaults=city_data_copy
            )
            city_objects[city_name] = city
            if created:
                self.stdout.write(self.style.SUCCESS(f"  [+] {city.name} olusturuldu"))
            else:
                self.stdout.write(f"  [!] {city.name} zaten mevcut")

        # Şehirler arası komşuluk ilişkileri
        self.stdout.write("\n[*] Sehir komsuluk iliskileri kuruluyor...")
        for city_name, neighbors in city_neighbors.items():
            if city_name in city_objects:
                city = city_objects[city_name]
                for neighbor_name in neighbors:
                    if neighbor_name in city_objects:
                        neighbor = city_objects[neighbor_name]
                        city.neighbors.add(neighbor)
                        self.stdout.write(
                            f"  [+] {city.name} <-> {neighbor.name} komsu yapildi"
                        )

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
            {
                "name": "Pamuk",
                "description": "Tekstil hammaddesi",
                "base_price": 150,
                "unit": "kg",
                "category": "tekstil",
            },
            {
                "name": "Bakir",
                "description": "Sanayi metali",
                "base_price": 200,
                "unit": "kg",
                "category": "madencilik",
            },
            {
                "name": "Yumurta",
                "description": "Taze yumurta",
                "base_price": 25,
                "unit": "adet",
                "category": "protein",
            },
            {
                "name": "Seker",
                "description": "Beyaz seker",
                "base_price": 40,
                "unit": "kg",
                "category": "gida",
            },
            {
                "name": "Zeytinyagi",
                "description": "Soguk sıkım zeytinyagi",
                "base_price": 250,
                "unit": "lt",
                "category": "gida",
            },
            {
                "name": "Cay",
                "description": "Siyah cay",
                "base_price": 180,
                "unit": "kg",
                "category": "icecek",
            },
        ]

        self.stdout.write("\n[*] Urunler olusturuluyor...")
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"], defaults=product_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  [+] {product.name} olusturuldu")
                )
            else:
                self.stdout.write(f"  [!] {product.name} zaten mevcut")

        # 3. Her şehir için pazar oluştur
        self.stdout.write("\n[*] Sehir pazarlari olusturuluyor...")
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
            self.style.SUCCESS(f"  [+] {created_count} pazar kaydi olusturuldu")
        )

        # 4. Karakterlere başlangıç parası ver ve şehirlere dağıt
        self.stdout.write("\n[*] Karakterlere baslangic parasi veriliyor...")
        characters = Character.objects.all()
        if characters.exists():
            updated = characters.update(score=10000)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [+] {updated} karakter guncellendi (10,000 lira)"
                )
            )

            # Şehirlere dağıt (karakterler farklı şehirlere atansın)
            cities = list(City.objects.all())
            if cities:
                chars_without_city = list(Character.objects.filter(city__isnull=True))
                for idx, char in enumerate(chars_without_city):
                    # Şehirleri döngüsel olarak dağıt
                    city = cities[idx % len(cities)]
                    char.city = city
                    char.save()
                    self.stdout.write(f"  [+] {char.name} {city.name} sehrine atandi")

                if chars_without_city:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [+] {len(chars_without_city)} karakter sehirlere dagitildi"
                        )
                    )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "  [!] Henuz karakter yok. Ilk giris yapinca otomatik olusacak."
                )
            )

        # 5. Görevler Oluştur
        self.stdout.write("\n[*] Gorevler olusturuluyor...")
        quests_data = [
            {
                "name": "İlk Ticaret",
                "description": "İlk şehir ticaretini tamamla.",
                "quest_type": "side",
                "requirements": {"trade_count": 1},
                "rewards": {"coins": 100, "xp": 10},
                "is_active": True,
            },
            {
                "name": "Usta Tüccar",
                "description": "5 farklı şehirde ticaret yap.",
                "quest_type": "main",
                "requirements": {"cities_visited": 5, "trade_count": 10},
                "rewards": {"coins": 500, "xp": 50},
                "is_active": True,
            },
            {
                "name": "Zengin Tüccar",
                "description": "10.000 lira kazan.",
                "quest_type": "main",
                "requirements": {"profit": 10000},
                "rewards": {"coins": 1000, "xp": 100},
                "is_active": True,
            },
            {
                "name": "Çeşitli Ürünler",
                "description": "10 farklı ürün ticareti yap.",
                "quest_type": "side",
                "requirements": {"product_variety": 10},
                "rewards": {"coins": 300, "xp": 30},
                "is_active": True,
            },
            {
                "name": "Hızlı Tüccar",
                "description": "Bir günde 20 ticaret yap.",
                "quest_type": "side",
                "requirements": {"daily_trades": 20},
                "rewards": {"coins": 400, "xp": 40},
                "is_active": True,
            },
        ]

        for quest_data in quests_data:
            quest, created = Quest.objects.get_or_create(
                name=quest_data["name"], defaults=quest_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  [+] {quest.name} gorevi olusturuldu")
                )
            else:
                self.stdout.write(f"  [!] {quest.name} gorevi zaten mevcut")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS("[OK] TRADESIM VERILERI BASARIYLA OLUSTURULDU!")
        )
        self.stdout.write("=" * 60)
        self.stdout.write(f"\n[*] Sehir sayisi: {City.objects.count()}")
        self.stdout.write(f"[*] Urun sayisi: {Product.objects.count()}")
        self.stdout.write(f"[*] Pazar sayisi: {CityMarket.objects.count()}")
        self.stdout.write(f"[*] Gorev sayisi: {Quest.objects.count()}")
        self.stdout.write(f"[*] Karakter sayisi: {Character.objects.count()}")
        self.stdout.write(
            "\n" + self.style.WARNING("[!] Simdi oyunu yenileyip test edebilirsiniz!")
        )
        self.stdout.write(
            self.style.WARNING("    http://127.0.0.1:8001/games/trade-sim/start/\n")
        )
