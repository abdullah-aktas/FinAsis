#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FinQuest 3D
-----------
Finansal Eğitim Simülasyon Oyunu

Bu oyun, finansal okuryazarlık geliştirmek için tasarlanmış
eğitici bir 3D ticaret simülasyonudur.
"""

import os
import sys
import argparse

# Text sınıfında raw_text hatası için monkey patch
def patch_ursina_text():
    try:
        from ursina import Text
        # Orijinal init metodunu kaydet
        original_init = Text.__init__
        
        # Text sınıfını patch et
        def patched_init(self, *args, **kwargs):
            # wordwrap parametresini kaldır, daha sonra ayarlanacak
            if 'wordwrap' in kwargs:
                kwargs.pop('wordwrap')
            # Orijinal init çağır
            original_init(self, *args, **kwargs)
            
        # Text sınıfının init metodunu değiştir
        Text.__init__ = patched_init
        print("Ursina Text sınıfı başarıyla patch edildi.")
    except ImportError:
        print("Ursina Text sınıfı import edilemedi.")
    except Exception as e:
        print(f"Text sınıfı patch edilirken hata oluştu: {e}")

def run_game():
    """Oyunu başlat"""
    # Text sınıfını patch et (raw_text hatası için)
    patch_ursina_text()
    
    # Proje dizinini sys.path'e ekle
    # * mutlak importlarını çözebilmek için hem 'src' klasörünün ebeveynini
    # hem de mevcut klasörün üst dizinlerini ekleyelim.
    here = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.abspath(os.path.join(here, '..', '..', '..')),     # src/apps/games
        os.path.abspath(os.path.join(here, '..', '..', '..', '..', '..')),  # FinAsis (src'nın ebeveyni)
    ]
    for p in candidates:
        if p not in sys.path and os.path.isdir(p):
            sys.path.append(p)
    
    # Ursina Engine değişken atamaları (ikon hatasını önle)
    os.environ['URSINA_ICON_PATH'] = 'None'
    
    # Ursina Engine oyununu import et (FinQuest modülü üzerinden)
    from games.finquest.game import TicaretinIzinde3D

    # Oyunu başlat
    game = TicaretinIzinde3D()

    # Pause/Resume için kontrol dosyasını izle (oyun içinde global pause toggling)
    # application.paused özniteliği yoksa sessizce yoksayılır
    try:
        import threading
        from ursina import application
        from pathlib import Path
        import json as _json
        import time as _time

        ctrl_path = Path(__file__).resolve().parent / 'control.json'
        state = {'paused': False}

        def _watch_control():
            last = None
            while True:
                try:
                    if ctrl_path.exists():
                        data = _json.loads(ctrl_path.read_text(encoding='utf-8') or '{}')
                        paused = bool(data.get('paused', False))
                        if paused != last:
                            try:
                                setattr(application, 'paused', paused)
                            except Exception:
                                pass
                            last = paused
                    else:
                        if last:
                            try:
                                setattr(application, 'paused', False)
                            except Exception:
                                pass
                            last = False
                except Exception:
                    # İzleyici hiçbir zaman oyunu çökertmemeli
                    pass
                _time.sleep(0.5)

        t = threading.Thread(target=_watch_control, daemon=True)
        t.start()
    except Exception:
        pass

if __name__ == "__main__":
    # Komut satırı argümanlarını işle
    parser = argparse.ArgumentParser(description="FinQuest 3D Oyunu")
    parser.add_argument('--fullscreen', action='store_true', help='Tam ekran modunda başlat')
    parser.add_argument('--age', choices=['child', 'teen', 'adult', 'senior'], 
                       help='Başlangıç yaş grubu (child:5-12, teen:13-18, adult:19-65, senior:65+)')
    parser.add_argument('--character', choices=['businessman', 'student', 'teacher', 'retiree'],
                       help='Başlangıç karakteri')
    
    args = parser.parse_args()
    
    # Oyunu başlat
    run_game() 