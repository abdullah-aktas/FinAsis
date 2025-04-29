# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

app_name = 'seo_management'

urlpatterns = [
    path('', include(router.urls)),
] 