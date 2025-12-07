from __future__ import annotations
from django.utils import timezone
from typing import Tuple
from .models import Submission, SubmissionLog
from .integration import submit_via_gib


def send_submission_to_gib(submission: Submission) -> Tuple[str, str]:
    """GİB'e gönderim (stub/http modlarına göre GibClient kullanır).

    Dönüş: (external_id/tracking_id, final_status)
    """
    SubmissionLog.objects.create(
        submission=submission,
        level="info",
        message="Gönderim başlatılıyor...",
        context={"target": submission.target},
    )

    tracking_id, status = submit_via_gib(submission)

    # State machine: draft->queued->sent->accepted/rejected
    submission.external_id = tracking_id
    if not submission.submitted_at:
        submission.submitted_at = timezone.now()
    lowered = (status or "").lower()
    if lowered in ("accepted", "rejected"):
        submission.status = lowered
    elif lowered in ("pending", "queued", "sent"):
        submission.status = "sent"
    else:
        submission.status = lowered or "sent"
    submission.save(update_fields=["external_id", "submitted_at", "status"])

    return tracking_id, status
