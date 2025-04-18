from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Employee(models.Model):
    GENDER_CHOICES = (
        ('M', 'Erkek'),
        ('F', 'Kadın'),
    )
    
    MARITAL_STATUS_CHOICES = (
        ('S', 'Bekar'),
        ('M', 'Evli'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    identity_number = models.CharField(max_length=11, unique=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    hire_date = models.DateField()
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    position = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_department')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.base_salary}"

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.period_start} to {self.period_end}"

class Leave(models.Model):
    LEAVE_TYPES = (
        ('ANNUAL', 'Yıllık İzin'),
        ('SICK', 'Hastalık İzni'),
        ('MATERNITY', 'Doğum İzni'),
        ('PATERNITY', 'Babalık İzni'),
        ('UNPAID', 'Ücretsiz İzin'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    reason = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})" 