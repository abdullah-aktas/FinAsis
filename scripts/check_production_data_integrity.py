#!/usr/bin/env python
"""
Production'da gerçeği yansıtmayan verileri tespit eder.
Kullanım: python manage.py check_production_data_integrity
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from accounting.models import Company  # noqa: E402

User = get_user_model()


def check_demo_data():
    """Demo/test verilerini kontrol et"""
    issues = []

    # Demo kullanıcıları kontrol et
    demo_users = User.objects.filter(username__startswith="demo_")
    if demo_users.exists() and not settings.DEBUG:
        issues.append(
            {
                "type": "DEMO_USER",
                "message": f"Production'da {demo_users.count()} demo kullanıcı bulundu!",
                "count": demo_users.count(),
                "users": list(demo_users.values_list("username", flat=True)[:10]),
            }
        )

    # Demo şirketleri kontrol et
    demo_companies = (
        Company.objects.filter(name__icontains="demo")
        | Company.objects.filter(name__icontains="test")
        | Company.objects.filter(
            tax_number__startswith="100000000"  # Test vergi numaraları
        )
    )
    if demo_companies.exists() and not settings.DEBUG:
        issues.append(
            {
                "type": "DEMO_COMPANY",
                "message": f"Production'da {demo_companies.count()} demo/test şirket bulundu!",
                "count": demo_companies.count(),
                "companies": list(demo_companies.values_list("name", flat=True)[:10]),
            }
        )

    # Guest kullanıcıları kontrol et (sadece production'da sorun)
    if not settings.DEBUG:
        guest_users = User.objects.filter(username__startswith="guest-")
        if guest_users.count() > 100:  # Çok fazla guest kullanıcı
            issues.append(
                {
                    "type": "TOO_MANY_GUESTS",
                    "message": f"Production'da {guest_users.count()} guest kullanıcı var (normal: <100)",
                    "count": guest_users.count(),
                }
            )

    return issues


def main():
    print("🔍 Production veri bütünlüğü kontrol ediliyor...\n")

    issues = check_demo_data()

    if not issues:
        print("✅ Hiçbir sorun bulunamadı. Tüm veriler gerçek görünüyor.")
        return 0

    print(f"⚠️  {len(issues)} sorun bulundu:\n")
    for issue in issues:
        print(f"❌ {issue['type']}: {issue['message']}")
        if "users" in issue:
            print(f"   Kullanıcılar: {', '.join(issue['users'][:5])}")
        if "companies" in issue:
            print(f"   Şirketler: {', '.join(issue['companies'][:5])}")
        print()

    return 1


if __name__ == "__main__":
    exit(main())
