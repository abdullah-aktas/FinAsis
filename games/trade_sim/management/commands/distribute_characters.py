# -*- coding: utf-8 -*-
"""
Karakterleri şehirlere dağıtır.
Kullanım: python manage.py distribute_characters
"""

from django.core.management.base import BaseCommand
from games.trade_sim.models import Character, City


class Command(BaseCommand):
    help = "Karakterleri sehirlere dagitir"

    def handle(self, *args, **options):
        self.stdout.write("\n[*] Karakterler sehirlere dagitiliyor...")

        cities = list(City.objects.all())
        if not cities:
            self.stdout.write(
                self.style.ERROR("  [!] Hic sehir yok! Once sehirleri olusturun.")
            )
            return

        characters = list(Character.objects.all())
        if not characters:
            self.stdout.write(self.style.WARNING("  [!] Hic karakter yok."))
            return

        # Karakterleri şehirlere döngüsel olarak dağıt
        distributed = 0
        for idx, char in enumerate(characters):
            city = cities[idx % len(cities)]
            old_city = char.city.name if char.city else "Yok"
            char.city = city
            char.save()
            distributed += 1
            self.stdout.write(f"  [+] {char.name}: {old_city} -> {city.name}")

        self.stdout.write(
            self.style.SUCCESS(f"\n  [+] {distributed} karakter sehirlere dagitildi!")
        )
