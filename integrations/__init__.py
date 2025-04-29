# -*- coding: utf-8 -*-
# MVT yapıları için oluşturuldu

"""
Entegrasyon uygulamaları paketi.
Bu paket, farklı dış sistemlerle entegrasyonları içerir:
- E-Fatura/E-Arşiv entegrasyonu (efatura)
- Banka entegrasyonları (bank_integration)
- Diğer dış servis entegrasyonları (external, services)
"""

"""
FinAsis Entegrasyon Modülü

Bu modül, çeşitli e-ticaret platformları, ödeme sistemleri ve ERP sistemleri ile
entegrasyon sağlar.
"""

from .ecommerce.trendyol import TrendyolIntegration

__all__ = ['TrendyolIntegration']
