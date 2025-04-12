from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer, CustomerNote, CustomerDocument
from .serializers import CustomerSerializer, CustomerNoteSerializer, CustomerDocumentSerializer

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
