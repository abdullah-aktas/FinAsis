from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

from .models import Declaration, Submission, SubmissionLog
from .serializers import (
    DeclarationSerializer,
    SubmissionSerializer,
    SubmissionLogSerializer,
)
from .permissions import AdvisorOnlySubmission
from advisors.models import Engagement
from .services import send_submission_to_gib


class DeclarationViewSet(viewsets.ModelViewSet):
    queryset = Declaration.objects.all().order_by("-created_at")
    serializer_class = DeclarationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all().order_by("-submitted_at", "-id")
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated, AdvisorOnlySubmission]

    def perform_create(self, serializer):
        submission = serializer.save(submitted_by=self.request.user, status="queued")
        # Enforce active engagement: advisor must be engaged with taxpayer for the declaration
        decl = submission.declaration
        vkn = decl.taxpayer_vkn_tckn
        advisor = getattr(self.request.user, "advisor_profile", None)
        has_engagement = Engagement.objects.filter(
            advisor=advisor, taxpayer__vkn_tckn=vkn, status="active"
        ).exists()
        if not has_engagement:
            submission.status = "rejected"
            submission.save(update_fields=["status"])
            SubmissionLog.objects.create(
                submission=submission,
                level="error",
                message=f"Yetkili danışman ile mükellef arasında aktif sözleşme bulunamadı (VKN/TCKN={vkn}).",
                context={"vkn_tckn": vkn},
            )
            raise PermissionDenied("Aktif sözleşme bulunamadı.")
        # Else: would enqueue send job here; for now mark as sent
        submission.submitted_at = timezone.now()
        submission.status = "sent"
        submission.save(update_fields=["submitted_at", "status"])
        SubmissionLog.objects.create(
            submission=submission,
            level="info",
            message="Gönderim kuyruğa alındı ve test modunda sent olarak işaretlendi.",
            context={"target": submission.target},
        )

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        submission = self.get_object()
        # Basit güvenlik: sahibinin veya oluşturucunun çağırmasını zorunlu kılalım
        if (
            submission.submitted_by_id != request.user.id
            and submission.declaration.created_by_id != request.user.id
        ):
            raise PermissionDenied("Bu gönderimi başlatma yetkiniz yok.")
        external_id, status = send_submission_to_gib(submission)
        return Response({"external_id": external_id, "status": status})

    @action(detail=True, methods=["post"], url_path="validate")
    def validate(self, request, pk=None):
        submission = self.get_object()
        # Basit yetki: kendi gönderimi veya oluşturduğu deklarasyon
        if (
            submission.submitted_by_id != request.user.id
            and submission.declaration.created_by_id != request.user.id
        ):
            raise PermissionDenied("Bu doğrulamayı başlatma yetkiniz yok.")
        # Stub AI: payload boyutu ve basit kurallar
        payload = submission.declaration.payload or {}
        issues = []
        if not payload:
            issues.append("Boş payload")
        if "total" in payload and payload.get("total", 0) < 0:
            issues.append("Toplam tutar negatif olamaz")

        level = "warning" if issues else "info"
        msg = "AI ön kontrol tamamlandı." + (
            f" Uyarılar: {', '.join(issues)}" if issues else ""
        )
        SubmissionLog.objects.create(
            submission=submission, level=level, message=msg, context={"issues": issues}
        )
        return Response({"ok": not issues, "issues": issues})


class SubmissionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubmissionLog.objects.all().order_by("-created_at")
    serializer_class = SubmissionLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Advisors see logs for submissions they own; else see none (tighten later by tenant/company)
        return qs.filter(
            Q(submission__submitted_by=user)
            | Q(submission__declaration__created_by=user)
        )
