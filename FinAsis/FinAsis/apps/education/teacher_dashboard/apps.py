from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TeacherDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FinAsis.apps.education.teacher_dashboard'
    label = 'teacher_dashboard'
    verbose_name = _('Öğretmen Paneli') 