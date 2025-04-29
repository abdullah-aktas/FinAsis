# -*- coding: utf-8 -*-
"""
Rol tabanlı izin sistemi ve güvenlik iyileştirmeleri için modül.
"""

default_app_config = 'permissions.apps.PermissionsConfig'

# MVT yapısı için oluşturuldu

# Rol-İzin Haritası
# Her rol için izin verilen modüller ve eylemler
ROLE_PERMISSIONS_MAP = {
    # Admin tüm sistemde tam yetkili
    'admin': {
        'all': ['create', 'view', 'update', 'delete'],
    },
    
    # Genel Müdür yetkileri
    'manager': {
        'all': ['view'],
        'accounting': ['create', 'view', 'update', 'delete'],
        'finance': ['create', 'view', 'update', 'delete'],
        'crm': ['create', 'view', 'update', 'delete'],
        'stock': ['view', 'update'],
        'hr': ['view', 'update'],
        'reports': ['view'],
    },
    
    # Finans Müdürü yetkileri
    'finance_manager': {
        'accounting': ['create', 'view', 'update'],
        'finance': ['create', 'view', 'update', 'delete'],
        'crm': ['view', 'update'],
        'stock': ['view'],
        'reports': ['view'],
    },
    
    # Muhasebe yetkileri
    'accounting': {
        'accounting': ['create', 'view', 'update', 'delete'],
        'finance': ['view', 'update'],
        'crm': ['view'],
        'stock': ['view'],
        'reports': ['view'],
    },
    
    # Depo Yetkilisi izinleri
    'stock_operator': {
        'stock': ['create', 'view', 'update', 'delete'],
        'accounting': ['view'],
        'reports': ['view'],
    },
    
    # Satış Sorumlusu izinleri
    'sales': {
        'crm': ['create', 'view', 'update', 'delete'],
        'stock': ['view'],
        'finance': ['view'],
        'accounting': ['view'],
        'reports': ['view'],
    },
    
    # İnsan Kaynakları izinleri
    'hr': {
        'hr': ['create', 'view', 'update', 'delete'],
        'reports': ['view'],
    },
    
    # İşletme kullanıcısı izinleri
    'business': {
        'accounting': ['view'],
        'crm': ['view', 'update'],
        'stock': ['view'],
        'reports': ['view'],
    },
    
    # Öğrenci ve öğretmen rolleri (sanal şirket için)
    'student': {
        'virtual_company': ['create', 'view', 'update', 'delete'],
    },
    
    'teacher': {
        'virtual_company': ['create', 'view', 'update', 'delete'],
    },
    
    # Misafir kullanıcısı sınırlı izinler
    'guest': {
        'reports': ['view'],
    },
}

# Modül Bağımlılıkları
# Hangi modülün hangi modüle bağımlı olduğunu belirtir
MODULE_DEPENDENCIES = {
    'accounting': ['finance'],
    'finance': ['accounting'],
    'stock': ['accounting', 'finance'],
    'reports': ['accounting', 'finance', 'stock', 'crm', 'hr'],
}

# İzin Açıklamaları
PERMISSION_DESCRIPTIONS = {
    'create': 'Veri oluşturma yetkisi',
    'view': 'Veri görüntüleme yetkisi',
    'update': 'Veri güncelleme yetkisi',
    'delete': 'Veri silme yetkisi',
}

# Modül Açıklamaları
MODULE_DESCRIPTIONS = {
    'accounting': 'Muhasebe Modülü',
    'finance': 'Finans Yönetimi Modülü',
    'crm': 'Müşteri İlişkileri Modülü',
    'stock': 'Stok ve Depo Yönetimi Modülü',
    'hr': 'İnsan Kaynakları Modülü',
    'reports': 'Raporlama Modülü',
    'virtual_company': 'Sanal Şirket Modülü',
}

# Dış modüllerden import'ları buradan yapmıyoruz
# Django'nun app yükleme sürecinde sorun çıkardığı için
