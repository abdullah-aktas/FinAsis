from django.urls import path
from . import views

urlpatterns = [
    path('send', views.send, name='gib-mock-send'),
    path('status', views.status, name='gib-mock-status'),
]
