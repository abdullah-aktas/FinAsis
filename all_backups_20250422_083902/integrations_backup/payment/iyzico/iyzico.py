from typing import Any, Dict
import iyzipay
from ...base.base_integration import BaseIntegration

class IyzicoIntegration(BaseIntegration):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = config.get('api_url', 'https://sandbox-api.iyzipay.com')
        self._setup_options()
    
    def _setup_options(self):
        """İyzico API seçeneklerini yapılandırır"""
        self.options = {
            'api_key': self.api_key,
            'secret_key': self.access_token,
            'base_url': self.api_url
        }
    
    async def authenticate(self) -> bool:
        """İyzico API kimlik doğrulaması"""
        try:
            # Test ödemesi ile kimlik doğrulaması
            request = {
                'locale': 'tr',
                'conversationId': 'test-auth',
                'price': '1',
                'paidPrice': '1.2',
                'currency': 'TRY',
                'basketId': 'B67832',
                'paymentGroup': 'PRODUCT',
                'callbackUrl': 'https://merchant.com/callback',
                'enabledInstallments': [1, 2, 3, 6, 9],
                'buyer': {
                    'id': 'BY789',
                    'name': 'John',
                    'surname': 'Doe',
                    'email': 'email@email.com',
                    'identityNumber': '74300864791',
                    'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
                    'ip': '85.34.78.112',
                    'city': 'Istanbul',
                    'country': 'Turkey'
                },
                'shippingAddress': {
                    'contactName': 'Jane Doe',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1'
                },
                'billingAddress': {
                    'contactName': 'Jane Doe',
                    'city': 'Istanbul',
                    'country': 'Turkey',
                    'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1'
                },
                'basketItems': [
                    {
                        'id': 'BI101',
                        'name': 'Samsung S10',
                        'category1': 'Phones',
                        'itemType': 'PHYSICAL',
                        'price': '1'
                    }
                ]
            }
            checkout_form = iyzipay.CheckoutFormInitialize().create(request, self.options)
            return checkout_form.status == 'success'
        except Exception as e:
            self.log_sync("error", f"Authentication error: {str(e)}")
            return False
    
    async def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """3D Secure ödeme formu oluşturur"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': payment_data.get('conversation_id'),
                'price': payment_data.get('price'),
                'paidPrice': payment_data.get('paid_price'),
                'currency': payment_data.get('currency', 'TRY'),
                'basketId': payment_data.get('basket_id'),
                'paymentGroup': 'PRODUCT',
                'callbackUrl': payment_data.get('callback_url'),
                'enabledInstallments': [1, 2, 3, 6, 9],
                'buyer': payment_data.get('buyer'),
                'shippingAddress': payment_data.get('shipping_address'),
                'billingAddress': payment_data.get('billing_address'),
                'basketItems': payment_data.get('basket_items')
            }
            
            checkout_form = iyzipay.CheckoutFormInitialize().create(request, self.options)
            return {
                'status': checkout_form.status,
                'paymentId': checkout_form.paymentId,
                'paymentPageUrl': checkout_form.paymentPageUrl
            }
        except Exception as e:
            raise Exception(f"Payment creation error: {str(e)}")
    
    async def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Ödeme durumunu kontrol eder"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': f'check-{payment_id}',
                'paymentId': payment_id
            }
            
            result = iyzipay.CheckoutForm().retrieve(request, self.options)
            return {
                'status': result.status,
                'paymentStatus': result.paymentStatus,
                'fraudStatus': result.fraudStatus,
                'merchantCommissionRate': result.merchantCommissionRate,
                'merchantCommissionRateAmount': result.merchantCommissionRateAmount,
                'iyziCommissionRateAmount': result.iyziCommissionRateAmount,
                'iyziCommissionFee': result.iyziCommissionFee,
                'cardType': result.cardType,
                'cardAssociation': result.cardAssociation,
                'cardFamily': result.cardFamily,
                'binNumber': result.binNumber,
                'lastFourDigits': result.lastFourDigits
            }
        except Exception as e:
            raise Exception(f"Payment status check error: {str(e)}")
    
    async def refund_payment(self, payment_id: str, amount: float) -> Dict[str, Any]:
        """Ödeme iadesi yapar"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': f'refund-{payment_id}',
                'paymentTransactionId': payment_id,
                'price': str(amount),
                'currency': 'TRY',
                'ip': '85.34.78.112'
            }
            
            result = iyzipay.Refund().create(request, self.options)
            return {
                'status': result.status,
                'paymentId': result.paymentId,
                'price': result.price,
                'currency': result.currency
            }
        except Exception as e:
            raise Exception(f"Refund error: {str(e)}")
    
    async def handle_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Webhook isteklerini işler"""
        event_type = data.get("eventType")
        if event_type == "payment.success":
            return await self._handle_successful_payment(data)
        elif event_type == "payment.failed":
            return await self._handle_failed_payment(data)
        return {"status": "error", "message": "Unknown event type"}
    
    async def _handle_successful_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Başarılı ödeme webhook'unu işler"""
        payment_id = data.get("paymentId")
        # Muhasebe fişi oluştur
        # Sipariş durumunu güncelle
        return {"status": "success", "payment_id": payment_id}
    
    async def _handle_failed_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Başarısız ödeme webhook'unu işler"""
        payment_id = data.get("paymentId")
        error_message = data.get("errorMessage")
        # Hata logunu kaydet
        # Sipariş durumunu güncelle
        return {"status": "error", "payment_id": payment_id, "error": error_message} 