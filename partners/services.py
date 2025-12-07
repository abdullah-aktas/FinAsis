from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.services import log_security_event

from .models import PartnerApplication, PartnerCategory, PartnerProfile


PARTNER_TYPE_CATEGORY_MAP = {
    "erp": "erp-integration",
    "crm": "crm-sales",
    "compliance": "regtech",
    "education": "education-lms",
    "payment": "fintech-payments",
    "consulting": "consulting",
    "other": "other",
}


def _get_or_create_category_for_application(
    application: PartnerApplication,
) -> Optional[PartnerCategory]:
    code = PARTNER_TYPE_CATEGORY_MAP.get(application.partner_type, "other")
    defaults = {
        "name": dict(PartnerApplication.PARTNER_TYPES).get(
            application.partner_type, _("Partner")
        ),
        "description": application.integration_focus,
    }
    category, _created = PartnerCategory.objects.get_or_create(code=code, defaults=defaults)
    return category


@dataclass
class ApprovalResult:
    application: PartnerApplication
    profile: Optional[PartnerProfile]
    profile_created: bool


def transition_application(
    application: PartnerApplication,
    *,
    status: str,
    reviewer,
    notes: str | None = None,
) -> bool:
    if application.status == status:
        return False
    application.status = status
    application.reviewed_by = reviewer
    application.reviewed_at = timezone.now()
    if notes:
        application.metadata.setdefault("review_notes", notes)
    application.save(
        update_fields=["status", "reviewed_by", "reviewed_at", "metadata", "updated_at"]
    )
    log_security_event(
        action="partners.application_status_changed",
        actor=reviewer,
        resource=f"PartnerApplication:{application.pk}",
        metadata={"status": status, "company": application.company_name},
    )
    return True


def reject_application(
    application: PartnerApplication,
    *,
    reviewer,
    notes: str | None = None,
) -> bool:
    changed = transition_application(
        application,
        status=PartnerApplication.Status.REJECTED,
        reviewer=reviewer,
        notes=notes,
    )
    if changed:
        _notify_applicant(application, template="partners/email/rejected.txt")
    return changed


def _notify_applicant(
    application: PartnerApplication, template: str, context: Optional[dict] = None
) -> None:
    if not application.contact_email:
        return
    merged_context = {
        "application": application,
        "company_name": application.company_name,
        "support_email": getattr(settings, "SUPPORT_EMAIL", "destek@finasis.com"),
        "marketplace_url": settings.SITE_BASE_URL + "/resources/partner-marketplace/",
    }
    if context:
        merged_context.update(context)
    subject = _("FinAsis Partner Programı Başvurusu")
    message = render_to_string(template, merged_context)
    send_mail(subject, message, None, [application.contact_email], fail_silently=True)


def _generate_unique_slug(name: str) -> str:
    base_slug = slugify(name) or "partner"
    slug = base_slug
    index = 1
    while PartnerProfile.objects.filter(slug=slug).exists():
        index += 1
        slug = f"{base_slug}-{index}"
    return slug


@transaction.atomic
def approve_application(
    application: PartnerApplication,
    *,
    reviewer,
    publish: bool = False,
    notes: str | None = None,
) -> ApprovalResult:
    if application.status == PartnerApplication.Status.REJECTED:
        raise ValueError(_("Reddedilmiş başvurular onaylanamaz."))

    transition_application(
        application,
        status=PartnerApplication.Status.APPROVED,
        reviewer=reviewer,
        notes=notes,
    )

    profile, created = _create_profile_from_application(application, publish=publish)
    if created:
        log_security_event(
            action="partners.profile_created",
            actor=reviewer,
            resource=f"PartnerProfile:{profile.pk}",
            metadata={"company": application.company_name, "status": profile.status},
        )
    if publish and profile.status == PartnerProfile.Status.PUBLISHED:
        _notify_applicant(
            application,
            template="partners/email/approved.txt",
            context={
                "profile_url": f"{settings.SITE_BASE_URL}/resources/partner-marketplace/"
            },
        )

    return ApprovalResult(
        application=application, profile=profile, profile_created=created
    )


def _create_profile_from_application(
    application: PartnerApplication,
    *,
    publish: bool,
) -> tuple[PartnerProfile, bool]:
    existing = PartnerProfile.objects.filter(
        slug=slugify(application.company_name)
    ).first()
    if existing:
        if publish:
            existing.status = PartnerProfile.Status.PUBLISHED
            existing.save(update_fields=["status", "updated_at"])
        return existing, False

    category = _get_or_create_category_for_application(application)
    status = (
        PartnerProfile.Status.PUBLISHED if publish else PartnerProfile.Status.REVIEW
    )
    profile = PartnerProfile.objects.create(
        category=category,
        name=application.company_name,
        slug=_generate_unique_slug(application.company_name),
        headline=application.integration_focus,
        description=application.additional_notes or application.integration_focus,
        integration_focus=application.integration_focus,
        website_url=application.website_url,
        contact_email=application.contact_email,
        badge_label=_("Yeni Partner"),
        regions=application.regions,
        status=status,
        is_featured=False,
    )
    return profile, True


__all__ = [
    "approve_application",
    "reject_application",
    "transition_application",
    "ApprovalResult",
]
