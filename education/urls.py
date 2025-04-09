from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courses', views.CourseViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'quizzes', views.QuizViewSet)
router.register(r'assignments', views.AssignmentViewSet)
router.register(r'submissions', views.StudentSubmissionViewSet, basename='submission')
router.register(r'badges', views.BadgeViewSet)
router.register(r'user-badges', views.UserBadgeViewSet, basename='user-badge')

app_name = 'education'

urlpatterns = [
    path('', views.education_home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('', include(router.urls)),
] 