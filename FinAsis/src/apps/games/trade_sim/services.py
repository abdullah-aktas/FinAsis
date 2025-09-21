import random
from .models import CityMarket, Product, City
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
    """
    from_market = CityMarket.objects.get(city=from_city, product=product)
    to_market = CityMarket.objects.get(city=to_city, product=product)
    # Arz ve talep güncellemesi
    from_market.supply -= amount
    from_market.demand += amount // 2
    to_market.supply += amount
    to_market.demand -= amount // 2
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