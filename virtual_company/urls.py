from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'production-orders', views.ProductionOrderViewSet)
router.register(r'quality-controls', views.QualityControlViewSet)
router.register(r'bill-of-materials', views.BillOfMaterialsViewSet)

app_name = 'virtual_company'

urlpatterns = [
    # Şirket URL'leri
    path('', views.company_list, name='company_list'),
    path('create/', views.company_create, name='company_create'),
    path('<int:pk>/', views.company_detail, name='company_detail'),
    path('<int:pk>/update/', views.company_update, name='company_update'),
    path('<int:pk>/delete/', views.company_delete, name='company_delete'),
    
    # Departman URL'leri
    path('<int:company_pk>/departments/', views.department_list, name='department_list'),
    path('<int:company_pk>/departments/create/', views.department_create, name='department_create'),
    
    # Proje URL'leri
    path('<int:company_pk>/projects/', views.project_list, name='project_list'),
    path('<int:company_pk>/projects/create/', views.project_create, name='project_create'),
    
    # Görev URL'leri
    path('projects/<int:project_pk>/tasks/', views.task_list, name='task_list'),
    path('projects/<int:project_pk>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:task_pk>/update-progress/', views.update_task_progress, name='update_task_progress'),
    
    # Bütçe URL'leri
    path('<int:company_pk>/budgets/', views.budget_list, name='budget_list'),
    path('<int:company_pk>/budgets/create/', views.budget_create, name='budget_create'),
    
    # Rapor URL'leri
    path('<int:company_pk>/reports/', views.report_list, name='report_list'),
    path('<int:company_pk>/reports/create/', views.report_create, name='report_create'),
    
    path('api/', include(router.urls)),
] 