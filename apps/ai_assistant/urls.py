from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.ai_home, name='home'),
    path('chat/', views.ai_chat, name='chat'),
    path('analysis/', views.financial_analysis, name='analysis'),
    path('recommendations/', views.recommendations, name='recommendations'),
] 