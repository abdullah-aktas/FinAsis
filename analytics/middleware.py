from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger(__name__)

class AnalyticsErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if request.path.startswith('/analytics/'):
            if isinstance(exception, PermissionDenied):
                return JsonResponse({
                    'error': 'Bu işlem için yetkiniz bulunmamaktadır.',
                    'code': 'permission_denied'
                }, status=403)
            elif isinstance(exception, APIException):
                return JsonResponse({
                    'error': str(exception),
                    'code': exception.get_codes()
                }, status=exception.status_code)
            else:
                logger.error(f"Analitik hatası: {str(exception)}", exc_info=True)
                return JsonResponse({
                    'error': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.',
                    'code': 'internal_error'
                }, status=500)
        return None 