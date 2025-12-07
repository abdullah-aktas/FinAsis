import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from games.trade_sim.models import City, Product, CityMarket


@pytest.mark.django_db
def test_product_list():
    client = APIClient()
    url = reverse("games:trade_sim:product_list")
    response = client.get(url)
    assert response.status_code == 200
    assert "products" in response.data


@pytest.mark.django_db
def test_city_market_list():
    client = APIClient()
    city = City.objects.create(
        name="TestCity",
        description="Test",
        sectors=[],
        market_size=1000,
        coordinates={},
    )
    product = Product.objects.create(name="Buğday", base_price=100)
    CityMarket.objects.create(
        city=city, product=product, price=120, supply=100, demand=100
    )
    url = reverse("games:trade_sim:city_market_list", args=[city.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "markets" in response.data
    assert response.data["markets"][0]["product"] == "Buğday"


@pytest.mark.django_db
def test_city_trade():
    client = APIClient()
    city1 = City.objects.create(
        name="A", description="A", sectors=[], market_size=1000, coordinates={}
    )
    city2 = City.objects.create(
        name="B", description="B", sectors=[], market_size=1000, coordinates={}
    )
    product = Product.objects.create(name="Elma", base_price=50)
    CityMarket.objects.create(
        city=city1, product=product, price=50, supply=100, demand=100
    )
    CityMarket.objects.create(
        city=city2, product=product, price=60, supply=100, demand=100
    )
    url = reverse("games:trade_sim:city_trade")
    data = {
        "from_city": city1.id,
        "to_city": city2.id,
        "product_id": product.id,
        "amount": 5,
    }
    response = client.post(url, data, format="json")
    assert response.status_code == 200
    assert response.data["status"] == "ok"
    assert response.data["result"]["amount"] == 5


@pytest.mark.django_db
def test_trigger_market_event():
    client = APIClient()
    city = City.objects.create(
        name="EventCity",
        description="Event",
        sectors=[],
        market_size=1000,
        coordinates={},
    )
    product = Product.objects.create(name="Arpa", base_price=80)
    CityMarket.objects.create(
        city=city, product=product, price=80, supply=100, demand=100
    )
    url = reverse("games:trade_sim:trigger_market_event")
    data = {"city_id": city.id, "product_id": product.id}
    response = client.post(url, data, format="json")
    assert response.status_code == 200
    assert response.data["status"] == "ok"
    assert "event" in response.data
