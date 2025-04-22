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
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
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
    
    # Knowledge Base URLs
    path('bilgi-bankasi/', views.knowledge_base_list, name='knowledge_base_list'),
    path('bilgi-bankasi/<int:pk>/', views.knowledge_base_detail, name='knowledge_base_detail'),
    path('bilgi-bankasi/ekle/', views.knowledge_base_create, name='knowledge_base_create'),
    path('bilgi-bankasi/<int:pk>/duzenle/', views.knowledge_base_update, name='knowledge_base_update'),
    path('bilgi-bankasi/<int:pk>/sil/', views.knowledge_base_delete, name='knowledge_base_delete'),
    
    # Günlük Görevler
    path('gorevler/', views.DailyTaskListView.as_view(), name='daily_task_list'),
    path('gorev/<int:pk>/', views.DailyTaskDetailView.as_view(), name='daily_task_detail'),
    path('gorev/ekle/', views.DailyTaskCreateView.as_view(), name='daily_task_create'),
    path('gorev/<int:pk>/duzenle/', views.DailyTaskUpdateView.as_view(), name='daily_task_update'),
    path('gorev/<int:pk>/sil/', views.DailyTaskDeleteView.as_view(), name='daily_task_delete'),
    path('gorev/<int:pk>/durum-degistir/', views.ToggleDailyTaskActiveView.as_view(), name='toggle_daily_task'),
    path('gorev/<int:pk>/baslat/', views.StartDailyTaskView.as_view(), name='start_daily_task'),
    path('gorev/<int:pk>/tamamla/', views.CompleteDailyTaskView.as_view(), name='complete_daily_task'),
    path('gorev/<int:pk>/adim/<int:step_index>/tamamla/', views.CompleteDailyTaskStepView.as_view(), name='complete_task_step'),
    path('gorev/<int:pk>/not-ekle/', views.AddDailyTaskNoteView.as_view(), name='add_daily_task_note'),
    
    path('api/', include(router.urls)),
] 