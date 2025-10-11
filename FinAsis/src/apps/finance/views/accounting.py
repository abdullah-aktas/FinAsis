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

from src.apps.permissions.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import Voucher  # Voucher modelini import et
from ..forms import VoucherForm 
from ..models import Employee

# Burada muhasebe işlemleri ile ilgili view'ler olacak

class VoucherListView(ListView):
    model = Voucher
    template_name = "finance/voucher_list.html"
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Kullanıcı doğrulama
        if not user.is_authenticated:
            return Voucher.objects.none()
        # İlgili çalışan kaydını bul ve ona ait fişleri göster
        employee = Employee.objects.filter(user=user).first()
        if not employee:
            return Voucher.objects.none()
        return qs.filter(employee=employee)

class VoucherCreateView(CreateView):
    model = Voucher 
    form_class = VoucherForm
    template_name = "finance/voucher_form.html"
    permission_required = 'finance.add_voucher'
    
    def form_valid(self, form):
        user = self.request.user
        # Kullanıcının bağlı çalışan kaydı üzerinden ilişkilendir
        employee = Employee.objects.filter(user=user).first()
        if not employee:
            raise PermissionDenied("Bu işlem için yetkiniz bulunmamaktadır.")
        form.instance.employee = employee
        return super().form_valid(form)

class VoucherDetailView(DetailView):
    model = Voucher
    template_name = "finance/voucher_detail.html"
    context_object_name = 'voucher'

class VoucherUpdateView(UpdateView):
    model = Voucher
    form_class = VoucherForm
    template_name = "finance/voucher_form.html"
    success_url = reverse_lazy('finance:voucher_list')

class VoucherDeleteView(DeleteView):
    model = Voucher
    template_name = "finance/voucher_confirm_delete.html"
    success_url = reverse_lazy('finance:voucher_list')

@login_required
def dashboard(request):
    # Kullanıcının çalışan profilini güvenli şekilde al
    employee = Employee.objects.filter(user=request.user).first()
    vouchers = Voucher.objects.filter(employee=employee) if employee else []
    context = {
        'employee': employee,
        'vouchers': vouchers,
    }
    return render(request, 'finance/dashboard.html', context)