from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from src.apps.billing.models import Plan, Price, PlanGroup
from src.apps.accounts.models import SubscriptionType

class Command(BaseCommand):
    help = 'Check billing integrity: Plan→Price, Plan→Group, and Plan.code matching SubscriptionType.code (if exists).'

    def handle(self, *args, **options):
        ok = True
        for plan in Plan.objects.all():
            prices = Price.objects.filter(plan=plan, is_active=True)
            if not prices.exists():
                ok = False
                self.stdout.write(self.style.ERROR(f"Plan {plan.code} has no active prices"))
            if not PlanGroup.objects.filter(plan=plan).exists():
                ok = False
                self.stdout.write(self.style.ERROR(f"Plan {plan.code} has no PlanGroup mapping"))
            # SubscriptionType match (optional)
            st = SubscriptionType.objects.filter(code__iexact=plan.code).first()
            if not st:
                self.stdout.write(self.style.WARNING(f"No matching SubscriptionType for plan code {plan.code}"))
        if ok:
            self.stdout.write(self.style.SUCCESS('Billing integrity OK'))
        else:
            self.stdout.write(self.style.ERROR('Billing integrity issues found'))
