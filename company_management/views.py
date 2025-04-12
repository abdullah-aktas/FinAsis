from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Company, Department, Employee
from .forms import CompanyForm, DepartmentForm, EmployeeForm

@login_required
def company_list(request):
    """Şirket listesi görünümü"""
    companies = Company.objects.all()
    
    # Arama
    search_query = request.GET.get('search', '')
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(tax_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Sayfalama
    paginator = Paginator(companies, 10)
    page = request.GET.get('page')
    companies = paginator.get_page(page)
    
    return render(request, 'company_management/company_list.html', {
        'companies': companies,
        'search_query': search_query
    })

@login_required
def company_detail(request, pk):
    """Şirket detay görünümü"""
    company = get_object_or_404(Company, pk=pk)
    departments = company.departments.all()
    employees = company.employees.all()
    
    return render(request, 'company_management/company_detail.html', {
        'company': company,
        'departments': departments,
        'employees': employees
    })

@login_required
def company_create(request):
    """Şirket oluşturma görünümü"""
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, 'Şirket başarıyla oluşturuldu.')
            return redirect('company_management:company_detail', pk=company.pk)
    else:
        form = CompanyForm()
    
    return render(request, 'company_management/company_form.html', {
        'form': form,
        'title': 'Yeni Şirket'
    })

@login_required
def company_edit(request, pk):
    """Şirket düzenleme görünümü"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Şirket başarıyla güncellendi.')
            return redirect('company_management:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    
    return render(request, 'company_management/company_form.html', {
        'form': form,
        'company': company,
        'title': 'Şirketi Düzenle'
    })

@login_required
def company_delete(request, pk):
    """Şirket silme görünümü"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        company.delete()
        messages.success(request, 'Şirket başarıyla silindi.')
        return redirect('company_management:company_list')
    
    return render(request, 'company_management/company_confirm_delete.html', {
        'company': company
    })

@login_required
def department_list(request):
    """Departman listesi görünümü"""
    departments = Department.objects.all()
    
    # Arama
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )
    
    # Sayfalama
    paginator = Paginator(departments, 10)
    page = request.GET.get('page')
    departments = paginator.get_page(page)
    
    return render(request, 'company_management/department_list.html', {
        'departments': departments,
        'search_query': search_query
    })

@login_required
def department_detail(request, pk):
    """Departman detay görünümü"""
    department = get_object_or_404(Department, pk=pk)
    employees = department.employees.all()
    
    return render(request, 'company_management/department_detail.html', {
        'department': department,
        'employees': employees
    })

@login_required
def department_create(request):
    """Departman oluşturma görünümü"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, 'Departman başarıyla oluşturuldu.')
            return redirect('company_management:department_detail', pk=department.pk)
    else:
        form = DepartmentForm()
    
    return render(request, 'company_management/department_form.html', {
        'form': form,
        'title': 'Yeni Departman'
    })

@login_required
def department_edit(request, pk):
    """Departman düzenleme görünümü"""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departman başarıyla güncellendi.')
            return redirect('company_management:department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'company_management/department_form.html', {
        'form': form,
        'department': department,
        'title': 'Departmanı Düzenle'
    })

@login_required
def department_delete(request, pk):
    """Departman silme görünümü"""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Departman başarıyla silindi.')
        return redirect('company_management:department_list')
    
    return render(request, 'company_management/department_confirm_delete.html', {
        'department': department
    })

@login_required
def employee_list(request):
    """Çalışan listesi görünümü"""
    employees = Employee.objects.all()
    
    # Arama
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(position__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )
    
    # Sayfalama
    paginator = Paginator(employees, 10)
    page = request.GET.get('page')
    employees = paginator.get_page(page)
    
    return render(request, 'company_management/employee_list.html', {
        'employees': employees,
        'search_query': search_query
    })

@login_required
def employee_detail(request, pk):
    """Çalışan detay görünümü"""
    employee = get_object_or_404(Employee, pk=pk)
    
    return render(request, 'company_management/employee_detail.html', {
        'employee': employee
    })

@login_required
def employee_create(request):
    """Çalışan oluşturma görünümü"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, 'Çalışan başarıyla oluşturuldu.')
            return redirect('company_management:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'company_management/employee_form.html', {
        'form': form,
        'title': 'Yeni Çalışan'
    })

@login_required
def employee_edit(request, pk):
    """Çalışan düzenleme görünümü"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Çalışan başarıyla güncellendi.')
            return redirect('company_management:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'company_management/employee_form.html', {
        'form': form,
        'employee': employee,
        'title': 'Çalışanı Düzenle'
    })

@login_required
def employee_delete(request, pk):
    """Çalışan silme görünümü"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Çalışan başarıyla silindi.')
        return redirect('company_management:employee_list')
    
    return render(request, 'company_management/employee_confirm_delete.html', {
        'employee': employee
    })
