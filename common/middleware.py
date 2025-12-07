from django.utils.deprecation import MiddlewareMixin
from .logging import set_request_context, generate_request_id


class RequestContextLoggingMiddleware(MiddlewareMixin):
    """Populate per-request logging context (request_id, tenant, user, path)."""

    def process_request(self, request):
        rid = generate_request_id()
        request.request_id = rid
        tenant = getattr(request, "tenant", None)
        set_request_context(
            rid, tenant=tenant, user=getattr(request, "user", None), path=request.path
        )

    def process_response(self, request, response):
        # Clear context (best effort)
        set_request_context()
        return response

    def process_exception(self, request, exception):  # noqa: D401
        # Context already set; let logging capture exception.
        pass
