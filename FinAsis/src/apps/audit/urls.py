# -*- coding: utf-8 -*-
from django.urls import path
from .views import control_views

app_name = 'audit'

urlpatterns = [
    path('', control_views.audit_landing, name='landing'),
    path('controls/dashboard/', control_views.control_dashboard, name='control_dashboard'),
    path('controls/risk-assessment/', control_views.risk_assessment_view, name='risk_assessment'),
    path('controls/create/', control_views.control_create, name='control_create'),
    path('controls/<int:control_id>/test/', control_views.control_test, name='control_test'),
    path('controls/test-all/', control_views.control_test_all, name='control_test_all'),
    path('risk/assessment/create/', control_views.assessment_create, name='assessment_create'),
    path('report/trail/', control_views.audit_trail_report, name='trail_report'),
    path('report/trail/export/xlsx/', control_views.audit_trail_export_xlsx, name='trail_export_xlsx'),
    path('report/trail/export/pdf/', control_views.audit_trail_export_pdf, name='trail_export_pdf'),
    path('report/compliance/', control_views.compliance_report, name='compliance_report'),
    path('report/compliance/export/pdf/', control_views.compliance_export_pdf, name='compliance_export_pdf'),
    # AJAX endpoints
    path('ajax/control/<int:control_id>/', control_views.ajax_control_detail, name='ajax_control_detail'),
    path('ajax/pending-counts/', control_views.ajax_pending_counts, name='ajax_pending_counts'),
    path('ajax/workflow/<int:workflow_id>/approve/', control_views.ajax_workflow_approve, name='ajax_workflow_approve'),
    path('ajax/workflow/<int:workflow_id>/reject/', control_views.ajax_workflow_reject, name='ajax_workflow_reject'),
    path('ajax/control/<int:control_id>/test/', control_views.ajax_test_control, name='ajax_test_control'),
    path('ajax/notifications/', control_views.ajax_notifications, name='ajax_notifications'),
]
