from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum
from django.core.cache import cache
from .models import Product, StockMovement, ProductionOrder, BillOfMaterials, QualityControl
from .serializers import (
    ProductSerializer, StockMovementSerializer, ProductionOrderSerializer,
    BillOfMaterialsSerializer, QualityControlSerializer
)
from .services import ProductService, ProductionService, QualityControlService

@login_required
def company_home(request):
    return render(request, 'virtual_company/home.html')

@login_required
def create_company(request):
    return render(request, 'virtual_company/create_company.html')

@login_required
def my_company(request):
    return render(request, 'virtual_company/my_company.html')

@login_required
def market(request):
    return render(request, 'virtual_company/market.html')

@login_required
def dashboard(request):
    # Önbellekten verileri al veya hesapla
    cache_key = f'dashboard_stats_{request.user.id}'
    dashboard_data = cache.get(cache_key)
    
    if not dashboard_data:
        # Stok istatistikleri
        low_stock_products = Product.objects.filter(
            stock_quantity__lte=models.F('min_stock_level')
        ).count()
        
        total_stock_value = Product.objects.aggregate(
            total=Sum(models.F('stock_quantity') * models.F('unit_price'))
        )['total'] or 0
        
        # Üretim istatistikleri
        production_stats = ProductionOrder.objects.aggregate(
            total=Count('id'),
            in_progress=Count('id', filter=Q(status='in_progress')),
            completed=Count('id', filter=Q(status='completed')),
            cancelled=Count('id', filter=Q(status='cancelled'))
        )
        
        # Kalite kontrol istatistikleri
        quality_stats = QualityControl.objects.aggregate(
            total=Count('id'),
            passed=Count('id', filter=Q(result='passed')),
            failed=Count('id', filter=Q(result='failed')),
            conditional=Count('id', filter=Q(result='conditional'))
        )
        
        dashboard_data = {
            'low_stock_products': low_stock_products,
            'total_stock_value': total_stock_value,
            'production_stats': production_stats,
            'quality_stats': quality_stats,
        }
        
        # Verileri önbelleğe al (1 saat süreyle)
        cache.set(cache_key, dashboard_data, 3600)
    
    return render(request, 'virtual_company/dashboard.html', dashboard_data)

@login_required
def competitors(request):
    return render(request, 'virtual_company/competitors.html')

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        try:
            product = ProductService.update_stock_quantity(
                product_id=pk,
                quantity=request.data.get('quantity'),
                movement_type=request.data.get('movement_type'),
                reference=request.data.get('reference'),
                user=request.user
            )
            return Response(ProductSerializer(product).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    def perform_create(self, serializer):
        try:
            production_order = ProductionService.create_production_order(
                data=serializer.validated_data,
                user=self.request.user
            )
            serializer.instance = production_order
        except Exception as e:
            raise ValidationError(str(e))
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        try:
            order = ProductionService.update_production_status(
                order_id=pk,
                new_status=request.data.get('status'),
                user=request.user
            )
            return Response(ProductionOrderSerializer(order).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class QualityControlViewSet(viewsets.ModelViewSet):
    queryset = QualityControl.objects.all()
    serializer_class = QualityControlSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        try:
            quality_control = QualityControlService.create_quality_control(
                data=serializer.validated_data,
                user=self.request.user
            )
            serializer.instance = quality_control
        except Exception as e:
            raise ValidationError(str(e))

class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterials.objects.all()
    serializer_class = BillOfMaterialsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id', '')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset 