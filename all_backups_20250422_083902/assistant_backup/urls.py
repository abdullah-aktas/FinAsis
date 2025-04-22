from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('api/assistant/ask/', views.ask_assistant, name='ask_assistant'),
    path('api/assistant/history/<int:session_id>/', views.get_chat_history, name='get_chat_history'),
] 