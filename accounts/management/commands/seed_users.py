from __future__ import annotations

import csv
import sys
import secrets
from typing import List, Dict

from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import UserType, UserSettings


PRIVACY_NOTE = (
    "Bu komut test/yerel geliştirme içindir. Gerçek kişisel veri (PII) üretmez; "
    "kullanıcı adları ve e‑postalar sahte alan adlarıyla (example.local) oluşturulur."
)


class Command(BaseCommand):
    help = "Veri gizliliğine uygun, sahte (PII içermeyen) kullanıcılar oluşturur."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--count", type=int, default=0, help="Toplam kullanıcı sayısı (tip dağılımı eşit paylaşılır)")
        parser.add_argument("--kobi", type=int, default=0, help="KOBİ kullanıcı sayısı")
        parser.add_argument("--egitimci", type=int, default=0, help="Eğitimci kullanıcı sayısı")
        parser.add_argument("--ogrenci", type=int, default=0, help="Öğrenci kullanıcı sayısı")
        parser.add_argument("--oyuncu", type=int, default=0, help="Oyuncu kullanıcı sayısı")
        parser.add_argument("--password", type=str, default=None, help="Varsayılan parola (aksi halde her kullanıcı için rastgele)\nUYARI: Parolayı stdout'a yazmayız, isterseniz --out ile CSV alın")
        parser.add_argument("--out", type=str, default=None, help="Oluşturulan kullanıcıları CSV olarak bu dosyaya yaz")
        parser.add_argument("--email-notifications", choices=["on", "off"], default="off", help="E-posta bildirim ayarı (UserSettings)")
        parser.add_argument("--dry-run", action="store_true", help="Sadece ne yapılacağını göster, veri yazma")

    def handle(self, *args, **options):
        User = get_user_model()

        # Hedef sayıları hesapla
        per_type: Dict[str, int] = {
            "kobi": int(options.get("kobi") or 0),
            "egitimci": int(options.get("egitimci") or 0),
            "ogrenci": int(options.get("ogrenci") or 0),
            "oyuncu": int(options.get("oyuncu") or 0),
        }
        total = sum(per_type.values())
        if total == 0 and options.get("count"):
            # Tip dağılımı verilmediyse eşit paylaştır
            base = int(options["count"]) // 4
            remainder = int(options["count"]) - base * 4
            for code in list(per_type.keys()):
                per_type[code] = base
            # Kalanı ilk tiplere dağıt
            for i, code in enumerate(per_type.keys()):
                if i < remainder:
                    per_type[code] += 1
            total = options["count"]

        if total == 0:
            self.stdout.write(self.style.WARNING(
                "Oluşturulacak kullanıcı sayısı 0. --count veya tip bazında (--kobi vb.) girin."
            ))
            return

        # Gizlilik notu
        self.stdout.write(self.style.NOTICE(PRIVACY_NOTE))

        # UserType kayıtlarını garanti altına al
        with transaction.atomic():
            existing_types = {ut.code for ut in UserType.objects.all()}
            needed = [code for code in per_type.keys() if code not in existing_types]
            for code in needed:
                UserType.objects.get_or_create(code=code, defaults={"name": code.capitalize()})

        email_notifications = (options.get("email-notifications") == "on")
        use_password = options.get("password")
        out_path = options.get("out")
        dry_run = bool(options.get("dry-run"))

        created_rows: List[List[str]] = []

        def gen_password() -> str:
            # 16 char URL-safe, includes letters/digits
            return secrets.token_urlsafe(12)

        def gen_username(code: str) -> str:
            return f"{code}_{secrets.token_hex(3)}"

        # Oluşturma
        with transaction.atomic():
            for code, count in per_type.items():
                if count <= 0:
                    continue
                user_type = UserType.objects.filter(code=code).first()
                for _ in range(count):
                    username = gen_username(code)
                    email = f"{username}@example.local"
                    password = use_password or gen_password()

                    if dry_run:
                        created_rows.append([username, email, code, password if out_path else "<hidden>"])
                        continue

                    user = User(
                        username=username,
                        email=email,
                        first_name="",  # Veri minimizasyonu: isim/surname boş
                        last_name="",
                        role="staff",
                        user_type=user_type,
                    )
                    user.set_password(password)
                    user.save()

                    # UserSettings: bildirim tercihini set et
                    UserSettings.objects.get_or_create(user=user, defaults={
                        "email_notifications": email_notifications,
                        "dark_mode": False,
                    })

                    created_rows.append([username, email, code, password if out_path else "<hidden>"])

        # CSV çıktısı
        if out_path:
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["username", "email", "user_type", "password"])
                writer.writerows(created_rows)
            self.stdout.write(self.style.SUCCESS(f"{len(created_rows)} kullanıcı CSV'ye yazıldı: {out_path}"))
        else:
            # Parolaları STDOUT'a yazmayın, sadece özet verin
            masked = [row[:3] + ["<hidden>"] for row in created_rows]
            # Konsol özeti (ilk 10)
            preview = "\n".join([", ".join(row) for row in masked[:10]])
            self.stdout.write(self.style.SUCCESS(f"Toplam {len(created_rows)} kullanıcı hazırlandı."))
            if preview:
                self.stdout.write(preview)

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mod: veri yazılmadı."))


