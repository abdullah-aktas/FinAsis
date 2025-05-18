# -*- coding: utf-8 -*-
"""
Muhasebe işlemleri ile ilgili görünümler
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Q
from django.core.exceptions import PermissionDenied

from permissions.decorators import permission_required
from core.base_views import BaseListView, BaseDetailView, BaseCreateView, BaseUpdateView, BaseDeleteView
from core.permissions import HasModelPermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from finance.models import Voucher  # Voucher modelini import et
from finance.forms import VoucherForm 
from ..models import Employee

# Burada muhasebe işlemleri ile ilgili view'ler olacak

class VoucherListView(BaseListView):
    model = Voucher
    template_name = "finance/voucher_list.html"
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        # Önce user.is_authenticated kontrolü yap
        if not user.is_authenticated:
            return Voucher.objects.none()
            
        # Sonra employee ve company ilişkisini kontrol et
        try:
            if hasattr(user, 'employee') and user.employee and user.employee.company:
                return qs.filter(company=user.employee.company)
        except AttributeError:
            pass
            
        return Voucher.objects.none()

class VoucherCreateView(BaseCreateView):
    model = Voucher 
    form_class = VoucherForm
    template_name = "finance/voucher_form.html"
    permission_required = 'finance.add_voucher'
    
    def form_valid(self, form):
        user = self.request.user
        
        # Employee ve company kontrolü
        try:
            if hasattr(user, 'employee') and user.employee and user.employee.company:
                form.instance.company = user.employee.company
                return super().form_valid(form)
        except AttributeError:
            pass
            
        raise PermissionDenied("Bu işlem için yetkiniz bulunmamaktadır.")

@login_required
def dashboard(request):
    # Kullanıcının çalışan profilini al
    employee = Employee.objects.get(user=request.user)
    
    # Kullanıcıya ait voucher'ları getir 
    vouchers = Voucher.objects.filter(employee=employee)

    context = {
        'employee': employee,
        'vouchers': vouchers
    }
    return render(request, 'finance/dashboard.html', context)