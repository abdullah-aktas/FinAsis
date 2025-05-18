# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class VirtualCompany(models.Model):
    """Sanal şirket modeli"""
    name = models.CharField(max_length=100, verbose_name="Şirket Adı")
    description = models.TextField(verbose_name="Açıklama")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Bakiye")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='virtual_companies', verbose_name="Sahibi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Sanal Şirket"
        verbose_name_plural = "Sanal Şirketler"
        ordering = ['-created_at']
        app_label = 'virtual_company'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Ürün modeli"""
    name = models.CharField(max_length=100, verbose_name="Ürün Adı")
    description = models.TextField(verbose_name="Açıklama")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    stock = models.IntegerField(default=0, verbose_name="Stok")
    company = models.ForeignKey(VirtualCompany, on_delete=models.CASCADE, related_name='products', verbose_name="Şirket")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['-created_at']
        app_label = 'virtual_company'
    
    def __str__(self):
        return self.name
