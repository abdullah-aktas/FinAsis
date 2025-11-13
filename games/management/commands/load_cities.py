from django.core.management.base import BaseCommand
from games.trade_sim.models import City

CITIES = [
    {'name': 'Mardin Derik', 'description': 'Mardin ilinin Derik ilçesi', 'coordinates': {'x': 10, 'y': 20}},
    {'name': 'Denizli Çardak', 'description': 'Denizli ilinin Çardak ilçesi', 'coordinates': {'x': 30, 'y': 40}},
    {'name': 'İzmir Menemen', 'description': 'İzmir ilinin Menemen ilçesi', 'coordinates': {'x': 50, 'y': 60}},
    {'name': 'İzmir Aliağa', 'description': 'İzmir ilinin Aliağa ilçesi', 'coordinates': {'x': 52, 'y': 62}},
    {'name': 'Ankara Gölbaşı', 'description': 'Ankara ilinin Gölbaşı ilçesi', 'coordinates': {'x': 70, 'y': 80}},
    {'name': 'Çorum Alaca', 'description': 'Çorum ilinin Alaca ilçesi', 'coordinates': {'x': 90, 'y': 100}},
    {'name': 'Muğla Bodrum', 'description': 'Muğla ilinin Bodrum ilçesi', 'coordinates': {'x': 110, 'y': 120}},
    {'name': 'Irak Erbil', 'description': 'Irak Erbil şehri', 'coordinates': {'x': 200, 'y': 210}},
    {'name': 'Suriye Kamışlı', 'description': 'Suriye Kamışlı şehri', 'coordinates': {'x': 220, 'y': 230}},
    {'name': 'Suriye Şam', 'description': 'Suriye Şam şehri', 'coordinates': {'x': 240, 'y': 250}},
    {'name': 'Almanya Berlin', 'description': 'Almanya Berlin şehri', 'coordinates': {'x': 300, 'y': 310}},
    {'name': 'Fransa Paris', 'description': 'Fransa Paris şehri', 'coordinates': {'x': 320, 'y': 330}},
]

# Komşuluklar (isimler üzerinden)
NEIGHBORS = {
    'Mardin Derik': ['Suriye Kamışlı', 'Irak Erbil'],
    'Denizli Çardak': ['İzmir Menemen', 'Muğla Bodrum'],
    'İzmir Menemen': ['İzmir Aliağa', 'Denizli Çardak'],
    'İzmir Aliağa': ['İzmir Menemen'],
    'Ankara Gölbaşı': ['Çorum Alaca'],
    'Çorum Alaca': ['Ankara Gölbaşı'],
    'Muğla Bodrum': ['Denizli Çardak'],
    'Irak Erbil': ['Mardin Derik'],
    'Suriye Kamışlı': ['Mardin Derik', 'Suriye Şam'],
    'Suriye Şam': ['Suriye Kamışlı'],
    'Almanya Berlin': ['Fransa Paris'],
    'Fransa Paris': ['Almanya Berlin'],
}

SECTORS = ['finans', 'tarım', 'teknoloji', 'sanayi', 'sanat', 'turizm']

class Command(BaseCommand):
    help = 'Şehirleri, komşulukları ve sektör pazarlarını yükler.'

    def handle(self, *args, **options):
        name_to_city = {}
        # Şehirleri oluştur
        for c in CITIES:
            city, created = City.objects.get_or_create(
                name=c['name'],
                defaults={
                    'description': c['description'],
                    'coordinates': c['coordinates'],
                    'sectors': SECTORS,
                    'market_size': 1000,
                    'sector_markets': {s: {'price': 100, 'demand': 100} for s in SECTORS},
                }
            )
            name_to_city[c['name']] = city
        # Komşulukları ekle
        for city_name, neighbors in NEIGHBORS.items():
            city = name_to_city[city_name]
            for n in neighbors:
                city.neighbors.add(name_to_city[n])
            city.save()
        self.stdout.write(self.style.SUCCESS('Şehirler ve komşuluklar başarıyla yüklendi!')) 