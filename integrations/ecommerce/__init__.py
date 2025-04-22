"""
E-ticaret Platform Entegrasyonları

Bu modül, çeşitli e-ticaret platformları ile entegrasyon sağlar:
- Trendyol
- Hepsiburada
- Shopify
- WooCommerce
- Magento
"""

from .trendyol import TrendyolIntegration

__all__ = ['TrendyolIntegration'] 