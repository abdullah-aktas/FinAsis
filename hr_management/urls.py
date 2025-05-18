# -*- coding: utf-8 -*-
"""
HR Management Modülü - URL Yapılandırması
---------------------------------------
Bu dosya, İnsan Kaynakları Yönetimi modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/hr/ - Ana HR API endpoint'i
- /api/v1/hr/employees/ - Çalışan yönetimi
- /api/v1/hr/departments/ - Departman yönetimi
- /api/v1/hr/salaries/ - Maaş yönetimi
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'hr_management'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'salaries', views.SalaryViewSet, basename='salary')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Çalışan Yönetimi
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/<uuid:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<uuid:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<uuid:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),
    
    # Departman Yönetimi
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('departments/<uuid:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department-create'),
    path('departments/<uuid:pk>/update/', views.DepartmentUpdateView.as_view(), name='department-update'),
    path('departments/<uuid:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department-delete'),
    
    # Maaş Yönetimi
    path('salaries/', views.SalaryListView.as_view(), name='salary-list'),
    path('salaries/<uuid:pk>/', views.SalaryDetailView.as_view(), name='salary-detail'),
    path('salaries/create/', views.SalaryCreateView.as_view(), name='salary-create'),
    path('salaries/<uuid:pk>/update/', views.SalaryUpdateView.as_view(), name='salary-update'),
    path('salaries/<uuid:pk>/delete/', views.SalaryDeleteView.as_view(), name='salary-delete'),
    
    # Bordro Yönetimi
    path('payrolls/', views.PayrollListView.as_view(), name='payroll-list'),
    path('payrolls/<uuid:pk>/', views.PayrollDetailView.as_view(), name='payroll-detail'),
    path('payrolls/create/', views.PayrollCreateView.as_view(), name='payroll-create'),
    path('payrolls/<uuid:pk>/update/', views.PayrollUpdateView.as_view(), name='payroll-update'),
    path('payrolls/<uuid:pk>/delete/', views.PayrollDeleteView.as_view(), name='payroll-delete'),
    
    # HR Raporları
    path('reports/employee-analysis/', views.EmployeeAnalysisView.as_view(), name='employee-analysis'),
    path('reports/salary-analysis/', views.SalaryAnalysisView.as_view(), name='salary-analysis'),
    path('reports/department-analysis/', views.DepartmentAnalysisView.as_view(), name='department-analysis'),
] 