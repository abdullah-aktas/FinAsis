from django.urls import path
from . import views

app_name = "hr_management"

urlpatterns = [
    # Çalışan listesi
    path('employee/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employee/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employee/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employee/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    # Departman listesi
    path('department/', views.DepartmentListView.as_view(), name='department_list'),
    path('department/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('department/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('department/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('department/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Maaş listesi
    path('salary/', views.SalaryListView.as_view(), name='salary_list'),
    path('salary/<int:pk>/', views.SalaryDetailView.as_view(), name='salary_detail'),
    path('salary/create/', views.SalaryCreateView.as_view(), name='salary_create'),
    path('salary/<int:pk>/update/', views.SalaryUpdateView.as_view(), name='salary_update'),
    path('salary/<int:pk>/delete/', views.SalaryDeleteView.as_view(), name='salary_delete'),
    
    # Bordro listesi
    path('payroll/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payroll/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
    path('payroll/create/', views.PayrollCreateView.as_view(), name='payroll_create'),
    path('payroll/<int:pk>/update/', views.PayrollUpdateView.as_view(), name='payroll_update'),
    path('payroll/<int:pk>/delete/', views.PayrollDeleteView.as_view(), name='payroll_delete'),
    
    # İzin listesi
    path('leave/', views.LeaveListView.as_view(), name='leave_list'),
    path('leave/<int:pk>/', views.LeaveDetailView.as_view(), name='leave_detail'),
    path('leave/create/', views.LeaveCreateView.as_view(), name='leave_create'),
    path('leave/<int:pk>/update/', views.LeaveUpdateView.as_view(), name='leave_update'),
    path('leave/<int:pk>/delete/', views.LeaveDeleteView.as_view(), name='leave_delete'),
] 