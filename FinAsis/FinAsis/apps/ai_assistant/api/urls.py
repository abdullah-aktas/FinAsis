from django.urls import path
from .views import ask_financial_assistant

urlpatterns = [
    path('ask/', ask_financial_assistant, name='ask_financial_assistant'),
] 