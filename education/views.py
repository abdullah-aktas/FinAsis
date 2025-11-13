# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Any, Dict, List

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
import json as _json
from datetime import datetime, timedelta, timezone as _timezone
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    FinancialTermCard,
    Course, Lesson, LearningOutcome, LessonOutcome, Question, Exam,
    ExamSubmission, ClassSession, AttendanceRecord, PortfolioItem, Tournament, CheatingIncident,
)
from .forms import FinancialTermCardForm
from .forms import MeetingForm
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, filters
from django.core.mail import send_mail
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .serializers import (
    CourseSerializer, LessonSerializer, LearningOutcomeSerializer,
    LessonOutcomeSerializer, QuestionSerializer, ExamSerializer,
    ExamSubmissionSerializer, ClassSessionSerializer,
    AttendanceRecordSerializer, PortfolioItemSerializer,
    TournamentSerializer, CheatingIncidentSerializer, MeetingSerializer,
)
from . import services
from .permissions import IsTeacherOfCourseOrReadOnly
from .models import Meeting, MeetingRecording


@dataclass(frozen=True)
class CourseMarketingPage:
    slug: str
    title: str
    hero_subtitle: str
    hero_highlights: List[str]
    video_url: str | None
    audience: List[str]
    delivery: Dict[str, str]
    modules: List[Dict[str, str]]
    outcomes: List[str]
    metrics: List[Dict[str, str]]
    instructor: Dict[str, str]
    syllabus: List[Dict[str, str]]
    faqs: List[Dict[str, str]]


