"""
Tüm önemli URL'ler için basit bir sağlık taraması yapan yönetim komutu.

Kullanım:
    python manage.py check_urls

Varsayılan olarak demo süper admin kullanıcısı ile login olur
(`setup_test_environment` ile oluşturulan `demo_superadmin` / `FinAsis!2025`),
ve login gerektiren ekranlar da dahil mümkün olduğunca çok GET endpoint'ini
HTTP seviyesinde test eder.

Amaç:
- 500 / TemplateSyntaxError üreten URL'leri hızlıca tespit etmek
- Yanlış tanımlanmış veya bozuk reverse isimlerini ortaya çıkarmak

Notlar:
- Parametre gerektiren URL'ler (örn. <int:pk>) varsayılan olarak atlanır.
- Admin, API veya statik dosya URL'leri hariç tutulur.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver


EXCLUDE_PREFIXES: Tuple[str, ...] = (
    "admin/",
    "api/",
    "static/",
    "media/",
    "__debug__/",
)


@dataclass
class UrlCheckResult:
    path: str
    status_code: int
    ok: bool
    error: str | None = None


def iter_url_patterns(
    patterns: Iterable[URLPattern | URLResolver],
    prefix: str = "",
) -> Iterable[str]:
    """
    Tüm URL pattern'lerini düz bir liste halinde üret.

    - Sadece `path()` ile tanımlanan klasik URL'ler desteklenir.
    - Dinamik parametre içeren (<'li) path'ler atlanır (pk/id bilmiyoruz).
    - Çıktı daima `/` ile başlar ve gerçek URL yapısıyla uyumludur
      (örn. `/games/trade-sim/start/`).
    """
    for pattern in patterns:
        pattern_str = str(pattern.pattern)
        full = f"{prefix}{pattern_str}"

        if hasattr(pattern, "url_patterns"):
            # Include edilmiş alt router; prefix sonuna "/" ekleyerek alt path'i oluştur
            new_prefix = full
            if not new_prefix.endswith("/"):
                new_prefix += "/"
            yield from iter_url_patterns(pattern.url_patterns, new_prefix)
        else:
            # Dinamik parametreli URL'leri şimdilik atla
            if "<" in pattern_str or ">" in pattern_str:
                continue
            # Boş pattern ana sayfa anlamına gelir
            if full in ("", "/"):
                yield "/"
            else:
                # Çift slash'leri normalize et ve başına "/" ekle
                normalized = full.replace("//", "/")
                if not normalized.startswith("/"):
                    normalized = "/" + normalized
                yield normalized


class Command(BaseCommand):
    help = "Tüm önemli GET URL'leri için basit bir sağlık taraması yapar."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--username",
            default="demo_superadmin",
            help="Login için kullanılacak kullanıcı adı (varsayılan: demo_superadmin)",
        )
        parser.add_argument(
            "--password",
            default="FinAsis!2025",
            help="Login için parola (varsayılan: FinAsis!2025)",
        )
        parser.add_argument(
            "--anonymous",
            action="store_true",
            help="Login yapmadan anonim olarak test çalıştır.",
        )

    def handle(self, *args, **options) -> None:
        username: str = options["username"]
        password: str = options["password"]
        anonymous: bool = options["anonymous"]

        self.stdout.write(
            self.style.MIGRATE_HEADING("🔍 URL Sağlık Taraması Başlatılıyor")
        )
        self.stdout.write(f"DEBUG={getattr(settings, 'DEBUG', False)}")

        # URL listesi
        resolver = get_resolver()
        all_paths = sorted(set(iter_url_patterns(resolver.url_patterns)))

        # Özel olarak hariç tutulan prefix'ler
        paths: List[str] = []
        for p in all_paths:
            # Admin, API, static gibi teknik path'leri atla
            trimmed = p.lstrip("/")
            if any(trimmed.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
                continue
            paths.append(p)

        self.stdout.write(f"Toplam {len(paths)} URL kontrol edilecek.\n")

        client = Client()

        if not anonymous:
            self.stdout.write(f"Giriş yapmayı deniyor: {username!r}")
            logged_in = client.login(username=username, password=password)
            if not logged_in:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Login başarısız oldu ({username}). URL'ler anonim olarak test edilecek."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Login başarılı, authenticated URL'ler de test edilecek.\n"
                    )
                )
        else:
            self.stdout.write("Anonim modda çalıştırılıyor (login yapılmayacak).\n")

        results: List[UrlCheckResult] = []

        for path in paths:
            try:
                resp = client.get(path, follow=True)
                ok = resp.status_code < 500
                results.append(
                    UrlCheckResult(
                        path=path,
                        status_code=resp.status_code,
                        ok=ok,
                        error=None if ok else f"HTTP {resp.status_code}",
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    UrlCheckResult(
                        path=path,
                        status_code=500,
                        ok=False,
                        error=str(exc),
                    )
                )

        # Özet
        ok_results = [r for r in results if r.ok and r.status_code < 400]
        warn_results = [r for r in results if r.ok and 400 <= r.status_code < 500]
        error_results = [r for r in results if not r.ok]

        self.stdout.write(self.style.MIGRATE_HEADING("\n📋 Sonuç Özeti"))
        self.stdout.write(self.style.SUCCESS(f"✅ Başarılı: {len(ok_results)} URL"))
        self.stdout.write(
            self.style.WARNING(f"⚠️  Uyarı (4xx): {len(warn_results)} URL")
        )
        self.stdout.write(
            self.style.ERROR(f"❌ Hata (5xx / exception): {len(error_results)} URL\n")
        )

        if warn_results:
            self.stdout.write(
                self.style.WARNING("4xx Dönen (muhtemel 404 / izin hatası) URL'ler:")
            )
            for r in warn_results[:20]:
                self.stdout.write(f"  - {r.path} -> HTTP {r.status_code}")
            if len(warn_results) > 20:
                self.stdout.write(f"  ... toplam {len(warn_results)} kayıt\n")

        if error_results:
            self.stdout.write(
                self.style.ERROR("Hata veren URL'ler (öncelikli inceleme gerekli):")
            )
            for r in error_results:
                msg = f"  - {r.path} -> {r.error or f'HTTP {r.status_code}'}"
                self.stdout.write(msg)

            # Komutu CI/CD'de kırmızı göstermek için non-zero exit
            raise SystemExit(1)

        self.stdout.write(
            self.style.SUCCESS(
                "🎉 URL sağlık taraması tamamlandı, kritik hata bulunmadı."
            )
        )
