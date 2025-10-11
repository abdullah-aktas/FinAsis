from django.core.management.base import BaseCommand
from importlib import import_module


class Command(BaseCommand):
    help = "Check UI completeness by discovering template names via URLs and files, reporting missing screens."

    def handle(self, *args, **options):
        mod = import_module("tests.check_ui_completeness")
        # Reuse existing logic without duplicating code
        if hasattr(mod, "main"):
            mod.main()
        else:
            self.stderr.write("tests.check_ui_completeness.main() bulunamadı")
