from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

app_name = 'ext_services'

urlpatterns = [
    path('', include(router.urls)),
] 