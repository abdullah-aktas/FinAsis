urlpatterns = [
    path('accounting/', include('FinAsis.apps.accounting.urls')),
    path('accounts/', include('FinAsis.apps.accounts.urls')),
    path('ai/', include('FinAsis.apps.ai_assistant.urls')),
    path('blockchain/', include('FinAsis.apps.blockchain.urls')),
    path('education/', include('FinAsis.apps.education.urls')),
    path('finance/', include('FinAsis.apps.finance.urls')),
    path('games/', include('FinAsis.apps.games.urls')),
    # ...
] 