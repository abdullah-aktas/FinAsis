# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet)

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),
] 