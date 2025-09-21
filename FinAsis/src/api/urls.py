from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["GET"])  # API v1 root
def api_index(_request):
    return Response({
        "name": "FinAsis API",
        "version": "v1",
        "health": "/api/v1/health/",
    })


urlpatterns = [
    path('', api_index, name='api-index'),
    path('education/', include('src.apps.education.api_urls')),
    # Future: mount per-app routers, e.g. accounts/, finance/, etc.
]
