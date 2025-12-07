from django.conf import settings
from rest_framework.permissions import BasePermission


class AdvisorOnlySubmission(BasePermission):
    message = "Beyan ve defter gönderimleri sadece yetkili mali müşavirler üzerinden yapılabilir."

    def has_permission(self, request, view):
        # Allow if feature flag explicitly allows direct submissions
        if getattr(settings, "SUBMISSIONS_ALLOW_DIRECT", False):
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        # User must be an advisor with verified profile
        advisor = getattr(user, "advisor_profile", None)
        if not advisor or not getattr(advisor, "verified_at", None):
            return False
        return True
