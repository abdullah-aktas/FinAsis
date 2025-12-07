import hashlib
import base64
import time
from django.conf import settings
import hmac


class PayTRClient:
    @staticmethod
    def _hash_token(
        merchant_id,
        user_ip,
        merchant_oid,
        email,
        payment_amount,
        user_basket_b64,
        no_installment,
        max_installment,
        currency,
        test_mode,
        merchant_salt,
        merchant_key,
    ):
        # PayTR token hesaplama
        data = f"{merchant_id}{user_ip}{merchant_oid}{email}{payment_amount}{user_basket_b64}{no_installment}{max_installment}{currency}{test_mode}"
        hmac_str = data + merchant_salt
        token = base64.b64encode(
            hashlib.sha256((hmac_str + merchant_key).encode("utf-8")).digest()
        ).decode("utf-8")
        return token

    @staticmethod
    def init_payment(payload: dict) -> dict:
        # Not: Gerçek entegrasyonda PayTR API'ye POST edilir. Burada iskelet dönüyoruz.
        # Dönüş: iframe_token veya redirect URL
        return {"status": "success", "iframe_token": "sandbox_token_example"}

    @staticmethod
    def verify_callback(
        merchant_oid: str,
        status: str,
        total_amount: str,
        hash_str: str,
        request_ip: str | None = None,
    ) -> bool:
        """PayTR server-to-server doğrulama.

        Doğrulama adımları:
        - (Opsiyonel) IP allowlist kontrolü (settings.PAYTR_ALLOWED_IPS)
        - PayTR hash eşleşmesi kontrolü
        """
        allowed_ips = getattr(settings, "PAYTR_ALLOWED_IPS", []) or []
        if allowed_ips and request_ip and request_ip not in allowed_ips:
            return False

        merchant_salt = getattr(settings, "PAYTR_MERCHANT_SALT", "")
        merchant_key = getattr(settings, "PAYTR_MERCHANT_KEY", "")
        if not (
            merchant_salt
            and merchant_key
            and merchant_oid
            and status
            and total_amount
            and hash_str
        ):
            return False

        # PayTR dokümantasyonuna göre geri dönüş hash'i oluşturma şekli.
        # Bazı örneklerde HMAC-SHA256( merchant_oid + merchant_salt + status + total_amount , merchant_key ) kullanılır.
        # Aşağıda HMAC-SHA256 ile base64 karşılaştırması yapılır.
        message = f"{merchant_oid}{merchant_salt}{status}{total_amount}".encode("utf-8")
        key = merchant_key.encode("utf-8")
        expected = base64.b64encode(
            hmac.new(key, message, hashlib.sha256).digest()
        ).decode("utf-8")
        # Bazı eski örneklerde salt+key dizgesel birleştirme kullanılabildiğinden, uyumluluk için ikincil bir kontrol daha yapıyoruz.
        if expected == hash_str:
            return True
        fallback = base64.b64encode(
            hashlib.sha256(
                (
                    f"{merchant_oid}{merchant_salt}{status}{total_amount}"
                    + merchant_key
                ).encode("utf-8")
            ).digest()
        ).decode("utf-8")
        return fallback == hash_str


class RefGenerator:
    @staticmethod
    def bank_reference(prefix: str = "HVL") -> str:
        import random

        return f"{prefix}{int(time.time())}{random.randint(100,999)}"
