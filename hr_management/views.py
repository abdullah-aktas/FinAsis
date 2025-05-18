# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Employee, Department, Salary, Payroll, Leave
from .forms import (
    EmployeeForm, DepartmentForm, SalaryForm,
    PayrollForm, LeaveForm, LeaveApprovalForm
)

# Create your views here.

# Employee Views
class EmployeeListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Employee
    template_name = 'hr_management/employee_list.html'
    context_object_name = 'employees'
    permission_required = 'hr_management.view_employee'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        department = self.request.GET.get('department')
        status = self.request.GET.get('status')

        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(identity_number__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        if department:
            queryset = queryset.filter(department_id=department)

        if status:
            queryset = queryset.filter(is_active=(status == 'active'))

        return queryset.select_related('department')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        return context

class EmployeeDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Employee
    template_name = 'hr_management/employee_detail.html'
    permission_required = 'hr_management.view_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        context['salaries'] = Salary.objects.filter(employee=employee).order_by('-effective_date')
        context['payrolls'] = Payroll.objects.filter(employee=employee).order_by('-period_start')
        context['leaves'] = Leave.objects.filter(employee=employee).order_by('-start_date')
        return context

class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr_management/employee_form.html'
    permission_required = 'hr_management.add_employee'
    success_url = reverse_lazy('hr_management:employee_list')

    def form_valid(self, form):
        messages.success(self.request, _('Çalışan başarıyla oluşturuldu.'))
        return super().form_valid(form)

class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr_management/employee_form.html'
    permission_required = 'hr_management.change_employee'
    success_url = reverse_lazy('hr_management:employee_list')

    def form_valid(self, form):
        messages.success(self.request, _('Çalışan bilgileri başarıyla güncellendi.'))
        return super().form_valid(form)

class EmployeeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Employee
    template_name = 'hr_management/employee_confirm_delete.html'
    permission_required = 'hr_management.delete_employee'
    success_url = reverse_lazy('hr_management:employee_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Çalışan başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

# Department Views
class DepartmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Department
    template_name = 'hr_management/department_list.html'
    context_object_name = 'departments'
    permission_required = 'hr_management.view_department'

    def get_queryset(self):
        return Department.objects.select_related('parent', 'manager')

class DepartmentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Department
    template_name = 'hr_management/department_detail.html'
    permission_required = 'hr_management.view_department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = self.get_object()
        context['employees'] = Employee.objects.filter(department=department)
        context['sub_departments'] = Department.objects.filter(parent=department)
        return context

class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'hr_management/department_form.html'
    permission_required = 'hr_management.add_department'
    success_url = reverse_lazy('hr_management:department_list')

    def form_valid(self, form):
        messages.success(self.request, _('Departman başarıyla oluşturuldu.'))
        return super().form_valid(form)

class DepartmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'hr_management/department_form.html'
    permission_required = 'hr_management.change_department'
    success_url = reverse_lazy('hr_management:department_list')

    def form_valid(self, form):
        messages.success(self.request, _('Departman bilgileri başarıyla güncellendi.'))
        return super().form_valid(form)

class DepartmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Department
    template_name = 'hr_management/department_confirm_delete.html'
    permission_required = 'hr_management.delete_department'
    success_url = reverse_lazy('hr_management:department_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Departman başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

# Salary Views
class SalaryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Salary
    template_name = 'hr_management/salary_list.html'
    context_object_name = 'salaries'
    permission_required = 'hr_management.view_salary'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.GET.get('employee')
        if employee:
            queryset = queryset.filter(employee_id=employee)
        return queryset.select_related('employee')

class SalaryDetailView(LoginRequiredMixin, DetailView):
    model = Salary
    template_name = 'hr_management/salary_detail.html'

class SalaryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Salary
    form_class = SalaryForm
    template_name = 'hr_management/salary_form.html'
    permission_required = 'hr_management.add_salary'
    success_url = reverse_lazy('hr_management:salary_list')

    def form_valid(self, form):
        messages.success(self.request, _('Maaş bilgisi başarıyla oluşturuldu.'))
        return super().form_valid(form)

class SalaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Salary
    template_name = 'hr_management/salary_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:salary_list')

class SalaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Salary
    template_name = 'hr_management/salary_confirm_delete.html'
    success_url = reverse_lazy('hr_management:salary_list')

# Payroll Views
class PayrollListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Payroll
    template_name = 'hr_management/payroll_list.html'
    context_object_name = 'payrolls'
    permission_required = 'hr_management.view_payroll'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        period = self.request.GET.get('period')

        if employee:
            queryset = queryset.filter(employee_id=employee)
        if status:
            queryset = queryset.filter(payment_status=status)
        if period:
            queryset = queryset.filter(period_start__lte=period, period_end__gte=period)

        return queryset.select_related('employee')

class PayrollDetailView(LoginRequiredMixin, DetailView):
    model = Payroll
    template_name = 'hr_management/payroll_detail.html'

class PayrollCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'hr_management/payroll_form.html'
    permission_required = 'hr_management.add_payroll'
    success_url = reverse_lazy('hr_management:payroll_list')

    def form_valid(self, form):
        messages.success(self.request, _('Bordro başarıyla oluşturuldu.'))
        return super().form_valid(form)

class PayrollUpdateView(LoginRequiredMixin, UpdateView):
    model = Payroll
    template_name = 'hr_management/payroll_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:payroll_list')

class PayrollDeleteView(LoginRequiredMixin, DeleteView):
    model = Payroll
    template_name = 'hr_management/payroll_confirm_delete.html'
    success_url = reverse_lazy('hr_management:payroll_list')

# Leave Views
class LeaveListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Leave
    template_name = 'hr_management/leave_list.html'
    context_object_name = 'leaves'
    permission_required = 'hr_management.view_leave'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        employee = self.request.GET.get('employee')
        status = self.request.GET.get('status')
        leave_type = self.request.GET.get('type')

        if employee:
            queryset = queryset.filter(employee_id=employee)
        if status:
            queryset = queryset.filter(status=status)
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)

        return queryset.select_related('employee', 'approved_by')

