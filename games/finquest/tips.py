# -*- coding: utf-8 -*-
"""
FinQuest 3D - Financial tips module
"""
from __future__ import annotations
from typing import Dict


def load_financial_tips() -> Dict[str, list]:
    return {
        "accounting": [
            "Muhasebe, işletmenin finansal işlemlerini kaydetme, sınıflandırma ve raporlama sürecidir.",
            "Bilanço, işletmenin varlıklarını ve bu varlıkların kaynaklarını gösteren finansal tablodur.",
            "Gelir tablosu, işletmenin belirli bir dönemdeki gelir ve giderlerini gösteren finansal tablodur.",
            "Çift taraflı kayıt sistemi, her işlem için en az iki hesabı etkiler (borç ve alacak).",
        ],
        "trading": [
            "Alış fiyatına kâr marjı ekleyerek satış fiyatını belirlemelisiniz.",
            "Talep yüksekken satın alıp, talep düşükken satmak zarar etmenize neden olabilir.",
            "Stok devir hızı, envanterinizin ne kadar hızlı satıldığını gösterir.",
            "Nakit akışı yönetimi, işletmenizin hayatta kalması için kritik öneme sahiptir.",
        ],
        "banking": [
            "Bileşik faiz, paranızın zaman içinde büyümesini sağlar.",
            "Kredi, işletme sermayenizi artırmanın bir yoludur, ancak geri ödeme planını dikkatlice değerlendirin.",
            "Yatırım çeşitlendirmesi, riski azaltmanın ve potansiyel getiriyi artırmanın bir yoludur.",
            "Banka kredisi kullanırken faiz oranları ve vade süresi önemli faktörlerdir.",
        ],
    }
