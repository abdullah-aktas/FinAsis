urlpatterns = [
    path('accounting/', include('src.apps.accounting.urls')),
    path('accounts/', include('src.apps.accounts.urls')),
    path('ai/', include('src.apps.ai_assistant.urls')),
    path('blockchain/', include('src.apps.blockchain.urls')),
    path('education/', include('src.apps.education.urls')),
    path('finance/', include('src.apps.finance.urls')),
    path('games/', include('src.apps.games.urls')),
    # ...
] 