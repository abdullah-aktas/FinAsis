from django.db import models
from FinAsis.apps.accounts.managers import CompanyManager


class CompanyQuerySet(models.QuerySet):
    def for_user(self, user):
        if user.is_superuser:
            return self
        return self.filter(company=user.company)

class CompanyManager(models.Manager):
    def get_queryset(self):
        return CompanyQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)


class Invoice(models.Model):
    company = models.ForeignKey("accounts.Company", on_delete=models.CASCADE, related_name="invoices")
    ...
    objects = CompanyManager()