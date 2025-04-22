"""
Güvenlik middleware'leri.
"""
import ipaddress
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone

logger = logging.getLogger('security')


class IPRestrictionMiddleware:
    """
    IP kısıtlamaları uygulayan middleware.
    
    Bu middleware, belirli IP adreslerini veya IP aralıklarını kısıtlar.
    settings.RESTRICTED_IPS ve settings.ALLOWED_IPS listeleri ile yapılandırılır.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Kısıtlı IP'ler ve izin verilen IP'ler
        self.restricted_ips = getattr(settings, 'RESTRICTED_IPS', [])
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])
        
        # IP ağ nesnelerini önceden oluştur
        self.restricted_networks = []
        self.allowed_networks = []
        
        for ip_str in self.restricted_ips:
            try:
                if '/' in ip_str:
                    self.restricted_networks.append(ipaddress.ip_network(ip_str, strict=False))
                else:
                    self.restricted_networks.append(ipaddress.ip_address(ip_str))
            except ValueError:
                logger.warning(f"Geçersiz IP adresi formatı: {ip_str}")
        
        for ip_str in self.allowed_ips:
            try:
                if '/' in ip_str:
                    self.allowed_networks.append(ipaddress.ip_network(ip_str, strict=False))
                else:
                    self.allowed_networks.append(ipaddress.ip_address(ip_str))
            except ValueError:
                logger.warning(f"Geçersiz IP adresi formatı: {ip_str}")
    
    def __call__(self, request):
        # IP adresini al
        client_ip_str = self._get_client_ip(request)
        
        try:
            client_ip = ipaddress.ip_address(client_ip_str)
            
            # İzin verilen IP kontrolü
            if self.allowed_networks:
                is_allowed = False
                for network in self.allowed_networks:
                    if isinstance(network, ipaddress.IPv4Network) or isinstance(network, ipaddress.IPv6Network):
                        if client_ip in network:
                            is_allowed = True
                            break
                    elif client_ip == network:
                        is_allowed = True
                        break
                
                if not is_allowed:
                    logger.warning(f"İzin verilmeyen IP erişimi: {client_ip_str}")
                    return HttpResponseForbidden("Bu IP adresinden erişime izin verilmiyor.")
            
            # Kısıtlı IP kontrolü
            for network in self.restricted_networks:
                if isinstance(network, ipaddress.IPv4Network) or isinstance(network, ipaddress.IPv6Network):
                    if client_ip in network:
                        logger.warning(f"Kısıtlı IP erişim girişimi: {client_ip_str}")
                        return HttpResponseForbidden("Bu IP adresinden erişim kısıtlanmıştır.")
                elif client_ip == network:
                    logger.warning(f"Kısıtlı IP erişim girişimi: {client_ip_str}")
                    return HttpResponseForbidden("Bu IP adresinden erişim kısıtlanmıştır.")
                
        except ValueError:
            logger.warning(f"Geçersiz IP adresi: {client_ip_str}")
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        """
        İstemci IP adresini döndürür.
        X-Forwarded-For, proxy-client-ip gibi headerlar dikkate alınır.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For başlığı birden fazla IP içerebilir,
            # genellikle ilk IP gerçek istemci IP'sidir
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class BruteForceProtectionMiddleware:
    """
    Brute-force saldırılarına karşı koruma sağlayan middleware.
    
    Bu middleware, belirli endpoint'lere yapılan fazla sayıda başarısız 
    giriş denemelerini izler ve geçici olarak IP adresini engeller.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Brute-force koruma ayarları
        self.max_login_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
        self.block_time_minutes = getattr(settings, 'LOGIN_BLOCK_TIME_MINUTES', 15)
        self.tracked_urls = getattr(settings, 'BRUTE_FORCE_PROTECTED_URLS', [
            '/api/token/',  # Token endpointi
            '/accounts/login/',  # Login sayfası
            '/admin/login/',  # Admin login
        ])
    
    def __call__(self, request):
        # Sadece POST isteklerini ve korunan URL'leri kontrol et
        if request.method == 'POST' and any(request.path.startswith(url) for url in self.tracked_urls):
            client_ip = self._get_client_ip(request)
            cache_key = f'login_attempts:{client_ip}'
            
            # IP'nin bloke edilip edilmediğini kontrol et
            if cache.get(f'blocked:{client_ip}'):
                block_time = cache.get(f'block_time:{client_ip}')
                logger.warning(f"Engellenen IP adresinden erişim girişimi: {client_ip}")
                return HttpResponseForbidden(
                    f"Çok fazla başarısız giriş denemesi. Hesabınız geçici olarak kilitlendi. "
                    f"Lütfen {block_time} dakika sonra tekrar deneyin."
                )
            
            # İsteği işle
            response = self.get_response(request)
            
            # Başarısız giriş denemeleri için 400 ve 401 yanıtları kontrol et
            if response.status_code in [400, 401]:
                # Başarısız giriş denemesi sayacını artır
                attempts = cache.get(cache_key, 0) + 1
                cache.set(cache_key, attempts, 60 * 60)  # 1 saat süreyle sakla
                
                # Maksimum deneme sayısı aşıldıysa IP'yi engelle
                if attempts >= self.max_login_attempts:
                    cache.set(f'blocked:{client_ip}', True, 60 * self.block_time_minutes)
                    cache.set(f'block_time:{client_ip}', self.block_time_minutes, 60 * self.block_time_minutes)
                    logger.warning(f"IP adresi engellendi (brute-force): {client_ip}")
                    
                    # Kullanıcı veritabanında da güncelleme yapmak için response'u değiştir
                    return HttpResponseForbidden(
                        f"Çok fazla başarısız giriş denemesi. Hesabınız geçici olarak kilitlendi. "
                        f"Lütfen {self.block_time_minutes} dakika sonra tekrar deneyin."
                    )
            
            # Başarılı giriş için sayacı sıfırla (200 OK)
            elif response.status_code == 200 or response.status_code == 302:  # 302 genellikle başarılı girişten sonra yönlendirme
                cache.delete(cache_key)
            
            return response
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        """
        İstemci IP adresini döndürür.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 