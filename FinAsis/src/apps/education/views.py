# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
import json as _json
from datetime import datetime, timedelta, timezone as _timezone
from django.urls import reverse_lazy
from .models import (
    FinancialTermCard,
    Course, Lesson, LearningOutcome, LessonOutcome, Question, Exam,
    ExamSubmission, ClassSession, AttendanceRecord, PortfolioItem, Tournament, CheatingIncident,
)
from .forms import FinancialTermCardForm
from .forms import MeetingForm
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, filters
from typing import Any
from django.core.mail import send_mail
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .serializers import (
    CourseSerializer, LessonSerializer, LearningOutcomeSerializer,
    LessonOutcomeSerializer, QuestionSerializer, ExamSerializer,
    ExamSubmissionSerializer, ClassSessionSerializer,
    AttendanceRecordSerializer, PortfolioItemSerializer,
    TournamentSerializer, CheatingIncidentSerializer, MeetingSerializer,
)
from . import services
from .permissions import IsTeacherOfCourseOrReadOnly
from .models import Meeting
 

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
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//FinAsis//Education Meetings//TR',
        'BEGIN:VEVENT',
        f'DTSTAMP:{dtstamp}',
        f'UID:{uid}',
        f'SUMMARY:{meeting.title}',
        f'DESCRIPTION:{(meeting.description or '').replace('\n',' ')}',
        f'DTSTART:{dtstart}',
        f'DTEND:{dtend}',
        f'URL:{meeting.join_url or ''}',
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