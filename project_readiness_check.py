#!/usr/bin/env python
"""
Django Proje Hazırlık Kontrol Scripti

Kullanım:
    python project_readiness_check.py

Bu script aşağıdakileri yapar:
- Django sistem kontrolleri
- Boşta bekleyen migration var mı?
- Testleri çalıştırma (özellikle smoke testler)
- collectstatic dry-run
- URL haritasını ve admin panelinin ulaşılabilirliğini raporlama
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MANAGE_PY = BASE_DIR / "manage.py"


def run(cmd: str, description: str, stop_on_fail: bool = True) -> bool:
    """Yardımcı fonksiyon: komutu çalıştırır, sonucu yazar."""
    print("\n" + "=" * 80)
    print(f"▶ {description}")
    print(f"   $ {cmd}")
    print("=" * 80)
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print(f"✅ {description} BAŞARILI")
        return True

    print(f"❌ {description} BAŞARISIZ (exit code: {result.returncode})")
    if stop_on_fail:
        print("\n⚠ Hata alan aşamadan sonra devam edilmedi.")
        sys.exit(result.returncode)
    return False


def print_urls():
    """
    Projedeki URL’leri listeler (bilgi amaçlı).
    Burada hata olması durumunda canlıya almadan önce URLconf sorunlarını da görürsün.
    """
    print("\n" + "=" * 80)
    print("▶ URL Haritası (Debug amaçlı)")
    print("=" * 80)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "config.settings"))

    import django

    django.setup()
    from django.urls import get_resolver

    resolver = get_resolver()
    for pattern in resolver.url_patterns:
        try:
            pattern_str = str(pattern.pattern)
        except Exception:
            pattern_str = repr(pattern)
        name = getattr(pattern, "name", None)
        print(f"- {pattern_str}  (name={name})")


def main():
    if not MANAGE_PY.exists():
        print("manage.py bu dizinde bulunamadı. Scripti proje kökünde çalıştırdığından emin ol.")
        sys.exit(1)

    python = sys.executable

    # 1) Django check
    run(f"{python} manage.py check", "Django sistem kontrolleri")

    # 2) Boşta migration var mı?
    run(
        f"{python} manage.py makemigrations --check --dry-run",
        "Boşta bekleyen migration var mı kontrolü",
        stop_on_fail=False,
    )

    # 3) migrate planı (uygulanmamış migration var mı görmek için)
    run(
        f"{python} manage.py showmigrations",
        "Migration durumunun listelenmesi",
        stop_on_fail=False,
    )

    # 3b) Demo verisi ve AI varlıkları hazır mı?
    run(
        f"{python} manage.py setup_test_environment",
        "Test ortamı ve AI demolarının hazırlanması",
        stop_on_fail=False,
    )

    # 4) URL’leri listeler (bilgi için)
    try:
        print_urls()
    except Exception as exc:  # pragma: no cover - bilgilendirme amaçlı
        print(f"⚠ URL'ler listelenirken hata oluştu: {exc}")

    # 5) Smoke testler + diğer testler
    run(
        f"{python} manage.py test",
        "Tüm testlerin (özellikle smoke testlerin) çalıştırılması",
        stop_on_fail=True,
    )

    # 6) collectstatic dry-run
    run(
        f"{python} manage.py collectstatic --dry-run --noinput",
        "Static dosyaların collectstatic ile toplanabilirliğinin testi (dry-run)",
        stop_on_fail=False,
    )

    print("\n" + "=" * 80)
    print("🎉 TOPLAM DURUM")
    print("Yukarıdaki adımlar hata vermeden geçtiyse projen canlıya almaya GÖRÜNÜŞE GÖRE hazır.")
    print("Yine de canlı ortamda DEBUG=False ve gerçek veritabanı ile son bir kez test etmeni öneririm.")
    print("=" * 80)


if __name__ == "__main__":
    main()


