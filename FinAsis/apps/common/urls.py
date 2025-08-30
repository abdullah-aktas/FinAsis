from django.urls import path
from . import views
app_name = 'common'
urlpatterns = [
    path('approvals/request/<str:app_label>/<str:model>/<int:pk>/', views.request_approval, name='request_approval'),
    path('approvals/<int:pk>/<str:action>/', views.approval_action, name='approval_action'),
    path('audit/', views.audit_list, name='audit_list'),
]
