# -*- coding: utf-8 -*-
from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    stock_symbol = models.CharField(max_length=10, unique=True)
    sector = models.CharField(max_length=50)
    market_cap = models.DecimalField(max_digits=15, decimal_places=2)
    stock_price = models.DecimalField(max_digits=10, decimal_places=2)
    volatility = models.FloatField(default=0.5)
    performance = models.FloatField(default=0.0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.stock_symbol})"

class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    performance = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

class Employee(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    performance = models.FloatField(default=0.0)
    hire_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.position} at {self.department.company.name}" 