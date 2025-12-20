"""
Cloudflare Middleware
Gerçek kullanıcı IP'sini Cloudflare header'larından alır.
"""
from django.utils.deprecation import MiddlewareMixin


class CloudflareRealIPMiddleware(MiddlewareMixin):
    """
    Cloudflare üzerinden gelen isteklerde gerçek kullanıcı IP'sini alır.
    
    Cloudflare, gerçek kullanıcı IP'sini CF-Connecting-IP header'ında gönderir.
    Bu middleware, REMOTE_ADDR'ı gerçek IP ile değiştirir.
    """

    def process_request(self, request):
        """
        Cloudflare header'larından gerçek IP'yi al ve request'e ekle.
        """
        # Cloudflare gerçek IP'si
        cf_connecting_ip = request.META.get("HTTP_CF_CONNECTING_IP")
        if cf_connecting_ip:
            # Gerçek IP'yi request'e ekle
            request.META["REMOTE_ADDR"] = cf_connecting_ip
            request.META["CF_CONNECTING_IP"] = cf_connecting_ip

        # Cloudflare diğer header'ları
        cf_ray = request.META.get("HTTP_CF_RAY")
        if cf_ray:
            request.META["CF_RAY"] = cf_ray

        cf_visitor = request.META.get("HTTP_CF_VISITOR")
        if cf_visitor:
            request.META["CF_VISITOR"] = cf_visitor

        cf_country = request.META.get("HTTP_CF_IPCOUNTRY")
        if cf_country:
            request.META["CF_IPCOUNTRY"] = cf_country

        return None


def get_real_ip(request):
    """
    Request'ten gerçek IP'yi alır.
    Cloudflare varsa CF-Connecting-IP, yoksa REMOTE_ADDR kullanır.
    """
    # Cloudflare gerçek IP'si
    cf_ip = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf_ip:
        return cf_ip

    # X-Forwarded-For (diğer proxy'ler için)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # İlk IP'yi al (proxy chain'de ilk gerçek IP)
        return x_forwarded_for.split(",")[0].strip()

    # Varsayılan
    return request.META.get("REMOTE_ADDR", "unknown")


def get_cloudflare_country(request):
    """
    Cloudflare'den gelen ülke bilgisini alır.
    """
    return request.META.get("HTTP_CF_IPCOUNTRY", "unknown")


def is_cloudflare_request(request):
    """
    İsteğin Cloudflare üzerinden gelip gelmediğini kontrol eder.
    """
    return "HTTP_CF_CONNECTING_IP" in request.META or "HTTP_CF_RAY" in request.META

