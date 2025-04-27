from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VirtualCompany, Product
from .serializers import VirtualCompanySerializer, ProductSerializer
from django.db.models import Sum
from rest_framework import status

# Create your views here.

class VirtualCompanyViewSet(viewsets.ModelViewSet):
    """Sanal şirket view seti"""
    queryset = VirtualCompany.objects.all()
    serializer_class = VirtualCompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VirtualCompany.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        company = self.get_object()
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        company = self.get_object()
        products = company.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def total_inventory_value(self, request, pk=None):
        company = self.get_object()
        total_value = company.products.aggregate(
            total=Sum('price') * Sum('stock')
        )['total'] or 0
        return Response({'total_inventory_value': total_value})

class ProductViewSet(viewsets.ModelViewSet):
    """Ürün view seti"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.filter(company__owner=self.request.user)
    
    def perform_create(self, serializer):
        company = VirtualCompany.objects.get(owner=self.request.user)
        serializer.save(company=company)
