from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.cache import cache
import time
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """API rate limiting middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'RATE_LIMIT', 100)  # requests per minute
        self.window = 60  # 1 minute window

    def __call__(self, request):
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Create cache key
        key = f'rate_limit:{ip}'
        
        # Get current count
        count = cache.get(key, 0)
        
        if count >= self.rate_limit:
            logger.warning(f'Rate limit exceeded for IP: {ip}')
            return HttpResponseForbidden('Rate limit exceeded')
        
        # Increment count
        cache.set(key, count + 1, self.window)
        
        return self.get_response(request)

class SecurityHeadersMiddleware:
    """Security headers middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'"
        
        return response

class AuditLogMiddleware:
    """Audit logging middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start time
        start_time = time.time()
        
        # Get response
        response = self.get_response(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log audit
        self.log_audit(request, response, duration)
        
        return response
    
    def log_audit(self, request, response, duration):
        """Log audit information"""
        try:
            # Get user info
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            
            # Get request info
            method = request.method
            path = request.path
            status = response.status_code
            
            # Create audit log
            audit_log = {
                'timestamp': time.time(),
                'user': user,
                'method': method,
                'path': path,
                'status': status,
                'duration': duration,
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
            }
            
            # Log to file
            logger.info(json.dumps(audit_log))
            
        except Exception as e:
            logger.error(f'Error in audit logging: {str(e)}')

class DataMaskingMiddleware:
    """Data masking middleware for sensitive information"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_fields = ['password', 'token', 'api_key', 'credit_card']

    def __call__(self, request):
        # Mask sensitive data in request
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.mask_sensitive_data(request.data)
        
        response = self.get_response(request)
        
        # Mask sensitive data in response
        if hasattr(response, 'data'):
            self.mask_sensitive_data(response.data)
        
        return response
    
    def mask_sensitive_data(self, data):
        """Mask sensitive data in dictionary"""
        if isinstance(data, dict):
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    if isinstance(value, str):
                        data[key] = '*' * len(value)
                elif isinstance(value, (dict, list)):
                    self.mask_sensitive_data(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self.mask_sensitive_data(item) 