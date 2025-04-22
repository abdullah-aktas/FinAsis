#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FinAsis - Ticaretin İzinde 3D
------------------------------
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
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    sys.path.append(project_root)
    
    # Ursina Engine değişken atamaları (ikon hatasını önle)
    os.environ['URSINA_ICON_PATH'] = 'None'
    
    # Ursina Engine oyununu import et
    from ticaretin_izinde_3d import TicaretinIzinde3D
    
    # Oyunu başlat
    game = TicaretinIzinde3D()

if __name__ == "__main__":
    # Komut satırı argümanlarını işle
    parser = argparse.ArgumentParser(description="FinAsis - Ticaretin İzinde 3D Oyunu")
    parser.add_argument('--fullscreen', action='store_true', help='Tam ekran modunda başlat')
    parser.add_argument('--age', choices=['child', 'teen', 'adult', 'senior'], 
                       help='Başlangıç yaş grubu (child:5-12, teen:13-18, adult:19-65, senior:65+)')
    parser.add_argument('--character', choices=['businessman', 'student', 'teacher', 'retiree'],
                       help='Başlangıç karakteri')
    
    args = parser.parse_args()
    
    # Oyunu başlat
    run_game() 