COURSE_MARKETING_PAGES: Dict[str, CourseMarketingPage] = {
    "finance-literacy": CourseMarketingPage(
        slug="finance-literacy",
        title=_("Finansal Okuryazarlık Sertifika Programı"),
        hero_subtitle=_("Öğrenciler, girişimciler ve genç profesyoneller için 6 haftada kapsamlı finans okuryazarlığı."),
        hero_highlights=[
            _("Haftada 4 saat canlı ders + asenkron içerik"),
            _("Gerçek banka ekstresi ve bütçe şablonlarıyla uygulamalı"),
            _("AI destekli quiz ve görevlerle pekiştirme"),
        ],
        video_url=None,
        audience=[
            _("Üniversite öğrencileri ve yeni mezunlar"),
            _("Finans dışı departmanlarda çalışan profesyoneller"),
            _("Genç girişimciler ve KOBİ sahipleri"),
        ],
        delivery={
            "duration": _("6 hafta · 18 saat canlı + 12 saat asenkron"),
            "format": _("Zoom canlı oturumları, FinAsis LMS, FinQuest görev motoru"),
            "language": _("Türkçe · İngilizce altyazı destekli"),
        },
        modules=[
            {
                "icon": "bi-wallet2",
                "title": _("Kişisel Bütçe ve Nakit Akışı"),
                "description": _("Gelir-gider analizi, hedef bazlı bütçeleme, acil durum fonu inşası."),
            },
            {
                "icon": "bi-graph-up",
                "title": _("Yatırım Araçları ve Risk"),
                "description": _("Hisse senedi, fon, tahvil, kripto; risk-getiri dengesi ve portföy oluşturma."),
            },
            {
                "icon": "bi-piggy-bank",
                "title": _("Tasarruf ve Borç Yönetimi"),
                "description": _("Kredi skor yönetimi, borç kapama stratejileri, psikolojik finans."),
            },
            {
                "icon": "bi-lightbulb",
                "title": _("Girişimciler için Finans"),
                "description": _("İş planı finansalları, nakit akışı projeksiyonu, yatırımcı sunumu hazırlama."),
            },
        ],
        outcomes=[
            _("Kişisel ve iş bütçesi hazırlayıp 90 günlük eylem planı oluşturabilecek"),
            _("Yatırım araçlarını risk profiline göre değerlendirebilecek"),
            _("Borç yönetimi ve kredi planlaması yapabilecek"),
            _("Basit finansal tabloları okuyup nakit akışı yorumlayabilecek"),
        ],
        metrics=[
            {"value": "4.8/5", "label": _("Katılımcı memnuniyeti")},
            {"value": "2.300+", "label": _("Mezun öğrenci")},
            {"value": _("₺50K+"), "label": _("Sanallaştırılmış portföy yönetimi")},
        ],
        instructor={
            "name": _("Selin Kaya"),
            "title": _("Finans Eğitmeni · Eski CFO"),
            "bio": _("12 yıllık finans direktörlüğü deneyimi, finansal okuryazarlık programları ve girişim hızlandırıcılarında mentor."),
        },
        syllabus=[
            {"week": _("1. Hafta"), "topic": _("Finansal hedefler ve bütçe incelemesi"), "format": _("Canlı ders + FinQuest görevleri")},
            {"week": _("2. Hafta"), "topic": _("Gelir-gider analizi, bütçe şablonları"), "format": _("Vaka analizi + quiz")},
            {"week": _("3. Hafta"), "topic": _("Yatırım araçları ve risk yönetimi"), "format": _("Portföy simülasyonu")},
            {"week": _("4. Hafta"), "topic": _("Borç ve kredi planlaması"), "format": _("Senaryo çalışması + AI raporu")},
            {"week": _("5. Hafta"), "topic": _("Finansal tabloları okuma"), "format": _("Bilanço ve nakit akışı analizi")},
            {"week": _("6. Hafta"), "topic": _("Girişim finansalları ve yatırımcı sunumu"), "format": _("Pitch hazırlığı + bire bir mentorluk")},
        ],
        faqs=[
            {
                "question": _("Canlı dersleri kaçırırsam ne olur?"),
                "answer": _("Tüm canlı oturumlar kayıt altına alınır ve LMS üzerinden 48 saat içinde yayınlanır."),
            },
            {
                "question": _("Sertifika veriliyor mu?"),
                "answer": _("Tüm görevleri tamamlayan ve final simülasyonunu bitiren katılımcılar FinAsis sertifikası alır."),
            },
            {
                "question": _("Kurumsal paket var mı?"),
                "answer": _("Kurumsal ekipler için özelleştirilmiş içerik ve mentorluk sağlıyoruz. İletişim sayfasından bize ulaşabilirsiniz."),
            },
        ],
    ),
}


def course_marketing(request, slug: str):
    page = COURSE_MARKETING_PAGES.get(slug)
    if page is None:
        raise Http404(f"Course marketing page not found for slug '{slug}'")

    context = {
        "page": page,
        "contact_url": reverse("contact"),
        "enroll_url": reverse("education:student:dashboard") if request.user.is_authenticated else reverse("accounts:login"),
    }
    return render(request, "education/courses/marketing_detail.html", context)


@login_required
def kobi_tutorials(request):
    return render(request, 'education/kobi_tutorials.html')

@login_required
def index(request):
    return render(request, 'education/index.html')

@login_required
def education_home(request):
    # Ana sayfada gösterilecek özet veriler (sadeleştirilmiş)
    context = {
        'card_count': FinancialTermCard.objects.count(),
        'latest_cards': list(FinancialTermCard.objects.order_by('-id')[:5]),
    }
    return render(request, "education/education_home.html", context)

