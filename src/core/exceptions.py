"""
Özel istisna sınıfları.
Bu modül, proje genelinde kullanılacak özel istisna sınıflarını içerir.
"""

class FinAsisException(Exception):
    """Temel FinAsis istisna sınıfı."""
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)

class ValidationError(FinAsisException):
    """Doğrulama hatası."""
    def __init__(self, message, field=None, value=None):
        super().__init__(
            message=message,
            code='validation_error',
            details={'field': field, 'value': value}
        )

class AuthenticationError(FinAsisException):
    """Kimlik doğrulama hatası."""
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='authentication_error',
            details=details
        )

class AuthorizationError(FinAsisException):
    """Yetkilendirme hatası."""
    def __init__(self, message, required_permissions=None):
        super().__init__(
            message=message,
            code='authorization_error',
            details={'required_permissions': required_permissions}
        )

class ResourceNotFoundError(FinAsisException):
    """Kaynak bulunamadı hatası."""
    def __init__(self, resource_type, resource_id):
        super().__init__(
            message=f"{resource_type} with id {resource_id} not found",
            code='resource_not_found',
            details={'resource_type': resource_type, 'resource_id': resource_id}
        )

class BusinessLogicError(FinAsisException):
    """İş mantığı hatası."""
    def __init__(self, message, operation=None, context=None):
        super().__init__(
            message=message,
            code='business_logic_error',
            details={'operation': operation, 'context': context}
        )

class ExternalServiceError(FinAsisException):
    """Harici servis hatası."""
    def __init__(self, service_name, error_message, status_code=None):
        super().__init__(
            message=f"Error in {service_name}: {error_message}",
            code='external_service_error',
            details={'service_name': service_name, 'status_code': status_code}
        )

class RateLimitError(FinAsisException):
    """İstek sınırı aşımı hatası."""
    def __init__(self, limit, window):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}",
            code='rate_limit_error',
            details={'limit': limit, 'window': window}
        )

class DatabaseError(FinAsisException):
    """Veritabanı hatası."""
    def __init__(self, operation, error_message):
        super().__init__(
            message=f"Database error during {operation}: {error_message}",
            code='database_error',
            details={'operation': operation}
        )

class CacheError(FinAsisException):
    """Önbellek hatası."""
    def __init__(self, operation, error_message):
        super().__init__(
            message=f"Cache error during {operation}: {error_message}",
            code='cache_error',
            details={'operation': operation}
        ) 