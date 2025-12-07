from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    LessonViewSet,
    LearningOutcomeViewSet,
    LessonOutcomeViewSet,
    QuestionViewSet,
    ExamViewSet,
    ExamSubmissionViewSet,
    ClassSessionViewSet,
    AttendanceRecordViewSet,
    PortfolioItemViewSet,
    TournamentViewSet,
    CheatingIncidentViewSet,
    MeetingViewSet,
)

router = DefaultRouter()

# LMS endpoints
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"outcomes", LearningOutcomeViewSet, basename="learning-outcome")
router.register(r"lesson-outcomes", LessonOutcomeViewSet, basename="lesson-outcome")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"exams", ExamViewSet, basename="exam")
router.register(r"exam-submissions", ExamSubmissionViewSet, basename="exam-submission")
router.register(r"class-sessions", ClassSessionViewSet, basename="class-session")
router.register(r"attendance", AttendanceRecordViewSet, basename="attendance")
router.register(r"portfolio", PortfolioItemViewSet, basename="portfolio-item")
router.register(r"tournaments", TournamentViewSet, basename="tournament")
router.register(
    r"cheating-incidents", CheatingIncidentViewSet, basename="cheating-incident"
)
router.register(r"meetings", MeetingViewSet, basename="meeting")

urlpatterns = [
    path("", include(router.urls)),
]
