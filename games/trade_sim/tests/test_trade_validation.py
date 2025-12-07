import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.response import Response as DRFResponse
from typing import cast
from games.trade_sim.models import City, Product, CityMarket


@pytest.mark.django_db
def test_city_trade_insufficient_supply_returns_400():
    client = APIClient()
    a = City.objects.create(
        name="A", description="A", sectors=[], market_size=1000, coordinates={}
    )
    b = City.objects.create(
        name="B", description="B", sectors=[], market_size=1000, coordinates={}
    )
    p = Product.objects.create(name="Altin", base_price=500)
    CityMarket.objects.create(city=a, product=p, price=500, supply=2, demand=100)
    CityMarket.objects.create(city=b, product=p, price=600, supply=100, demand=100)
    url = reverse("games:trade_sim:city_trade")
    payload = {
        "from_city": getattr(a, "id"),
        "to_city": getattr(b, "id"),
        "product_id": getattr(p, "id"),
        "amount": 5,
    }
    res = cast(DRFResponse, client.post(url, payload, format="json"))
    assert res.status_code == 400
    err = (res.data or {}) if isinstance(res.data, dict) else {}
    assert "insufficient" in (err.get("error") or "").lower()


@pytest.mark.django_db
def test_city_trade_negative_amount_returns_400():
    client = APIClient()
    a = City.objects.create(
        name="A", description="A", sectors=[], market_size=1000, coordinates={}
    )
    b = City.objects.create(
        name="B", description="B", sectors=[], market_size=1000, coordinates={}
    )
    p = Product.objects.create(name="Bakir", base_price=200)
    CityMarket.objects.create(city=a, product=p, price=200, supply=100, demand=100)
    CityMarket.objects.create(city=b, product=p, price=250, supply=100, demand=100)
    url = reverse("games:trade_sim:city_trade")
    payload = {
        "from_city": getattr(a, "id"),
        "to_city": getattr(b, "id"),
        "product_id": getattr(p, "id"),
        "amount": -1,
    }
    res = cast(DRFResponse, client.post(url, payload, format="json"))
    assert res.status_code == 400
