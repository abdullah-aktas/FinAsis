from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from . import api_role_assignment
from . import views_help

app_name = 'common'

# API URLs
api_urlpatterns = [
    # Role Assignment API
    path('role-assignment/summary/', api_role_assignment.role_assignment_summary, name='api_role_assignment_summary'),
    path('role-assignment/rules/', api_role_assignment.role_assignment_rules, name='api_role_assignment_rules'),
    path('role-assignment/assign-all/', api_role_assignment.assign_roles_all_users, name='api_assign_roles_all_users'),
    path('role-assignment/assign-user/<int:user_id>/', api_role_assignment.assign_roles_single_user, name='api_assign_roles_single_user'),
    path('role-assignment/assign-user-type/<str:user_type_code>/', api_role_assignment.assign_roles_by_user_type, name='api_assign_roles_by_user_type'),
    path('role-assignment/create-groups/', api_role_assignment.create_required_groups_api, name='api_create_required_groups'),
    path('role-assignment/users-without-groups/', api_role_assignment.users_without_groups, name='api_users_without_groups'),
    path('role-assignment/group-stats/', api_role_assignment.group_statistics, name='api_group_statistics'),
    path('role-assignment/my-info/', api_role_assignment.my_role_info, name='api_my_role_info'),
]

# Help System URLs
help_urlpatterns = [
    path('', views_help.help_center, name='help_center'),
    path('module/<str:module_name>/', views_help.help_module, name='help_module'),
    path('faq/', views_help.help_faq, name='help_faq'),
    path('videos/', views_help.help_videos, name='help_videos'),
    path('shortcuts/', views_help.help_shortcuts, name='help_shortcuts'),
    path('quick-start/', views_help.help_quick_start, name='help_quick_start'),
    path('contact/', views_help.help_contact_support, name='help_contact'),
    path('api/search/', views_help.help_search, name='help_api_search'),
    path('api/tooltip/<str:tooltip_key>/', views_help.help_api_tooltip, name='help_api_tooltip'),
    path('api/tour/<str:tour_name>/', views_help.help_api_tour, name='help_api_tour'),
]

urlpatterns = [
    # /common/ -> yardım merkezine yönlendir
    path(
        '',
        RedirectView.as_view(pattern_name='common:help_center', permanent=False),
        name='common_root',
    ),

    path('approvals/request/<str:app_label>/<str:model>/<int:pk>/', views.request_approval, name='request_approval'),
    path('approvals/<int:pk>/<str:action>/', views.approval_action, name='approval_action'),
    path('audit/', views.audit_list, name='audit_list'),

    # API endpoints
    path('api/', include(api_urlpatterns)),

    # Help System
    path('help/', include(help_urlpatterns)),
]
