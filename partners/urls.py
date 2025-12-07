from django.urls import path

from . import views

app_name = "partners"

urlpatterns = [
    path("apply/", views.PartnerApplicationCreateView.as_view(), name="apply"),
    path(
        "apply/thanks/",
        views.PartnerApplicationThanksView.as_view(),
        name="apply_thanks",
    ),
]
