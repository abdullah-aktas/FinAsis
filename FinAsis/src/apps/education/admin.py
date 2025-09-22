from django.contrib import admin
from .models import FinancialTermCard
from .models import StudentAnalytics
from .models import Badge, Level, StudentGamificationProgress
from .models import LearningContent
from .models import Forum, ForumTopic, ForumPost, GroupAssignment
from .models import Feedback, Meeting, MeetingInvitation
import openpyxl
from django.http import HttpResponse
from typing import cast
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Register your models here.
admin.site.register(FinancialTermCard)
admin.site.register(StudentAnalytics)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('criteria',)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'score_required')
    search_fields = ('name',)
    list_filter = ('score_required',)

@admin.register(StudentGamificationProgress)
class StudentGamificationProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'total_score', 'level')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    list_filter = ('level',)

def export_as_excel(modeladmin, request, queryset):
    wb: Workbook = openpyxl.Workbook()
    ws = cast(Worksheet, wb.active)
    # Başlıklar
    if queryset.model == LearningContent:
        ws.append(['Başlık', 'Tip', 'Oluşturan', 'Tarih'])
        for obj in queryset:
            ws.append([obj.title, obj.content_type, str(obj.created_by), obj.created_at.strftime('%Y-%m-%d')])
    elif queryset.model == StudentAnalytics:
        ws.append(['Öğrenci', 'Tarih', 'Tamamlanan Ödev', 'Tamamlanan Quiz', 'Başarı Oranı'])
        for obj in queryset:
            ws.append([
                str(obj.student), obj.date.strftime('%Y-%m-%d'),
                obj.completed_assignments, obj.completed_quizzes, obj.success_rate
            ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export.xlsx'
    wb.save(response)
    return response
setattr(export_as_excel, 'short_description', 'Seçili kayıtları Excel olarak dışa aktar')

@admin.register(LearningContent)
class LearningContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'created_by', 'created_at')
    search_fields = ('title', 'description', 'extra_note')
    list_filter = ('content_type', 'created_by')
    date_hierarchy = 'created_at'
    actions = [export_as_excel]

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_by',)
    date_hierarchy = 'created_at'

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'forum', 'created_by', 'created_at')
    search_fields = ('title',)
    list_filter = ('forum', 'created_by')
    date_hierarchy = 'created_at'

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'created_at')
    search_fields = ('content',)
    list_filter = ('author', 'topic')
    date_hierarchy = 'created_at'

@admin.register(GroupAssignment)
class GroupAssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignment', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('assignment', 'created_by')
    date_hierarchy = 'created_at'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'page_url', 'created_at', 'is_answered')
    search_fields = ('user__username', 'email', 'message', 'page_url')
    list_filter = ('is_answered', 'created_at')
    date_hierarchy = 'created_at'

admin.site.unregister(LearningContent)
admin.site.unregister(StudentAnalytics)
admin.site.register(LearningContent, LearningContentAdmin)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'meeting_type', 'status', 'start_time')
    search_fields = ('title', 'description', 'organizer__username')
    list_filter = ('meeting_type', 'status', 'start_time', 'organizer')
    date_hierarchy = 'start_time'

@admin.register(MeetingInvitation)
class MeetingInvitationAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'invitee', 'email', 'status', 'sent_at', 'responded_at')
    search_fields = ('email', 'invitee__username', 'meeting__title', 'token')
    list_filter = ('status', 'sent_at')
