# -*- coding: utf-8 -*-
import pytest

@pytest.mark.django_db
def test_games_index(client):
    resp = client.get('/games/game_app/games/')
    assert resp.status_code == 200
    text = resp.content.decode('utf-8', errors='ignore').lower()
    assert ('finans oyunlar' in text or 'oyunlar' in text or 'games' in text)

@pytest.mark.django_db
def test_budget_challenge(client):
    resp = client.get('/games/game_app/budget-challenge/')
    assert resp.status_code == 200
    text = resp.content.decode('utf-8', errors='ignore').lower()
    assert ('bütçe' in text or 'butce' in text or 'budget' in text)

@pytest.mark.django_db
def test_tradesim(client):
    resp = client.get('/games/game_app/tradesim/')
    assert resp.status_code == 200
    text = resp.content.decode('utf-8', errors='ignore').lower()
    assert ('tradesim' in text or 'trade sim' in text)
