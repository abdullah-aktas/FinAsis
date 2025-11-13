from django.utils.deprecation import MiddlewareMixin
from .models import Tenant

class CurrentTenantMiddleware(MiddlewareMixin):
    HEADER_NAME = 'HTTP_X_TENANT'

    def process_request(self, request):
        tenant_code = request.META.get(self.HEADER_NAME)
        if not tenant_code:
            # Try subdomain: tenant.example.com
            host = request.get_host().split(':')[0]
            parts = host.split('.')
            if len(parts) > 2:  # e.g., tenant.domain.com
                tenant_code = parts[0]
        request.tenant = None
        if tenant_code:
            try:
                request.tenant = Tenant.objects.get(code=tenant_code)
            except Tenant.DoesNotExist:
                pass
        return None
