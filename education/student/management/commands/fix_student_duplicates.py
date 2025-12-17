# -*- coding: utf-8 -*-
"""
StudentProfile'deki duplicate student_number kayıtlarını düzeltir.
Kullanım: python manage.py fix_student_duplicates
"""
from django.core.management.base import BaseCommand
from education.student.models import StudentProfile
from django.db.models import Count


class Command(BaseCommand):
    help = "StudentProfile'deki duplicate student_number kayıtlarını düzeltir"

    def handle(self, *args, **options):
        self.stdout.write("🔍 Duplicate student_number kayıtları aranıyor...")

        # Duplicate'leri bul
        duplicates = (
            StudentProfile.objects.values("student_number")
            .annotate(count=Count("student_number"))
            .filter(count__gt=1)
        )

        if not duplicates:
            self.stdout.write(self.style.SUCCESS("✅ Duplicate kayıt bulunamadı."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"⚠️  {len(duplicates)} duplicate student_number bulundu."
            )
        )

        fixed_count = 0
        for dup in duplicates:
            student_number = dup["student_number"]
            if not student_number:  # Boş student_number'ları atla
                continue

            students = StudentProfile.objects.filter(
                student_number=student_number
            ).order_by("id")

            self.stdout.write(
                f"\n📝 '{student_number}' için {students.count()} kayıt bulundu:"
            )

            # İlkini tut, diğerlerini düzelt
            for idx, student in enumerate(students):
                if idx == 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✅ İlk kayıt korunuyor: {student.user.username} (ID: {student.id})"
                        )
                    )
                else:
                    # Duplicate için yeni bir numara oluştur
                    new_number = f"{student_number}_dup_{student.id}"
                    student.student_number = new_number
                    student.save()
                    self.stdout.write(
                        f"  🔧 Düzeltildi: {student.user.username} (ID: {student.id}) → {new_number}"
                    )
                    fixed_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Toplam {fixed_count} kayıt düzeltildi.")
        )
