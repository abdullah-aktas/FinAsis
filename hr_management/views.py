from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    Employee, Department, Salary, Payroll, Leave
)

# Create your views here.

# Employee Views
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hr_management/employee_list.html'
    context_object_name = 'employees'

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'hr_management/employee_detail.html'

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    template_name = 'hr_management/employee_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:employee_list')

class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    template_name = 'hr_management/employee_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:employee_list')

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'hr_management/employee_confirm_delete.html'
    success_url = reverse_lazy('hr_management:employee_list')

# Department Views
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'hr_management/department_list.html'
    context_object_name = 'departments'

class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'hr_management/department_detail.html'

class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    template_name = 'hr_management/department_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:department_list')

class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Department
    template_name = 'hr_management/department_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:department_list')

class DepartmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Department
    template_name = 'hr_management/department_confirm_delete.html'
    success_url = reverse_lazy('hr_management:department_list')

# Salary Views
class SalaryListView(LoginRequiredMixin, ListView):
    model = Salary
    template_name = 'hr_management/salary_list.html'
    context_object_name = 'salaries'

class SalaryDetailView(LoginRequiredMixin, DetailView):
    model = Salary
    template_name = 'hr_management/salary_detail.html'

class SalaryCreateView(LoginRequiredMixin, CreateView):
    model = Salary
    template_name = 'hr_management/salary_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:salary_list')

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
class PayrollListView(LoginRequiredMixin, ListView):
    model = Payroll
    template_name = 'hr_management/payroll_list.html'
    context_object_name = 'payrolls'

class PayrollDetailView(LoginRequiredMixin, DetailView):
    model = Payroll
    template_name = 'hr_management/payroll_detail.html'

class PayrollCreateView(LoginRequiredMixin, CreateView):
    model = Payroll
    template_name = 'hr_management/payroll_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:payroll_list')

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
class LeaveListView(LoginRequiredMixin, ListView):
    model = Leave
    template_name = 'hr_management/leave_list.html'
    context_object_name = 'leaves'

class LeaveDetailView(LoginRequiredMixin, DetailView):
    model = Leave
    template_name = 'hr_management/leave_detail.html'

class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = Leave
    template_name = 'hr_management/leave_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:leave_list')

class LeaveUpdateView(LoginRequiredMixin, UpdateView):
    model = Leave
    template_name = 'hr_management/leave_form.html'
    fields = '__all__'
    success_url = reverse_lazy('hr_management:leave_list')

class LeaveDeleteView(LoginRequiredMixin, DeleteView):
    model = Leave
    template_name = 'hr_management/leave_confirm_delete.html'
    success_url = reverse_lazy('hr_management:leave_list')
