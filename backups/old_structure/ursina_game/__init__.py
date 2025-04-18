"""
FinAsis 3D Ticaret Simülasyonu

Bu modül, Ursina Engine kullanılarak geliştirilmiş finansal eğitim simülasyonunu içerir.
Kullanıcılar 3D ortamda borsa ve yatırım kavramlarını interaktif bir şekilde öğrenebilirler.

Özellikler:
- 3D borsa ortamında gezinme
- Gerçek zamanlı hisse senedi alım satımı
- Finansal danışman ile etkileşim
- Dinamik piyasa simülasyonu
- Portföy yönetim arayüzü
"""

from .game import run_game

__all__ = ['run_game']