# -*- coding: utf-8 -*-
import pytest

@pytest.mark.django_db
def test_games_index(client):
    resp = client.get('/games/game_app/games/')
    assert resp.status_code == 200
    html = resp.content.decode('utf-8', errors='ignore').lower()
    assert ('finans oyunlar' in html) or ('oyunlar' in html)

@pytest.mark.django_db
def test_budget_challenge(client):
    resp = client.get('/games/game_app/budget-challenge/')
    assert resp.status_code == 200
    html = resp.content.decode('utf-8', errors='ignore').lower()
    assert ('bütçe' in html) or ('budget' in html)

@pytest.mark.django_db
def test_tradesim(client):
    resp = client.get('/games/game_app/tradesim/')
    assert resp.status_code == 200
    html = resp.content.decode('utf-8', errors='ignore')
    assert 'tradesim' in html.lower()
