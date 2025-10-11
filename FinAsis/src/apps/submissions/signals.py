from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubmissionLog
from src.apps.blockchain.services import ensure_record
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SubmissionLog)
def anchor_submission_log(sender, instance: SubmissionLog, created, **kwargs):
    # Anchor every log to blockchain for immutable audit trail
    sub_id = getattr(instance, 'submission_id', None) or (instance.submission.pk if getattr(instance, 'submission', None) else '')
    ref = f"submission:{sub_id}:log:{getattr(instance, 'pk', '')}"
    # Build a deterministic, compact string payload as required by blockchain services
    ctx_keys = sorted((instance.context or {}).keys())
    ctx_part = ';'.join(f"{k}={instance.context[k]}" for k in ctx_keys)
    ts = instance.created_at.isoformat() if getattr(instance, 'created_at', None) else ''
    message = (instance.message or '')
    if len(message) > 500:
        message = message[:500]
    payload = f"SUBMISSION_LOG|{sub_id}|{instance.level}|{ts}|{message}|{ctx_part}"
    try:
        ensure_record(reference=ref, payload=payload, status='anchored')
    except Exception as e:
        # Sinyal hataları ana akışı kesmesin; logla ve devam et
        logger.warning("SubmissionLog anchoring failed: %s", e, extra={
            'ref': ref,
            'submission_id': sub_id,
        })
