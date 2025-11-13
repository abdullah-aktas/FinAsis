"""
Audit Views Package
İç Denetim ve Kontrol Görünümleri
"""
from .control_views import (
    audit_landing,
    control_dashboard,
    risk_assessment_view,
    control_create,
    control_test,
    control_test_all,
    assessment_create,
    audit_trail_report,
    audit_trail_export_xlsx,
    audit_trail_export_pdf,
    compliance_report,
    compliance_export_pdf,
    ajax_control_detail,
    ajax_pending_counts,
    ajax_workflow_approve,
    ajax_workflow_reject,
    ajax_test_control,
    ajax_notifications,
)

from .ai_dashboard_views import (
    ai_dashboard,
    anomaly_detection_view,
    kobi_health_dashboard,
    blockchain_verification_view,
    ajax_risk_trend,
    ajax_recommendations,
    generate_audit_certificate,
)

__all__ = [
    # Control Views
    'audit_landing',
    'control_dashboard',
    'risk_assessment_view',
    'control_create',
    'control_test',
    'control_test_all',
    'assessment_create',
    'audit_trail_report',
    'audit_trail_export_xlsx',
    'audit_trail_export_pdf',
    'compliance_report',
    'compliance_export_pdf',
    'ajax_control_detail',
    'ajax_pending_counts',
    'ajax_workflow_approve',
    'ajax_workflow_reject',
    'ajax_test_control',
    'ajax_notifications',
    # AI Dashboard Views
    'ai_dashboard',
    'anomaly_detection_view',
    'kobi_health_dashboard',
    'blockchain_verification_view',
    'ajax_risk_trend',
    'ajax_recommendations',
    'generate_audit_certificate',
]

