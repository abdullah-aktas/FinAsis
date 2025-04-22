from django.urls import path
from . import views

app_name = "stock_management"

urlpatterns = [
    # Depo listesi
    path('warehouse/', views.warehouse_list, name='warehouse_list'),
    path('warehouse/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouse/<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('warehouse/<int:pk>/update/', views.warehouse_update, name='warehouse_update'),
    path('warehouse/<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
    
    # Ürün listesi
    path('product/', views.product_list, name='product_list'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/update/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Stok listesi
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/create/', views.stock_create, name='stock_create'),
    path('stock/<int:pk>/', views.stock_detail, name='stock_detail'),
    path('stock/<int:pk>/update/', views.stock_update, name='stock_update'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    
    # Stok hareketi listesi
    path('stockmovement/', views.stockmovement_list, name='stockmovement_list'),
    path('stockmovement/create/', views.stockmovement_create, name='stockmovement_create'),
    path('stockmovement/<int:pk>/', views.stockmovement_detail, name='stockmovement_detail'),
    path('stockmovement/<int:pk>/update/', views.stockmovement_update, name='stockmovement_update'),
    path('stockmovement/<int:pk>/delete/', views.stockmovement_delete, name='stockmovement_delete'),
    
    # Stok sayımı listesi
    path('stockcount/', views.stockcount_list, name='stockcount_list'),
    path('stockcount/create/', views.stockcount_create, name='stockcount_create'),
    path('stockcount/<int:pk>/', views.stockcount_detail, name='stockcount_detail'),
    path('stockcount/<int:pk>/update/', views.stockcount_update, name='stockcount_update'),
    path('stockcount/<int:pk>/delete/', views.stockcount_delete, name='stockcount_delete'),
    
    # Stok sayım kalem listesi
    path('stockcountitem/', views.stockcountitem_list, name='stockcountitem_list'),
    path('stockcountitem/create/', views.stockcountitem_create, name='stockcountitem_create'),
    path('stockcountitem/<int:pk>/', views.stockcountitem_detail, name='stockcountitem_detail'),
    path('stockcountitem/<int:pk>/update/', views.stockcountitem_update, name='stockcountitem_update'),
    path('stockcountitem/<int:pk>/delete/', views.stockcountitem_delete, name='stockcountitem_delete'),
] 