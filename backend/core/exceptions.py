# -*- coding: utf-8 -*-
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # REST framework'in varsayılan exception handler'ını çağır
    response = exception_handler(exc, context)

    if response is None:
        # Eğer response None ise, özel exception'ları işle
        if isinstance(exc, ValidationError):
            response = Response(
                {
                    "error": {
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": str(exc),
                        "type": "validation_error"
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            response = Response(
                {
                    "error": {
                        "code": status.HTTP_409_CONFLICT,
                        "message": "Database integrity error occurred",
                        "type": "integrity_error"
                    }
                },
                status=status.HTTP_409_CONFLICT
            )
        else:
            # Bilinmeyen hatalar için
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            response = Response(
                {
                    "error": {
                        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "message": "Internal server error",
                        "type": "server_error"
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return response 