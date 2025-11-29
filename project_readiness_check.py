#!/usr/bin/env python
"""
Django Proje Hazırlık ve Otomatik Düzeltme Scripti

Kullanım:
    python project_readiness_check.py
    python project_readiness_check.py --auto-fix

Bu script aşağıdakileri yapar:
- Django sistem kontrolleri
- Boşta bekleyen migration var mı?
- (İsteğe bağlı) Migration'ları üretip uygulama (--auto-fix ile)
- Testleri çalıştırma (özellikle smoke testler)
- collectstatic dry-run
- (İsteğe bağlı) Gerçek collectstatic çalıştırma (--auto-fix ile)
- URL haritasını ve admin panelinin ulaşılabilirliğini raporlama
"""

import os
import re
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


def collect_template_url_names(base_dir: Path) -> set[str]:
    """
    Tüm .html şablon dosyalarındaki {% url 'namespace:name' %} kullanımlarını toplar.
    Amaç: Template'te kullanılan URL isimleri ile URLconf'taki isimleri çapraz kontrol etmek.
    """
    url_tag_re = re.compile(r"{%\s*url\s+['\"]([^'^\"]+)['\"]")
    names: set[str] = set()

    for html_path in base_dir.rglob("*.html"):
        try:
            text = html_path.read_text(encoding="utf-8")
        except Exception:
            continue

        for match in url_tag_re.finditer(text):
            name = match.group(1).strip()
            if name:
                names.add(name)

    return names


def check_template_urls(base_dir: Path) -> None:
    """
    Template'lerde kullanılan URL isimlerinin gerçekten tanımlı olup olmadığını kontrol eder.
    Boşa dönen buton / link kalmaması için uyarı üretir.
    """
    print("\n" + "=" * 80)
    print("▶ Template URL kontrolleri")
    print("=" * 80)

    # Django ortamını hazırla
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.getenv("DJANGO_SETTINGS_MODULE", "config.settings"),
    )

    import django

    django.setup()
    from django.urls import get_resolver

    resolver = get_resolver()

    # URLconf'ta tanımlı isimler
    valid_names = {
        name
        for name in resolver.reverse_dict.keys()
        if isinstance(name, str)
    }

    # Template'lerden toplanan isimler
    template_names = collect_template_url_names(base_dir)

    unused_in_urlconf = sorted(template_names - valid_names)

    print(f"- Bulunan template URL isimleri: {len(template_names)}")
    print(f"- URLConf'ta tanımlı isimler: {len(valid_names)}")

    if not unused_in_urlconf:
        print("✅ Tüm template URL isimleri URLConf içinde tanımlı görünüyor.")
        return

    print("⚠ Aşağıdaki URL isimleri template'lerde kullanılmış ancak URLConf'ta bulunamadı:")
    for name in unused_in_urlconf:
        print(f"  - {name}")

    print(
        "\nNot: Bu isimler yanlış yazılmış olabilir veya ilgili app bu ortamda yüklü değildir.\n"
        "Boşa dönen düğme/linkleri önlemek için bu listeyi gözden geçirmen önerilir."
    )


def main():
    auto_fix = "--auto-fix" in sys.argv

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

    # 2b) İsteğe bağlı otomatik düzeltme: migration üret + migrate
    if auto_fix:
        run(
            f"{python} manage.py makemigrations",
            "Eksik migration'ların oluşturulması (auto-fix)",
            stop_on_fail=False,
        )
        run(
            f"{python} manage.py migrate",
            "Veritabanı schema'sının güncellenmesi (auto-fix)",
            stop_on_fail=True,
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

    # 4b) Template URL isimlerini kontrol et
    try:
        check_template_urls(BASE_DIR)
    except Exception as exc:  # pragma: no cover - bilgilendirme amaçlı
        print(f"⚠ Template URL kontrolleri sırasında hata oluştu: {exc}")

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

    # 6b) İsteğe bağlı gerçek collectstatic
    if auto_fix:
        run(
            f"{python} manage.py collectstatic --noinput",
            "Static dosyaların gerçek collectstatic ile toplanması (auto-fix)",
            stop_on_fail=False,
        )

    print("\n" + "=" * 80)
    print("🎉 TOPLAM DURUM")
    print("Yukarıdaki adımlar hata vermeden geçtiyse projen canlıya almaya GÖRÜNÜŞE GÖRE hazır.")
    print("Yine de canlı ortamda DEBUG=False ve gerçek veritabanı ile son bir kez test etmeni öneririm.")
    print("=" * 80)


if __name__ == "__main__":
    main()


