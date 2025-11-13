from __future__ import annotations

from pathlib import Path
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from security import compliance


class Command(BaseCommand):
    help = "Uyumluluk checklist'lerini çalıştırır ve raporlar."

    def add_arguments(self, parser):
        parser.add_argument(
            "--profile",
            "-p",
            action="append",
            dest="profiles",
            help="Çalıştırılacak checklist adı (örn. masak, kvkk). Çoklu kullanılabilir.",
        )
        parser.add_argument(
            "--output",
            "-o",
            dest="output",
            help="Raporun yazılacağı dosya yolu (Markdown).",
        )

    def handle(self, *args, **options):
        profiles = options.get("profiles") or self._discover_profiles()
        if not profiles:
            raise CommandError("Çalıştırılacak checklist bulunamadı.")

        all_results = []
        any_failed = False
        debug = settings.DEBUG

        for profile in profiles:
            try:
                checks = compliance.load_checklist(profile)
            except FileNotFoundError as exc:
                self.stderr.write(self.style.ERROR(str(exc)))
                any_failed = True
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"[{profile}] Kontroller çalıştırılıyor"))
            for entry in checks:
                result = compliance.run_check(entry, debug=debug)
                all_results.append((profile, result))
                if result.passed:
                    label = self.style.SUCCESS("PASS")
                elif result.skipped:
                    label = self.style.WARNING("SKIP")
                else:
                    label = self.style.ERROR("FAIL")
                    any_failed = True
                self.stdout.write(f" {label} {result.id} - {result.title}: {result.message}")

        output = options.get("output")
        if output:
            self._write_markdown(Path(output), all_results)
            self.stdout.write(self.style.HTTP_INFO(f"Rapor kaydedildi: {output}"))

        if any_failed:
            raise CommandError("Bazı checklist kontrolleri başarısız oldu.")

    def _discover_profiles(self) -> List[str]:
        profiles = []
        for path in compliance.CHECKLIST_DIR.glob("*.yml"):
            profiles.append(path.stem)
        return sorted(profiles)

    def _write_markdown(self, path: Path, results):
        lines = [
            "# Compliance Raporu",
            "",
            "| Profil | ID | Başlık | Sonuç | Mesaj | Ciddiyet |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for profile, result in results:
            status = "PASS" if result.passed else ("SKIP" if result.skipped else "FAIL")
            lines.append(
                f"| {profile} | {result.id} | {result.title} | {status} | {result.message} | {result.severity} |"
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")

