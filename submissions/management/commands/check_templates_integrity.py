from django.core.management.base import BaseCommand
from importlib import import_module


class Command(BaseCommand):
    help = "Check templates integrity: compile/render and verify internal links resolve."

    def handle(self, *args, **options):
        mod = import_module("tests.check_templates_integrity")
        if hasattr(mod, "main"):
            mod.main()
        else:
            self.stderr.write("tests.check_templates_integrity.main() bulunamadı")
