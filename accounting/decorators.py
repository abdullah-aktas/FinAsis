# Transaction management decorators for accounting operations
from functools import wraps
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


def atomic_with_rollback_logging(func):
    """
    Atomic transaction decorator with rollback logging.
    Ensures database consistency and logs rollback scenarios.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                result = func(*args, **kwargs)
                return result
        except Exception as e:
            logger.error(
                f"Transaction rolled back in {func.__name__}: {str(e)}",
                exc_info=True,
                extra={
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200],
                }
            )
            raise
    return wrapper


def validate_balance_before_commit(func):
    """
    Validates that journal entries are balanced before committing.
    Used for voucher creation and updates.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            result = func(*args, **kwargs)
            
            # If result is a voucher-like object, validate balance
            if hasattr(result, 'is_balanced') and not result.is_balanced:
                raise ValidationError(
                    f"Voucher is not balanced. Cannot commit transaction."
                )
            
            return result
    return wrapper


def retry_on_deadlock(max_retries=3):
    """
    Retry decorator for handling database deadlocks.
    Useful for high-concurrency operations.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from django.db.utils import OperationalError
            
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        return func(*args, **kwargs)
                except OperationalError as e:
                    if 'deadlock' in str(e).lower() and attempt < max_retries - 1:
                        logger.warning(
                            f"Deadlock detected in {func.__name__}, "
                            f"retrying ({attempt + 1}/{max_retries})..."
                        )
                        continue
                    raise
            
        return wrapper
    return decorator


def ensure_company_context(func):
    """
    Ensures company context is set before operation.
    Prevents cross-company data leakage.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'company') or not request.user.company:
            raise ValidationError("No company context found for user.")
        return func(request, *args, **kwargs)
    return wrapper
