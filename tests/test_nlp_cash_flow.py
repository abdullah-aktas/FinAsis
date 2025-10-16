# -*- coding: utf-8 -*-
import types
import pandas as pd
import pytest

from django.contrib.auth import get_user_model
from src.apps.ai_assistant.services import nlp_service as nlp_mod
from src.apps.ai_assistant.services.nlp_service import LocalNLPService

User = get_user_model()

@pytest.mark.django_db
def test_cash_flow_guidance_negative(monkeypatch):
    # Create a dummy user with company
    dummy_user = User.objects.create(username='dummy')

    # Monkeypatch the report generator to return a DF with diacritics and TL formatting
    def fake_gen(company, year, month):
        return pd.DataFrame([
            {'Net Nakit Akışı': '-12.345,67 TL', 'Dönem': f'{year}-{month:02d}'}
        ])

    # Patch the name as imported in the module under test
    monkeypatch.setattr(nlp_mod, 'generate_nakit_akisi_tablosu', fake_gen, raising=True)

    svc = LocalNLPService()
    out = svc.respond(dummy_user, 'Bu ay nakit akışı analizi')

    assert out['type'] == 'cash_flow'
    assert out['period'].endswith('-' + out['period'].split('-')[1])
    assert any('negatif' in g for g in out.get('guidance', []))

@pytest.mark.django_db
def test_cash_flow_guidance_zero_or_positive(monkeypatch):
    dummy_user = User.objects.create(username='dummy2')

    def fake_gen(company, year, month):
        return pd.DataFrame([
            {'Net Nakit Akışı (TL)': '0', 'Dönem': f'{year}-{month:02d}'},
            {'Net Nakit Akışı (TL)': '1.234,00', 'Dönem': f'{year}-{month:02d}'},
        ])

    monkeypatch.setattr(nlp_mod, 'generate_nakit_akisi_tablosu', fake_gen, raising=True)

    svc = LocalNLPService()
    out = svc.respond(dummy_user, 'geçen ay nakit akısı')

    assert out['type'] == 'cash_flow'
    assert out.get('guidance') == []

@pytest.mark.django_db
def test_period_parsing(monkeypatch):
    dummy_user = User.objects.create(username='dummy3')

    def fake_gen(company, year, month):
        return pd.DataFrame([
            {'Net Cash Flow': 1000, 'Period': f'{year}-{month:02d}'}
        ])

    monkeypatch.setattr(nlp_mod, 'generate_nakit_akisi_tablosu', fake_gen, raising=True)

    svc = LocalNLPService()
    out = svc.respond(dummy_user, '2024-03 nakit akışı')
    assert out['period'] == '2024-03'
