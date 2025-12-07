"""
Management command to check for recent errors
Kullanım: python manage.py check_errors --hours 1
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from common.error_tracking import ErrorLog


class Command(BaseCommand):
    help = "Check for recent errors and generate report"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=1,
            help="Number of hours to look back (default: 1)",
        )
        parser.add_argument(
            "--severity",
            type=str,
            default="",
            help="Filter by severity (CRITICAL, ERROR, WARNING)",
        )
        parser.add_argument(
            "--status",
            type=str,
            default="NEW",
            help="Filter by status (NEW, INVESTIGATING, RESOLVED, IGNORED)",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        severity = options["severity"]
        status = options["status"]

        # Calculate time range
        time_threshold = timezone.now() - timedelta(hours=hours)

        # Query errors
        errors = ErrorLog.objects.filter(last_seen__gte=time_threshold)

        if severity:
            errors = errors.filter(severity=severity)

        if status:
            errors = errors.filter(status=status)

        # Generate report
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS(f"Error Report - Last {hours} hour(s)"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

        if not errors.exists():
            self.stdout.write(self.style.SUCCESS("✓ No errors found!"))
            return

        # Summary
        total_errors = errors.count()
        critical_count = errors.filter(severity="CRITICAL").count()
        error_count = errors.filter(severity="ERROR").count()
        warning_count = errors.filter(severity="WARNING").count()

        self.stdout.write(f"\nTotal Errors: {total_errors}")
        self.stdout.write(f"  - CRITICAL: {critical_count}")
        self.stdout.write(f"  - ERROR: {error_count}")
        self.stdout.write(f"  - WARNING: {warning_count}")

        # Top errors by occurrence
        self.stdout.write(self.style.WARNING("\n" + "-" * 80))
        self.stdout.write(self.style.WARNING("Top Errors by Occurrence:"))
        self.stdout.write(self.style.WARNING("-" * 80))

        top_errors = errors.order_by("-occurrence_count")[:10]
        for i, error in enumerate(top_errors, 1):
            self.stdout.write(
                f"\n{i}. [{error.severity}] {error.error_type} "
                f"(x{error.occurrence_count})"
            )
            self.stdout.write(f"   Message: {error.error_message[:100]}")
            self.stdout.write(f"   Last seen: {error.last_seen}")
            self.stdout.write(f"   Status: {error.status}")

        # Recent critical errors
        critical_errors = errors.filter(severity="CRITICAL").order_by("-last_seen")[:5]
        if critical_errors.exists():
            self.stdout.write(self.style.ERROR("\n" + "=" * 80))
            self.stdout.write(self.style.ERROR("🚨 RECENT CRITICAL ERRORS:"))
            self.stdout.write(self.style.ERROR("=" * 80))

            for i, error in enumerate(critical_errors, 1):
                self.stdout.write(
                    self.style.ERROR(f"\n{i}. {error.error_type} - {error.last_seen}")
                )
                self.stdout.write(f"   {error.error_message[:150]}")
                self.stdout.write(f"   URL: {error.url}")
                self.stdout.write(
                    f'   User: {error.user.email if error.user else "Anonymous"}'
                )

        # Unnotified errors
        unnotified = errors.filter(
            admin_notified=False, severity__in=["CRITICAL", "ERROR"]
        )
        if unnotified.exists():
            self.stdout.write(self.style.WARNING("\n" + "=" * 80))
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  {unnotified.count()} error(s) not yet notified to admins"
                )
            )
            self.stdout.write(self.style.WARNING("=" * 80))

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("Report complete!"))
