from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from common.services import log_security_event

from .forms import PartnerApplicationForm
from .models import PartnerApplication


class PartnerApplicationCreateView(FormView):
    template_name = "partners/apply.html"
    form_class = PartnerApplicationForm
    success_url = reverse_lazy("partners:apply_thanks")

    def form_valid(self, form: PartnerApplicationForm):
        application: PartnerApplication = form.save(commit=False)
        if self.request.user.is_authenticated:
            application.submitted_by = self.request.user
        application.status = PartnerApplication.Status.RECEIVED
        application.metadata["request_meta"] = {
            "ip": self.request.META.get("REMOTE_ADDR"),
            "user_agent": self.request.META.get("HTTP_USER_AGENT"),
        }
        application.save()

        log_security_event(
            action="partners.application_submitted",
            actor=self.request.user if self.request.user.is_authenticated else None,
            request=self.request,
            resource=f"PartnerApplication:{application.pk}",
            metadata={
                "company": application.company_name,
                "partner_type": application.partner_type,
                "regions": application.regions,
                "integration_focus": application.integration_focus,
            },
        )

        messages.success(
            self.request,
            _("Başvurunuz alındı. Ekiplerimiz en kısa sürede sizinle iletişime geçecek."),
        )
        return super().form_valid(form)


class PartnerApplicationThanksView(TemplateView):
    template_name = "partners/apply_thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault(
            "page_title", _("FinAsis · Partner Başvurusu Gönderildi")
        )
        context["apply_url"] = reverse("partners:apply")
        return context

