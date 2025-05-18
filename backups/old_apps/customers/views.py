# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer, CustomerNote, CustomerDocument
from .serializers import CustomerSerializer, CustomerNoteSerializer, CustomerDocumentSerializer
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerNoteViewSet(viewsets.ModelViewSet):
    queryset = CustomerNote.objects.all()
    serializer_class = CustomerNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomerNote.objects.filter(customer_id=self.kwargs['customer_pk'])

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer_pk'])
        serializer.save(customer=customer, created_by=self.request.user)

class CustomerDocumentViewSet(viewsets.ModelViewSet):
    queryset = CustomerDocument.objects.all()
    serializer_class = CustomerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomerDocument.objects.filter(customer_id=self.kwargs['customer_pk'])

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer_pk'])
        serializer.save(customer=customer, created_by=self.request.user)

# Template-based views
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_management/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            messages.success(request, 'Müşteri başarıyla oluşturuldu.')
            return redirect('customer_management:customer_list')
        else:
            messages.error(request, 'Müşteri oluşturulurken hata oluştu.')
    return render(request, 'customer_management/customer_form.html')

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    notes = CustomerNote.objects.filter(customer=customer)
    documents = CustomerDocument.objects.filter(customer=customer)
    return render(request, 'customer_management/customer_detail.html', {
        'customer': customer,
        'notes': notes,
        'documents': documents
    })

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        serializer = CustomerSerializer(customer, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Müşteri başarıyla güncellendi.')
            return redirect('customer_management:customer_detail', pk=pk)
        else:
            messages.error(request, 'Müşteri güncellenirken hata oluştu.')
    return render(request, 'customer_management/customer_form.html', {'customer': customer})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Müşteri başarıyla silindi.')
        return redirect('customer_management:customer_list')
    return render(request, 'customer_management/customer_confirm_delete.html', {'customer': customer})
