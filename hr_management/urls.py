from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'hr_management'

urlpatterns = [
    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<uuid:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<uuid:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),

    # Department URLs
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<uuid:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<uuid:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<uuid:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    # Salary URLs
    path('salaries/', views.SalaryListView.as_view(), name='salary_list'),
    path('salaries/<uuid:pk>/', views.SalaryDetailView.as_view(), name='salary_detail'),
    path('salaries/create/', views.SalaryCreateView.as_view(), name='salary_create'),
    path('salaries/<uuid:pk>/update/', views.SalaryUpdateView.as_view(), name='salary_update'),
    path('salaries/<uuid:pk>/delete/', views.SalaryDeleteView.as_view(), name='salary_delete'),

    # Payroll URLs
    path('payrolls/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payrolls/<uuid:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
    path('payrolls/create/', views.PayrollCreateView.as_view(), name='payroll_create'),
    path('payrolls/<uuid:pk>/update/', views.PayrollUpdateView.as_view(), name='payroll_update'),
    path('payrolls/<uuid:pk>/delete/', views.PayrollDeleteView.as_view(), name='payroll_delete'),

    # Leave URLs
    path('leaves/', views.LeaveListView.as_view(), name='leave_list'),
    path('leaves/<uuid:pk>/', views.LeaveDetailView.as_view(), name='leave_detail'),
    path('leaves/create/', views.LeaveCreateView.as_view(), name='leave_create'),
    path('leaves/<uuid:pk>/update/', views.LeaveUpdateView.as_view(), name='leave_update'),
    path('leaves/<uuid:pk>/delete/', views.LeaveDeleteView.as_view(), name='leave_delete'),
    path('leaves/<uuid:pk>/approve/', views.approve_leave, name='leave_approve'),

    # API URLs
    path('api/employee-stats/', views.employee_stats, name='employee_stats'),
    path('api/leave-stats/', views.leave_stats, name='leave_stats'),
] 