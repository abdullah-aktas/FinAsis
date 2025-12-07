"""
Dashboard API URL Configuration
"""

from django.urls import path
from .views_dashboard import (
    dashboard_stats,
    module_health,
    user_activity_graph,
)

app_name = "api_dashboard"

urlpatterns = [
    path("stats/", dashboard_stats, name="dashboard_stats"),
    path("health/", module_health, name="module_health"),
    path("activity/", user_activity_graph, name="user_activity_graph"),
]
