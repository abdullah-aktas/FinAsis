urlpatterns = [
    path("accounting/", include("accounting.urls")),
    path("accounts/", include("accounts.urls")),
    path("ai/", include("ai_assistant.urls")),
    path("blockchain/", include("blockchain.urls")),
    path("education/", include("education.urls")),
    path("finance/", include("finance.urls")),
    path("games/", include("games.urls")),
    # ...
]
