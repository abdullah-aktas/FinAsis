import random
from .models import CityMarket, Product, City
from django.db import transaction
from django.db.models import F
from django.utils import timezone

def update_city_market(city_market: CityMarket):
    """
    Şehirdeki ürünün fiyatını, arz ve talep durumuna göre günceller.
    """
    # Temel fiyat dinamiği: talep artarsa fiyat artar, arz artarsa fiyat düşer
    base_price = city_market.product.base_price
    demand_factor = 1 + (city_market.demand - 100) / 200  # 100 normal, 120 yüksek talep
    supply_factor = 1 - (city_market.supply - 100) / 300  # 100 normal, 70 düşük arz
    price = int(base_price * demand_factor * supply_factor)
    price = max(1, price)
    city_market.price = price
    city_market.last_updated = timezone.now()
    city_market.save()
    return city_market

def process_city_trade(from_city: City, to_city: City, product: Product, amount: int):
    """
    Şehirler arası ticaret işlemini gerçekleştirir ve pazarları günceller.
    - amount > 0 olmalı
    - from_city arzı yeterli olmalı (aksi halde 400 beklenir)
    - Yarış koşulları için satırlar kilitlenir
    - Arz/talep negatif olmayacak şekilde sınırlandırılır
    """
    if amount is None or int(amount) <= 0:
        raise ValueError("amount must be a positive integer")
    amount = int(amount)

    with transaction.atomic():
        # Satır kilitleme: aynı üründe aynı anda birden çok işlem yarışmasın
        try:
            from_market = (
                CityMarket.objects.select_for_update().get(city=from_city, product=product)
            )
            to_market = (
                CityMarket.objects.select_for_update().get(city=to_city, product=product)
            )
        except CityMarket.DoesNotExist:
            raise ValueError("Market not found for given city/product")

        if from_market.supply < amount:
            raise ValueError("insufficient supply in origin city")

        # Arz ve talep güncellemesi (F ifadeleri ile)
        from_market.supply = max(0, from_market.supply - amount)
        from_market.demand = max(0, from_market.demand + amount // 2)
        to_market.supply = max(0, to_market.supply + amount)
        to_market.demand = max(0, to_market.demand - amount // 2)

        # Makul üst sınırlar (aşırı büyümeyi engelle)
        for m in (from_market, to_market):
            m.supply = min(m.supply, 100000)
            m.demand = min(m.demand, 100000)

        # Fiyatları güncelle ve kaydet
        update_city_market(from_market)
        update_city_market(to_market)

        profit = (to_market.price - from_market.price) * amount

    return {
        'from_city': from_city.name,
        'to_city': to_city.name,
        'product': product.name,
        'amount': amount,
        'profit': profit,
        'from_price': from_market.price,
        'to_price': to_market.price
    }

def random_market_event(city_market: CityMarket):
    """
    Rastgele bir pazar olayı tetikler (ör. kıtlık, festival, bolluk).
    """
    event_type = random.choice(['kıtlık', 'festival', 'bolluk', 'normal'])
    if event_type == 'kıtlık':
        city_market.supply = max(10, city_market.supply - random.randint(10, 30))
        city_market.demand += random.randint(10, 30)
    elif event_type == 'festival':
        city_market.demand += random.randint(20, 50)
    elif event_type == 'bolluk':
        city_market.supply += random.randint(20, 50)
        city_market.demand = max(10, city_market.demand - random.randint(10, 30))
    update_city_market(city_market)
    return event_type 

def market_tick(city: City | None = None):
    """
    Basit bir piyasa zaman adımı. Tüm (veya belirtilen şehrin) marketlerinde
    arz/talep değerlerini 100'e doğru kademeli yaklaştırır ve fiyatları günceller.
    """
    qs = CityMarket.objects.all()
    if city is not None:
        qs = qs.filter(city=city)
    updated = 0
    for m in qs.select_related('product'):
        # 100'e yakınsama
        def converge(val: int, target: int = 100, step: int = 5):
            if val < target:
                return min(target, val + step)
            if val > target:
                return max(target, val - step)
            return val
        m.supply = converge(m.supply)
        m.demand = converge(m.demand)
        update_city_market(m)
        updated += 1
    return updated