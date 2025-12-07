# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from education.models import MeetingRecording


class Command(BaseCommand):
    help = "Prune old meeting recordings by age and/or keep-max per meeting. Deletes files and DB rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Delete recordings older than N days.",
        )
        parser.add_argument(
            "--keep-per-meeting",
            type=int,
            default=None,
            help="Keep at most N newest recordings per meeting (delete older).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not delete, just print what would be deleted.",
        )

    def handle(self, *args, **opts):
        days = opts["days"]
        keep = opts["keep_per_meeting"]
        dry = opts["dry_run"]
        # Defaults from settings if not provided
        if days is None:
            days = getattr(settings, "EDU_RECORDINGS_RETENTION_DAYS", None)
        if keep is None:
            keep = getattr(settings, "EDU_RECORDINGS_MAX_PER_MEETING", None)

        total = 0
        # Prune by age
        if days:
            cutoff = timezone.now() - timedelta(days=int(days))
            old_qs = MeetingRecording.objects.filter(created_at__lt=cutoff)
            total += self._delete_qs(old_qs, dry=dry, reason=f"older_than_{days}d")
        # Prune by count per meeting
        if keep:
            # Iterate meetings that exceed count
            meeting_ids = MeetingRecording.objects.values_list(
                "meeting_id", flat=True
            ).distinct()
            for mid in meeting_ids:
                qs = MeetingRecording.objects.filter(meeting_id=mid).order_by(
                    "-created_at"
                )
                ids = list(qs.values_list("id", flat=True))
                if len(ids) > int(keep):
                    delete_ids = ids[int(keep) :]
                    del_qs = MeetingRecording.objects.filter(id__in=delete_ids)
                    total += self._delete_qs(
                        del_qs, dry=dry, reason=f"exceeds_keep_{keep}"
                    )
        self.stdout.write(
            self.style.SUCCESS(
                f"Prune completed. Deleted: {total}{' (dry-run)' if dry else ''}"
            )
        )

    def _delete_qs(self, qs, dry=False, reason=""):
        count = 0
        for rec in qs:
            try:
                if dry:
                    self.stdout.write(
                        f"DRY {reason}: would delete rec#{rec.pk} file={getattr(rec.file, 'name', '')}"
                    )
                else:
                    try:
                        f = getattr(rec, "file", None)
                        if f and getattr(f, "name", None):
                            f.delete(save=False)
                    except Exception:
                        pass
                    rec.delete()
                    count += 1
            except Exception as e:
                self.stderr.write(
                    f"Failed to delete rec#{getattr(rec, 'pk', '?')}: {e}"
                )
        return count
