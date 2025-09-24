from django.urls import path
from . import views

app_name = 'trade_sim'

urlpatterns = [
    path('start/', views.start_game, name='start_game'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('stats/', views.stats, name='stats'),
    path('guest-onboarding/', views.guest_onboarding, name='guest_onboarding'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('cities/', views.city_list, name='city_list'),
    path('cities/<int:city_id>/', views.city_detail, name='city_detail'),
    path('trade/', views.trade_between_cities, name='trade_between_cities'),
    path('characters/', views.CharacterListCreateView.as_view(), name='character_list_create'),
    path('characters/<int:pk>/', views.CharacterDetailView.as_view(), name='character_detail'),
    path('quests/', views.QuestListView.as_view(), name='quest_list'),
    path('characters/<int:character_id>/quests/', views.CharacterQuestListCreateView.as_view(), name='character_quest_list_create'),
    path('character-quests/<int:pk>/', views.CharacterQuestDetailView.as_view(), name='character_quest_detail'),
    path('tournaments/', views.TournamentListCreateView.as_view(), name='tournament_list_create'),
    path('tournaments/<int:pk>/', views.TournamentDetailView.as_view(), name='tournament_detail'),
    path('tournaments/<int:tournament_id>/entries/', views.TournamentEntryListCreateView.as_view(), name='tournament_entry_list_create'),
    path('tournament-entries/<int:pk>/', views.TournamentEntryDetailView.as_view(), name='tournament_entry_detail'),
    path('characters/<int:character_id>/ai-suggestion/', views.ai_story_suggestion, name='ai_story_suggestion'),
    path('ai-market-suggestion/', views.ai_market_suggestion, name='ai_market_suggestion'),
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', views.NotificationMarkReadView.as_view(), name='notification_mark_read'),
    path('chat-messages/', views.ChatMessageListCreateView.as_view(), name='chat_message_list_create'),
    path('chat-messages/<int:pk>/report/', views.ChatMessageReportView.as_view(), name='chat_message_report'),
    path('products/', views.product_list, name='product_list'),
    path('city-markets/<int:city_id>/', views.city_market_list, name='city_market_list'),
    path('city-trade/', views.city_trade, name='city_trade'),
    path('trigger-market-event/', views.trigger_market_event, name='trigger_market_event'),
    path('api/qr-reward/', views.qr_reward, name='qr_reward'),
] 