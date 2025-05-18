# -*- coding: utf-8 -*-
from drf_yasg import openapi

test_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING, description='İşlem durumu'),
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='İşlem mesajı'),
        'timestamp': openapi.Schema(type=openapi.TYPE_NUMBER, description='İşlem zamanı'),
        'request_info': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'method': openapi.Schema(type=openapi.TYPE_STRING, description='HTTP metodu'),
                'path': openapi.Schema(type=openapi.TYPE_STRING, description='İstek yolu'),
                'user_agent': openapi.Schema(type=openapi.TYPE_STRING, description='Kullanıcı ajanı'),
                'ip': openapi.Schema(type=openapi.TYPE_STRING, description='IP adresi'),
            }
        )
    }
)

health_check_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Sistem durumu'),
        'timestamp': openapi.Schema(type=openapi.TYPE_NUMBER, description='Kontrol zamanı'),
        'services': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'database': openapi.Schema(type=openapi.TYPE_STRING, description='Veritabanı durumu'),
                'cache': openapi.Schema(type=openapi.TYPE_STRING, description='Önbellek durumu'),
                'auth': openapi.Schema(type=openapi.TYPE_STRING, description='Kimlik doğrulama durumu'),
            }
        )
    }
)

performance_test_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Test durumu'),
        'execution_time': openapi.Schema(type=openapi.TYPE_NUMBER, description='Çalışma süresi'),
        'result': openapi.Schema(type=openapi.TYPE_NUMBER, description='Test sonucu'),
    }
) 