from __future__ import annotations

from django.urls import path

from developer_portal import views

app_name = "developer_portal"

urlpatterns = [
    path("", views.DeveloperPortalDashboardView.as_view(), name="dashboard"),
    path("keys/", views.APIKeyListView.as_view(), name="api_keys"),
    path("keys/<uuid:pk>/", views.APIKeyDetailView.as_view(), name="api_key_detail"),
    path(
        "keys/<uuid:pk>/rotate/",
        views.APIKeyRotateView.as_view(),
        name="api_key_rotate",
    ),
    path(
        "keys/<uuid:pk>/revoke/",
        views.APIKeyRevokeView.as_view(),
        name="api_key_revoke",
    ),
    path("docs/", views.DeveloperDocsView.as_view(), name="docs"),
    path("webhooks/", views.WebhookConsoleView.as_view(), name="webhook_console"),
]
