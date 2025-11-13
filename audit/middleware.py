class AuditRequestMetaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_ip = request.META.get('REMOTE_ADDR')
        request.request_ua = request.META.get('HTTP_USER_AGENT', '')
        return self.get_response(request)
