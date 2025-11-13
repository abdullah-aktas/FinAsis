# -*- coding: utf-8 -*-
"""
FinQuest 3D - Game entry

Bu modül, Ursina tabanlı oyunun halka açık giriş noktasını sağlar.
Şimdilik mevcut uygulama `ursina_game/ticaretin_izinde_3d.py` dosyasındaki
TicaretinIzinde3D sınıfını kullanır. İleride oyun modülleri bu dizine
parçalanarak taşınacaktır.
"""
from __future__ import annotations

try:
    # Tercih edilen yol: ayrı finquest modülünden içe aktarım
    # (Gelecekte doğrudan burada tanımlanacak.)
    from games.ticaretin_izinde.ticaretin_izinde_3d import TicaretinIzinde3D  # noqa: F401
except Exception as e:  # pragma: no cover
    # Dağıtım ortamı farklı dizin düzenlerine sahip olabilir; son çare olarak tekrar dene
    try:
        from ..ticaretin_izinde.ticaretin_izinde_3d import TicaretinIzinde3D  # type: ignore # noqa: F401
    except Exception as inner:
        raise

# İsim uyumu için alternatif bir takma ad sağlayalım
FinQuestGame = TicaretinIzinde3D

# Yeni modüller
from .vr import VRManager
from .nft import NFTManager
from .ai_npc import TradeBot, create_npcs
from .worldgen import WorldGenerator, generate_worlds

class FinQuestDemo:
    def __init__(self):
        self.vr = VRManager()
        self.nft = NFTManager()
        self.npcs = create_npcs(['Mardin', 'Izmir', 'Corum'])
        self.worlds = generate_worlds(['Mardin', 'Izmir', 'Corum'])

    def toggle_vr(self):
        if self.vr.enabled:
            self.vr.disable()
        else:
            self.vr.enable()
        return self.vr.status()

    def mint_demo_nft(self, owner='demo_player'):
        return self.nft.mint('Demo NFT', owner)

    def get_demo_nfts(self, owner='demo_player'):
        return self.nft.get_nfts(owner)

    def npc_decisions(self, price, volume):
        return [npc.analyze_market(price, volume) for npc in self.npcs]

    def get_world_map(self, idx=0):
        return self.worlds[idx].map
