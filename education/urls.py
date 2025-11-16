# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import FinancialTermCardViewSet
from . import views
from .views import education_home

router = DefaultRouter()
router.register(r'financial-term-cards', FinancialTermCardViewSet, basename='financial-term-card')

app_name = 'education'

urlpatterns = [
    path('', education_home, name='education_home'),
    path('courses/<slug:slug>/', views.course_marketing, name='course_marketing'),
    # Student module (namespaced as 'student')
    path('student/', include(('education.student.urls', 'student'), namespace='student')),
    path('kobi-tutorials/', views.kobi_tutorials, name='kobi_tutorials'),
    # Exam quick prep (with Turkish aliases)
    path('exams/quick-prep/', views.quick_prep, name='quick_prep'),
    path('sınavlar/hızlı-hazırlık/', views.quick_prep, name='hizli_hazirlik'),
    # Meetings pages
    path('meetings/', views.MeetingListView.as_view(), name='meetings_list'),
    path('meetings/add/', views.MeetingCreateView.as_view(), name='meetings_add'),
    path('meetings/<int:pk>/', views.MeetingDetailView.as_view(), name='meetings_detail'),
    path('meetings/<int:pk>/edit/', views.MeetingUpdateView.as_view(), name='meetings_edit'),
    path('meetings/<int:pk>/ics/', views.meeting_ics, name='meetings_ics'),
    path('meetings/<int:pk>/cancel/', views.meeting_cancel, name='meetings_cancel'),
    path('meetings/<int:pk>/presence/', views.meeting_presence, name='meetings_presence'),
    path('meetings/<int:pk>/presence.csv', views.meeting_presence_csv, name='meetings_presence_csv'),
    path('meetings/<int:pk>/presence_totals.csv', views.meeting_presence_totals_csv, name='meetings_presence_totals_csv'),
    path('meetings/<int:pk>/invite/', views.meeting_invite, name='meetings_invite'),
    path('meetings/<int:pk>/presenter/set/', views.meeting_set_presenter, name='meetings_set_presenter'),
    path('meetings/<int:pk>/presenter/clear/', views.meeting_clear_presenter, name='meetings_clear_presenter'),
    path('meetings/<int:pk>/recordings/upload/', views.meeting_upload_recording, name='meetings_upload_recording'),
    path('meetings/<int:pk>/recordings/', views.meeting_recordings, name='meetings_recordings'),
    path('meetings/<int:pk>/recordings/<int:rec_id>/title/', views.meeting_update_recording_title, name='meetings_update_recording_title'),
    path('meetings/<int:pk>/recordings/<int:rec_id>/delete/', views.meeting_delete_recording, name='meetings_delete_recording'),
    path('meetings/rsvp/<str:token>/<str:action>/', views.meeting_rsvp, name='meetings_rsvp'),
    # FinancialTermCard CRUD
    path('financial-term-cards/', views.FinancialTermCardListView.as_view(), name='financialtermcard_list'),
    path('financial-term-cards/add/', views.FinancialTermCardCreateView.as_view(), name='financialtermcard_add'),
    path('financial-term-cards/<int:pk>/', views.FinancialTermCardDetailView.as_view(), name='financialtermcard_detail'),
    path('financial-term-cards/<int:pk>/edit/', views.FinancialTermCardUpdateView.as_view(), name='financialtermcard_edit'),
    path('financial-term-cards/<int:pk>/delete/', views.FinancialTermCardDeleteView.as_view(), name='financialtermcard_delete'),
    # Pruned non-LMS APIs
    path('api/', include(router.urls)),
    # LMS API router
    path('api/lms/', include('education.api_urls')),
] 