class LeaveDetailView(LoginRequiredMixin, DetailView):
    model = Leave
    template_name = 'hr_management/leave_detail.html'

class LeaveCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Leave
    form_class = LeaveForm
    template_name = 'hr_management/leave_form.html'
    permission_required = 'hr_management.add_leave'
    success_url = reverse_lazy('hr_management:leave_list')

    def form_valid(self, form):
        messages.success(self.request, _('İzin talebi başarıyla oluşturuldu.'))
        return super().form_valid(form)

class LeaveUpdateView(LoginRequiredMixin, UpdateView):
    model = Leave
    template_name = 'hr_management/leave_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:leave_list')

class LeaveDeleteView(LoginRequiredMixin, DeleteView):
    model = Leave
    template_name = 'hr_management/leave_confirm_delete.html'
    success_url = reverse_lazy('hr_management:leave_list')

@login_required
@require_http_methods(['POST'])
def approve_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    form = LeaveApprovalForm(request.POST, instance=leave)
    
    if form.is_valid():
        leave = form.save(commit=False)
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.save()
        messages.success(request, _('İzin talebi başarıyla onaylandı.'))
    else:
        messages.error(request, _('İzin talebi onaylanırken bir hata oluştu.'))
    
    return redirect('hr_management:leave_detail', pk=leave.pk)

# API Views
@login_required
def employee_stats(request):
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()
    departments = Department.objects.annotate(
        employee_count=Count('employee')
    ).values('name', 'employee_count')
    
    return JsonResponse({
        'total_employees': total_employees,
        'active_employees': active_employees,
        'departments': list(departments)
    })

@login_required
def leave_stats(request):
    current_year = timezone.now().year
    leaves = Leave.objects.filter(
        start_date__year=current_year
    ).values('leave_type').annotate(
        total_days=Sum('total_days')
    )
    
    return JsonResponse({
        'leaves': list(leaves)
    })
