from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from . import views

app_name = "stock_management"

urlpatterns = [
    # Ürün URL'leri
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Kategori URL'leri
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Stok Hareketi URL'leri
    path('movements/create/', views.StockMovementCreateView.as_view(), name='movement_create'),
    path('movements/<int:pk>/', views.StockMovementDetailView.as_view(), name='movement_detail'),
    
    # Stok Uyarıları URL'leri
    path('alerts/', views.stock_alert_list, name='stock_alert_list'),
    path('alerts/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    
    # Rapor URL'leri
    path('reports/stock/', views.stock_report, name='stock_report'),
    path('reports/movements/', views.movement_report, name='movement_report'),
    
    # API URL'leri
    path('api/products/', views.ProductAPIView.as_view(), name='api_products'),
    path('api/products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('api/movements/', views.StockMovementAPIView.as_view(), name='api_movements'),
    path('api/alerts/', views.StockAlertAPIView.as_view(), name='api_alerts'),
    
    # AJAX URL'leri
    path('ajax/check-stock/', views.check_stock_ajax, name='check_stock_ajax'),
    path('ajax/product-autocomplete/', views.product_autocomplete, name='product_autocomplete'),
] 