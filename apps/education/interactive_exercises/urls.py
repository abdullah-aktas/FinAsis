from django.urls import path
from .oyunlastirma_api import complete_task

urlpatterns = [
    path('complete-task/', complete_task, name='complete-task'),
] 