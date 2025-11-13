# -*- coding: utf-8 -*-
"""
FinQuest 3D - Quests module

Bu modül, oyundaki görevleri oluşturan yardımcı fonksiyonları içerir.
Mevcut Ursina sınıfıyla (TicaretinIzinde3D) çalışacak şekilde tasarlanmıştır.
"""
from __future__ import annotations
from typing import Dict, Any


def create_quests(game: Any) -> Dict[str, list]:
    """Verilen oyun nesnesi (self) için görevleri üretir.

    game: self benzeri; game.game_state ve game.check_diverse_inventory beklenir.
    """
    quests = {
        'tutorial': [
            {
                'id': 'market_visit',
                'title': 'Market Ziyareti',
                'description': 'Marketi ziyaret edin ve bir ürün satın alın.',
                'reward': {'money': 100, 'exp': 10},
                'completion_criteria': lambda: 'marketi_ziyaret_etti' in game.game_state
            },
            {
                'id': 'bank_visit',
                'title': 'Banka Ziyareti',
                'description': 'Bankayı ziyaret edin ve hesap bilgilerinizi kontrol edin.',
                'reward': {'money': 50, 'exp': 10},
                'completion_criteria': lambda: 'bankayi_ziyaret_etti' in game.game_state
            }
        ],
        'trading': [
            {
                'id': 'first_sale',
                'title': 'İlk Satış',
                'description': 'Bir ürün satın alın ve kârla satın.',
                'reward': {'money': 200, 'exp': 20},
                'completion_criteria': lambda: 'ilk_satisi_yapti' in game.game_state
            },
            {
                'id': 'diverse_inventory',
                'title': 'Çeşitli Envanter',
                'description': 'En az 3 farklı kategoriden ürün satın alın.',
                'reward': {'money': 300, 'exp': 30},
                'completion_criteria': lambda: game.check_diverse_inventory()
            }
        ],
        'accounting': [
            {
                'id': 'income_statement',
                'title': 'Gelir Tablosu',
                'description': 'Gelir tablosunu oluşturun ve 1 haftalık kâr-zarar durumunuzu görün.',
                'reward': {'money': 500, 'exp': 50},
                'completion_criteria': lambda: 'gelir_tablosu_olusturuldu' in game.game_state
            },
            {
                'id': 'balance_sheet',
                'title': 'Bilanço',
                'description': 'Şirketinizin bilançosunu oluşturun.',
                'reward': {'money': 500, 'exp': 50},
                'completion_criteria': lambda: 'bilanco_olusturuldu' in game.game_state
            }
        ]
    }

    age_group = game.game_state['player']['age_group']
    if age_group == 'child':
        quests['special'] = [
            {
                'id': 'piggy_bank',
                'title': 'Kumbara',
                'description': 'Para biriktirmeyi öğrenin, 1000 TL biriktirin.',
                'reward': {'money': 100, 'exp': 10},
                'completion_criteria': lambda: game.game_state['player']['money'] >= 1000
            }
        ]
    elif age_group == 'teen':
        quests['special'] = [
            {
                'id': 'budget_plan',
                'title': 'Bütçe Planı',
                'description': 'Haftalık bütçe planı oluşturun ve ona bağlı kalın.',
                'reward': {'money': 200, 'exp': 20},
                'completion_criteria': lambda: 'butce_plani_olusturuldu' in game.game_state
            }
        ]
    elif age_group == 'adult':
        quests['special'] = [
            {
                'id': 'investment',
                'title': 'Yatırım',
                'description': 'Bir yatırım aracına yatırım yapın.',
                'reward': {'money': 500, 'exp': 50},
                'completion_criteria': lambda: 'yatirim_yapti' in game.game_state
            }
        ]
    elif age_group == 'senior':
        quests['special'] = [
            {
                'id': 'retirement_plan',
                'title': 'Emeklilik Planı',
                'description': 'Emeklilik gelir stratejisi oluşturun.',
                'reward': {'money': 1000, 'exp': 100},
                'completion_criteria': lambda: 'emeklilik_plani_olusturuldu' in game.game_state
            }
        ]

    return quests
