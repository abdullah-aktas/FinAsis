from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from security import retention


class Command(BaseCommand):
    help = "Retention profillerini çalıştırarak KVKK/MASAK veri saklama politikalarını uygular."

    def add_arguments(self, parser):
        parser.add_argument(
            "--profile",
            action="append",
            dest="profiles",
            help="Çalıştırılacak retention profili ismi (birden fazla girilebilir).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Değişiklikleri uygulamadan etkilenecek kayıt sayısını raporla.",
        )

    def handle(self, *args, **options):
        profiles = options.get("profiles") or ["default"]
        dry_run = options.get("dry_run", False)

        self.stdout.write(
            self.style.NOTICE(
                f"Retention çalıştırılıyor | profiller={profiles} dry_run={dry_run}"
            )
        )

        overall_results: list[dict[str, object]] = []
        for profile in profiles:
            self.stdout.write(f"- Profil: {profile}")
            try:
                results = retention.execute_profile(profile, dry_run=dry_run)
            except FileNotFoundError as exc:
                raise CommandError(str(exc)) from exc
            except Exception as exc:  # pragma: no cover
                raise CommandError(
                    f"Profil yürütülürken hata oluştu ({profile}): {exc}"
                ) from exc

            for result in results:
                overall_results.append(result)
                self.stdout.write(
                    f"  • {result['model']} | action={result['action']} | affected={result['affected']}",
                )

        total = sum(int(item["affected"]) for item in overall_results)
        self.stdout.write(
            self.style.SUCCESS(f"Retention tamamlandı. Toplam etkilenen kayıt: {total}")
        )