@method_decorator(login_required, name='dispatch')
class FinancialTermCardListView(ListView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_list.html'
    context_object_name = 'cards'

@method_decorator(login_required, name='dispatch')
class FinancialTermCardDetailView(DetailView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_detail.html'
    context_object_name = 'card'

@method_decorator(login_required, name='dispatch')
class FinancialTermCardCreateView(CreateView):
    model = FinancialTermCard
    form_class = FinancialTermCardForm
    template_name = 'education/financialtermcard_form.html'
    success_url = reverse_lazy('education:financialtermcard_list')

@method_decorator(login_required, name='dispatch')
class FinancialTermCardUpdateView(UpdateView):
    model = FinancialTermCard
    form_class = FinancialTermCardForm
    template_name = 'education/financialtermcard_form.html'
    success_url = reverse_lazy('education:financialtermcard_list')

@method_decorator(login_required, name='dispatch')
class FinancialTermCardDeleteView(DeleteView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_confirm_delete.html'
    success_url = reverse_lazy('education:financialtermcard_list')

# Removed non-LMS API viewsets (analytics, badges, levels, gamification, content, forum, group, feedback)

# ---- LMS viewsets ----
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        # Teachers see their courses; students see enrolled courses
        return Course.objects.filter(Q(teacher=user) | Q(students=user)).distinct()

    def perform_create(self, serializer):
        # Teacher set to the creator
        serializer.save(teacher=self.request.user)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Lesson.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        # Ensure creator is teacher of the course
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can add lessons.')
        serializer.save()

class LearningOutcomeViewSet(viewsets.ModelViewSet):
    queryset = LearningOutcome.objects.all()
    serializer_class = LearningOutcomeSerializer
    permission_classes = [permissions.IsAuthenticated]

class LessonOutcomeViewSet(viewsets.ModelViewSet):
    serializer_class = LessonOutcomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return LessonOutcome.objects.filter(
            Q(lesson__course__teacher=user) | Q(lesson__course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        lesson = serializer.validated_data.get('lesson')
        if lesson.course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can map outcomes.')
        serializer.save()

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['points']
    search_fields = ['text']

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Question.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can add questions.')
        serializer.save(created_by=self.request.user)

class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Exam.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can create exams.')
        serializer.save()

class ExamSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        # Students: their own submissions. Teachers: submissions in their courses
        return ExamSubmission.objects.filter(
            Q(student=user) | Q(exam__course__teacher=user)
        ).distinct()

    def perform_create(self, serializer):
        instance = serializer.save(student=self.request.user)
        total, flags = services.grade_submission(instance)
        instance.auto_score = total
        instance.flags = flags
        instance.save(update_fields=["auto_score", "flags"])

    def perform_update(self, serializer):
        instance = serializer.save()
        total, flags = services.grade_submission(instance)
        instance.auto_score = total
        instance.flags = flags
        instance.save(update_fields=["auto_score", "flags"])

class ClassSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return ClassSession.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can create sessions.')
        serializer.save()

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return AttendanceRecord.objects.filter(
            Q(session__course__teacher=user) | Q(student=user)
        ).distinct()

    def perform_create(self, serializer):
        session = serializer.validated_data.get('session')
        if session.course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can record attendance.')
        serializer.save()

class PortfolioItemViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        # Students see their items; teachers see items in their course context
        return PortfolioItem.objects.filter(
            Q(student=user) | Q(course__teacher=user)
        ).distinct()

    def perform_create(self, serializer):
        # Students can create for themselves only
        serializer.save(student=self.request.user)

class TournamentViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Tournament.objects.filter(
            Q(course__teacher=user) | Q(course__students=user) | Q(course__isnull=True)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course and course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can create tournaments for a course.')
        serializer.save()

class CheatingIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = CheatingIncidentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return CheatingIncident.objects.filter(
            Q(submission__student=user) | Q(submission__exam__course__teacher=user)
        ).distinct()

    def perform_create(self, serializer):
        submission = serializer.validated_data.get('submission')
        if submission.exam.course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can log incidents for submissions in their course.')
        serializer.save()


# ---- Meeting Views ----
@method_decorator(login_required, name='dispatch')
class MeetingListView(ListView):
    model = Meeting
    template_name = 'education/meetings_list.html'
    context_object_name = 'meetings'

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(Q(organizer=user) | Q(participants=user)).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        qs = self.get_queryset()
        ctx['upcoming'] = qs.filter(start_time__gte=now).order_by('start_time')
        ctx['past'] = qs.filter(start_time__lt=now).order_by('-start_time')
        return ctx


@method_decorator(login_required, name='dispatch')
class MeetingDetailView(DetailView):
    model = Meeting
    template_name = 'education/meetings_detail.html'
    context_object_name = 'meeting'

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(Q(organizer=user) | Q(participants=user)).distinct()

    def get_context_data(self, **kwargs):  # type: ignore[override]
        from django.conf import settings
        ctx = super().get_context_data(**kwargs)
        mode = getattr(settings, 'MEETINGS_VIDEO_MODE', 'mesh')
        jitsi_domain = getattr(settings, 'MEETINGS_JITSI_DOMAIN', '')
        ice_servers = getattr(settings, 'MEETINGS_ICE_SERVERS', [])
        ctx['video_mode'] = mode
        ctx['jitsi_domain'] = jitsi_domain
        try:
            ctx['ice_servers_json'] = _json.dumps(ice_servers)  # string for safe embedding
        except Exception:
            ctx['ice_servers_json'] = '[]'
        # presenter context
        obj = ctx.get('meeting') or self.get_object()
        presenter_id = getattr(obj, 'presenter_id', None)
        ctx['presenter_id'] = presenter_id
        user = getattr(self.request, 'user', None)
        ctx['is_presenter'] = bool(user and (user == getattr(obj, 'organizer', None) or getattr(user, 'pk', None) == presenter_id))
        # recordings list
        try:
            rec_qs = MeetingRecording.objects.select_related('owner').filter(meeting=obj).order_by('-created_at')
            ctx['recordings'] = list(rec_qs[:10])  # show recent 10; rest is in paginated view
        except Exception:
            ctx['recordings'] = []
        # participants/organizer name map for UI (optional)
        try:
            name = lambda u: (getattr(u, 'get_full_name', lambda: '')() or getattr(u, 'get_username', lambda: '')())
            users_map = {}
            org = getattr(obj, 'organizer', None)
            if org is not None and getattr(org, 'pk', None) is not None:
                users_map[str(getattr(org, 'pk', None))] = name(org)
            parts = getattr(obj, 'participants', None)
            if parts is not None and hasattr(parts, 'all'):
                for u in parts.all():
                    if getattr(u, 'pk', None) is not None:
                        users_map[str(getattr(u, 'pk', None))] = name(u)
            ctx['users_json'] = _json.dumps(users_map)
        except Exception:
            ctx['users_json'] = '{}'

        # Optional Jitsi JWT token for Secure Domain
        ctx['jitsi_jwt'] = ''
        if mode == 'sfu' and jitsi_domain and getattr(settings, 'JITSI_JWT_ENABLED', False):
            app_id = getattr(settings, 'JITSI_JWT_APP_ID', '')
            secret = getattr(settings, 'JITSI_JWT_SECRET', '')
            iss = getattr(settings, 'JITSI_JWT_ISS', 'finasis')
            aud = getattr(settings, 'JITSI_JWT_AUD', 'jitsi')
            ttl = int(getattr(settings, 'JITSI_JWT_TTL', 3600))
            if secret:
                try:
                    import jwt  # type: ignore
                    from typing import cast
                    user = self.request.user
                    obj = cast(Meeting, self.get_object())
                    room = f"finasis-meeting-{obj.pk}"
                    now = datetime.now(tz=_timezone.utc)
                    payload = {
                        'aud': aud,
                        'iss': iss,
                        'sub': jitsi_domain,
                        'room': room,
                        'exp': now + timedelta(seconds=ttl),
                        'nbf': now - timedelta(seconds=5),
                        'context': {
                            'user': {
                                'name': getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'get_username', lambda: '')(),
                                'email': getattr(user, 'email', '') or '',
                                'moderator': bool(user == obj.organizer),
                            }
                        }
                    }
                    headers = {}
                    if app_id:
                        headers['kid'] = app_id
                    token = jwt.encode(payload, secret, algorithm='HS256', headers=headers)
                    ctx['jitsi_jwt'] = token
                except Exception:
                    ctx['jitsi_jwt'] = ''
        return ctx


@login_required
def meeting_set_presenter(request, pk: int):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.user != meeting.organizer:
        return HttpResponse(status=403)
    if request.method == 'POST':
        raw = request.POST.get('presenter_id')
        uid = None
        try:
            uid = int(raw) if raw else None
        except Exception:
            uid = None
        if uid:
            # Ensure the selected is organizer or a participant
            if uid == getattr(meeting.organizer, 'pk', None) or meeting.participants.filter(pk=uid).exists():
                meeting.presenter_id = uid  # type: ignore[attr-defined]
                meeting.save(update_fields=['presenter'])
                # Broadcast change to room via Channels
                try:
                    from asgiref.sync import async_to_sync  # type: ignore
                    from channels.layers import get_channel_layer  # type: ignore
                    channel_layer = get_channel_layer()
                    if channel_layer is not None:
                        async_to_sync(channel_layer.group_send)(
                            f"meeting_{meeting.pk}",
                            {
                                'type': 'broadcast',
                                'payload': {'type': 'moderate', 'from': getattr(request.user, 'pk', None), 'data': {'action': 'set-presenter', 'user_id': uid}},
                                'sender': 'server',
                            }
                        )
                except Exception:
                    pass
    return redirect('education:meetings_detail', pk=meeting.pk)


@login_required
def meeting_clear_presenter(request, pk: int):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.user != meeting.organizer:
        return HttpResponse(status=403)
    if request.method == 'POST':
        meeting.presenter = None
        meeting.save(update_fields=['presenter'])
        # Broadcast clear to room
        try:
            from asgiref.sync import async_to_sync  # type: ignore
            from channels.layers import get_channel_layer  # type: ignore
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                async_to_sync(channel_layer.group_send)(
                    f"meeting_{meeting.pk}",
                    {
                        'type': 'broadcast',
                        'payload': {'type': 'moderate', 'from': getattr(request.user, 'pk', None), 'data': {'action': 'clear-presenter'}},
                        'sender': 'server',
                    }
                )
        except Exception:
            pass
    return redirect('education:meetings_detail', pk=meeting.pk)


@login_required
def meeting_upload_recording(request, pk: int):
    """Accept client-side recording upload and persist as MeetingRecording."""
    meeting = get_object_or_404(Meeting, pk=pk)
    user = request.user
    # Access control: organizer or participant
    if not (user == meeting.organizer or meeting.participants.filter(pk=user.pk).exists()):
        return HttpResponse(status=403)
    if request.method != 'POST':
        return HttpResponse(status=405)
    from django.http import JsonResponse
    from .models import MeetingRecording
    f = request.FILES.get('file')
    if not f:
        return JsonResponse({'ok': False, 'error': 'no_file'}, status=400)
    kind = request.POST.get('kind') or ''
    dur = request.POST.get('duration_ms')
    try:
        duration_ms = int(dur) if dur else None
    except Exception:
        duration_ms = None
    title = request.POST.get('title') or ''
    rec = MeetingRecording.objects.create(
        meeting=meeting,
        owner=user,
        file=f,
        kind=kind,
        duration_ms=duration_ms,
        title=title,
    )
    # Return file URL
    url = getattr(rec.file, 'url', '')
    return JsonResponse({'ok': True, 'id': rec.pk, 'url': url})


@login_required
def meeting_delete_recording(request, pk: int, rec_id: int):
    """Delete a specific MeetingRecording. Only organizer or owner can delete."""
    meeting = get_object_or_404(Meeting, pk=pk)
    rec = get_object_or_404(MeetingRecording, pk=rec_id)
    user = request.user
    # Access control and ownership check
    if not (user == meeting.organizer or user == rec.owner):
        return HttpResponse(status=403)
    # Ensure recording belongs to this meeting
    if getattr(rec, 'meeting_id', None) != meeting.pk:
        return HttpResponse(status=404)
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        # Best-effort remove file from storage, then delete DB row
        try:
            f = getattr(rec, 'file', None)
            if f and getattr(f, 'name', None):
                f.delete(save=False)
        except Exception:
            pass
        rec.delete()
    except Exception:
        # Even if delete fails, redirect back to detail without crashing
        pass
    return redirect('education:meetings_detail', pk=meeting.pk)


@login_required
def meeting_recordings(request, pk: int):
    """Paginated list of recordings for a meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    user = request.user
    if not (user == meeting.organizer or meeting.participants.filter(pk=user.pk).exists()):
        return HttpResponse(status=403)
    qs = MeetingRecording.objects.select_related('owner').filter(meeting=meeting).order_by('-created_at')
    page = request.GET.get('page') or 1
    paginator = Paginator(qs, 15)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'education/meetings_recordings.html', {
        'meeting': meeting,
        'page_obj': page_obj,
        'paginator': paginator,
        'recordings': page_obj.object_list,
    })


@login_required
def meeting_update_recording_title(request, pk: int, rec_id: int):
    """Update title for a specific MeetingRecording. Organizer or owner only."""
    meeting = get_object_or_404(Meeting, pk=pk)
    rec = get_object_or_404(MeetingRecording, pk=rec_id)
    user = request.user
    if not (user == meeting.organizer or user == rec.owner):
        return HttpResponse(status=403)
    if getattr(rec, 'meeting_id', None) != meeting.pk:
        return HttpResponse(status=404)
    if request.method != 'POST':
        return HttpResponse(status=405)
    title = (request.POST.get('title') or '').strip()
    # Limit title length client-safely
    if len(title) > 200:
        title = title[:200]
    rec.title = title
    rec.save(update_fields=['title'])
    return redirect('education:meetings_detail', pk=meeting.pk)


@method_decorator(login_required, name='dispatch')
class MeetingCreateView(CreateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'education/meetings_form.html'
    success_url = reverse_lazy('education:meetings_list')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class MeetingUpdateView(UpdateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'education/meetings_form.html'
    success_url = reverse_lazy('education:meetings_list')

    def get_queryset(self):
        # Only organizer can update
        return Meeting.objects.filter(organizer=self.request.user)


# DRF API for meetings
class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> Any:
        user = self.request.user
        return Meeting.objects.filter(Q(organizer=user) | Q(participants=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


def meeting_ics(request, pk: int):
    meeting = get_object_or_404(Meeting, pk=pk)
    # Access control: organizer or participant
    user = request.user
    if not user.is_authenticated or not (user == meeting.organizer or meeting.participants.filter(pk=user.pk).exists()):
        return HttpResponse(status=403)
    dtstamp = timezone.now().strftime('%Y%m%dT%H%M%SZ')
    dtstart = meeting.start_time.strftime('%Y%m%dT%H%M%SZ')
    dtend = (meeting.end_time or (meeting.start_time)).strftime('%Y%m%dT%H%M%SZ')
    uid = f"meeting-{meeting.pk}@finasis"
    # Sanitize description and URL for ICS
    desc = (meeting.description or "").replace("\n", " ")
    url = meeting.join_url or ""
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//FinAsis//Education Meetings//TR',
        'BEGIN:VEVENT',
        f'DTSTAMP:{dtstamp}',
        f'UID:{uid}',
        f'SUMMARY:{meeting.title}',
        f'DESCRIPTION:{desc}',
        f'DTSTART:{dtstart}',
        f'DTEND:{dtend}',
        f'URL:{url}',
        'END:VEVENT',
        'END:VCALENDAR',
    ]
    content = "\r\n".join(lines)
    resp = HttpResponse(content, content_type='text/calendar; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="meeting-{meeting.pk}.ics"'
    return resp


@login_required
def meeting_cancel(request, pk: int):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.user != meeting.organizer:
        return HttpResponse(status=403)
    if request.method == 'POST':
        meeting.status = 'canceled'
        meeting.save(update_fields=['status'])
        return redirect('education:meetings_detail', pk=meeting.pk)
    return redirect('education:meetings_detail', pk=meeting.pk)


@login_required
def meeting_presence(request, pk: int):
    """HTML report of MeetingPresence entries for a meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    user = request.user
    if not (user == meeting.organizer or meeting.participants.filter(pk=user.pk).exists()):
        return HttpResponse(status=403)
    from .models import MeetingPresence
    from django.utils import timezone as dj_tz

    def fmt_hms(total_sec: int) -> str:
        if total_sec < 0:
            total_sec = 0
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return (f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}")

    now = dj_tz.now()
    qs = MeetingPresence.objects.select_related('user').filter(meeting=meeting).order_by('user_id', 'joined_at')

    presence_rows = []
    per_user = {}
    ongoing_sessions = 0
    total_seconds_all = 0
    for p in qs:
        joined = p.joined_at
        left = p.left_at
        effective_left = left or now
        if left is None:
            ongoing_sessions += 1
        duration_seconds = int((effective_left - joined).total_seconds()) if (joined and effective_left) else 0
        total_seconds_all += max(duration_seconds, 0)
        # Per-user totals
        uname = getattr(p.user, 'get_full_name', lambda: '')() or getattr(p.user, 'get_username', lambda: '')()
        uid = getattr(p.user, 'pk', None)
        per_user.setdefault(uid, {'user_display': uname, 'sessions': 0, 'total_seconds': 0})
        per_user[uid]['sessions'] += 1
        per_user[uid]['total_seconds'] += max(duration_seconds, 0)

        presence_rows.append({
            'user_display': uname,
            'joined_at': joined,
            'left_at': left,  # keep None if ongoing to display '-'
            'duration_seconds': max(duration_seconds, 0),
            'duration_hms': fmt_hms(max(duration_seconds, 0)),
        })

    per_user_totals = []
    for _uid, entry in per_user.items():
        per_user_totals.append({
            'user_display': entry['user_display'],
            'sessions': entry['sessions'],
            'total_seconds': entry['total_seconds'],
            'total_hms': fmt_hms(entry['total_seconds']),
        })

    # Sort users by total time desc
    per_user_totals.sort(key=lambda x: x['total_seconds'], reverse=True)

    summary = {
        'total_participants': len(per_user_totals),
        'total_sessions': len(presence_rows),
        'total_seconds': total_seconds_all,
        'total_hms': fmt_hms(total_seconds_all),
        'ongoing_sessions': ongoing_sessions,
    }

    return render(request, 'education/meetings_presence.html', {
        'meeting': meeting,
        'presence_rows': presence_rows,
        'per_user_totals': per_user_totals,
        'summary': summary,
    })


@login_required
def meeting_presence_csv(request, pk: int):
    """CSV export for MeetingPresence entries."""
    meeting = get_object_or_404(Meeting, pk=pk)
    user = request.user
    if not (user == meeting.organizer or meeting.participants.filter(pk=user.pk).exists()):
        return HttpResponse(status=403)
    from .models import MeetingPresence
    import csv
    from io import StringIO
    from django.utils import timezone as dj_tz
    presences = MeetingPresence.objects.select_related('user').filter(meeting=meeting).order_by('user_id', 'joined_at')

    def fmt_hms(total_sec: int) -> str:
        if total_sec is None:
            return ''
        if total_sec < 0:
            total_sec = 0
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return (f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}")

    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(['user_id', 'user', 'joined_at', 'left_at', 'duration_seconds', 'duration_hms'])
    for p in presences:
        joined = p.joined_at
        left = p.left_at
        if left is None:
            left = dj_tz.now()
        duration = int((left - joined).total_seconds()) if (joined and left) else None
        writer.writerow([
            getattr(p.user, 'pk', ''),
            getattr(p.user, 'get_username', lambda: '')(),
            joined,
            p.left_at,
            duration if duration is not None else '',
            fmt_hms(duration) if duration is not None else '',
        ])
    resp = HttpResponse(out.getvalue(), content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="meeting_{meeting.pk}_presence.csv"'
    return resp


@login_required
def meeting_presence_totals_csv(request, pk: int):
    """CSV export for per-user presence totals for a meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    user = request.user
    if not (user == meeting.organizer or meeting.participants.filter(pk=user.pk).exists()):
        return HttpResponse(status=403)
    from .models import MeetingPresence
    import csv
    from io import StringIO
    from django.utils import timezone as dj_tz

    def fmt_hms(total_sec: int) -> str:
        if total_sec < 0:
            total_sec = 0
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return (f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}")

    qs = MeetingPresence.objects.select_related('user').filter(meeting=meeting).order_by('user_id', 'joined_at')
    now = dj_tz.now()
    per_user: dict[int, dict] = {}
    for p in qs:
        uid = getattr(p.user, 'pk', None)
        uname = getattr(p.user, 'get_full_name', lambda: '')() or getattr(p.user, 'get_username', lambda: '')()
        if uid is None:
            # skip if user missing
            continue
        joined = p.joined_at
        left = p.left_at or now
        duration_seconds = int((left - joined).total_seconds()) if (joined and left) else 0
        entry = per_user.setdefault(uid, {'user_display': uname, 'sessions': 0, 'total_seconds': 0})
        entry['sessions'] += 1
        entry['total_seconds'] += max(duration_seconds, 0)

    # Prepare CSV
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(['user_id', 'user', 'sessions', 'total_seconds', 'total_hms'])
    for uid, entry in per_user.items():
        writer.writerow([
            uid,
            entry['user_display'],
            entry['sessions'],
            entry['total_seconds'],
            fmt_hms(entry['total_seconds']),
        ])
    resp = HttpResponse(out.getvalue(), content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="meeting_{meeting.pk}_presence_totals.csv"'
    return resp


@login_required
def meeting_invite(request, pk: int):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.user != meeting.organizer:
        return HttpResponse(status=403)
    from .forms import MeetingInvitationForm
    if request.method == 'POST':
        form = MeetingInvitationForm(request.POST)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.meeting = meeting
            inv.invited_by = request.user
            inv.save()
            # Send email if address provided (simple stub)
            if inv.email:
                try:
                    send_mail(
                        subject=f"Toplantı daveti: {meeting.title}",
                        message=f"Toplantı linki: {meeting.join_url or ''}\nRSVP: /education/meetings/rsvp/{inv.token}/accept",
                        from_email=None,
                        recipient_list=[inv.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
            return redirect('education:meetings_detail', pk=meeting.pk)
    else:
        form = MeetingInvitationForm()
    return render(request, 'education/meeting_invite_form.html', {'form': form, 'meeting': meeting})


def meeting_rsvp(request, token: str, action: str):
    from .models import MeetingInvitation
    inv = get_object_or_404(MeetingInvitation, token=token)
    if action == 'accept':
        inv.status = 'accepted'
        if request.user.is_authenticated:
            inv.invitee = request.user
            # add to participants
            inv.meeting.participants.add(request.user)
        inv.responded_at = timezone.now()
        inv.save(update_fields=['status', 'invitee', 'responded_at'])
    elif action == 'decline':
        inv.status = 'declined'
        inv.responded_at = timezone.now()
        inv.save(update_fields=['status', 'responded_at'])
    return redirect('education:meetings_detail', pk=inv.meeting.pk)