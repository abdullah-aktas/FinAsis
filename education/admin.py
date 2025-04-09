from django.contrib import admin
from .models import (
    Course, Lesson, Quiz, QuizQuestion,
    Assignment, StudentSubmission, PerformanceTracking,
    Badge, UserBadge
)

class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'level', 'duration')
    list_filter = ('level', 'teacher')
    search_fields = ('title', 'description')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration')
    list_filter = ('course',)
    search_fields = ('title', 'content')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'time_limit', 'passing_score')
    list_filter = ('lesson__course',)
    search_fields = ('title', 'description')
    inlines = [QuizQuestionInline]

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'due_date', 'max_score')
    list_filter = ('lesson__course',)
    search_fields = ('title', 'description')

@admin.register(StudentSubmission)
class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'score')
    list_filter = ('assignment__lesson__course', 'submitted_at')
    search_fields = ('student__username', 'assignment__title')

@admin.register(PerformanceTracking)
class PerformanceTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completion', 'quiz_score', 'assignment_score')
    list_filter = ('completion', 'lesson__course')
    search_fields = ('user__username', 'lesson__title')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'criteria')
    search_fields = ('name', 'description')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge', 'earned_at')
    search_fields = ('user__username', 'badge__name')
