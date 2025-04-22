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

    # VirtualCompany URLs
    path('virtualcompany/', views.VirtualCompanyListView.as_view(), name='virtualcompany_list'),
    path('virtualcompany/<int:pk>/', views.VirtualCompanyDetailView.as_view(), name='virtualcompany_detail'),
    path('virtualcompany/create/', views.VirtualCompanyCreateView.as_view(), name='virtualcompany_create'),
    path('virtualcompany/<int:pk>/update/', views.VirtualCompanyUpdateView.as_view(), name='virtualcompany_update'),
    path('virtualcompany/<int:pk>/delete/', views.VirtualCompanyDeleteView.as_view(), name='virtualcompany_delete'),

    # Employee URLs
    path('employee/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employee/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employee/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employee/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),

    # Project URLs
    path('project/', views.ProjectListView.as_view(), name='project_list'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # Budget URLs
    path('budget/', views.BudgetListView.as_view(), name='budget_list'),
    path('budget/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budget/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budget/<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget_update'),
    path('budget/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),

    # Report URLs
    path('report/', views.ReportListView.as_view(), name='report_list'),
    path('report/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('report/create/', views.ReportCreateView.as_view(), name='report_create'),
    path('report/<int:pk>/update/', views.ReportUpdateView.as_view(), name='report_update'),
    path('report/<int:pk>/delete/', views.ReportDeleteView.as_view(), name='report_delete'),

    # Product URLs
    path('product/', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # StockMovement URLs
    path('stockmovement/', views.StockMovementListView.as_view(), name='stockmovement_list'),
    path('stockmovement/<int:pk>/', views.StockMovementDetailView.as_view(), name='stockmovement_detail'),
    path('stockmovement/create/', views.StockMovementCreateView.as_view(), name='stockmovement_create'),
    path('stockmovement/<int:pk>/update/', views.StockMovementUpdateView.as_view(), name='stockmovement_update'),
    path('stockmovement/<int:pk>/delete/', views.StockMovementDeleteView.as_view(), name='stockmovement_delete'),

    # ProductionOrder URLs
    path('productionorder/', views.ProductionOrderListView.as_view(), name='productionorder_list'),
    path('productionorder/<int:pk>/', views.ProductionOrderDetailView.as_view(), name='productionorder_detail'),
    path('productionorder/create/', views.ProductionOrderCreateView.as_view(), name='productionorder_create'),
    path('productionorder/<int:pk>/update/', views.ProductionOrderUpdateView.as_view(), name='productionorder_update'),
    path('productionorder/<int:pk>/delete/', views.ProductionOrderDeleteView.as_view(), name='productionorder_delete'),

    # BillOfMaterials URLs
    path('billofmaterials/', views.BillOfMaterialsListView.as_view(), name='billofmaterials_list'),
    path('billofmaterials/<int:pk>/', views.BillOfMaterialsDetailView.as_view(), name='billofmaterials_detail'),
    path('billofmaterials/create/', views.BillOfMaterialsCreateView.as_view(), name='billofmaterials_create'),
    path('billofmaterials/<int:pk>/update/', views.BillOfMaterialsUpdateView.as_view(), name='billofmaterials_update'),
    path('billofmaterials/<int:pk>/delete/', views.BillOfMaterialsDeleteView.as_view(), name='billofmaterials_delete'),

    # QualityControl URLs
    path('qualitycontrol/', views.QualityControlListView.as_view(), name='qualitycontrol_list'),
    path('qualitycontrol/<int:pk>/', views.QualityControlDetailView.as_view(), name='qualitycontrol_detail'),
    path('qualitycontrol/create/', views.QualityControlCreateView.as_view(), name='qualitycontrol_create'),
    path('qualitycontrol/<int:pk>/update/', views.QualityControlUpdateView.as_view(), name='qualitycontrol_update'),
    path('qualitycontrol/<int:pk>/delete/', views.QualityControlDeleteView.as_view(), name='qualitycontrol_delete'),

    # ModuleSetting URLs
    path('modulesetting/', views.ModuleSettingListView.as_view(), name='modulesetting_list'),
    path('modulesetting/<int:pk>/', views.ModuleSettingDetailView.as_view(), name='modulesetting_detail'),
    path('modulesetting/create/', views.ModuleSettingCreateView.as_view(), name='modulesetting_create'),
    path('modulesetting/<int:pk>/update/', views.ModuleSettingUpdateView.as_view(), name='modulesetting_update'),
    path('modulesetting/<int:pk>/delete/', views.ModuleSettingDeleteView.as_view(), name='modulesetting_delete'),

    # UserDailyTask URLs
    path('userdailytask/', views.UserDailyTaskListView.as_view(), name='userdailytask_list'),
    path('userdailytask/<int:pk>/', views.UserDailyTaskDetailView.as_view(), name='userdailytask_detail'),
    path('userdailytask/create/', views.UserDailyTaskCreateView.as_view(), name='userdailytask_create'),
    path('userdailytask/<int:pk>/update/', views.UserDailyTaskUpdateView.as_view(), name='userdailytask_update'),
    path('userdailytask/<int:pk>/delete/', views.UserDailyTaskDeleteView.as_view(), name='userdailytask_delete'),

    # KnowledgeBaseRelatedItem URLs
    path('knowledgebaserelateditem/', views.KnowledgeBaseRelatedItemListView.as_view(), name='knowledgebaserelateditem_list'),
    path('knowledgebaserelateditem/<int:pk>/', views.KnowledgeBaseRelatedItemDetailView.as_view(), name='knowledgebaserelateditem_detail'),
    path('knowledgebaserelateditem/create/', views.KnowledgeBaseRelatedItemCreateView.as_view(), name='knowledgebaserelateditem_create'),
    path('knowledgebaserelateditem/<int:pk>/update/', views.KnowledgeBaseRelatedItemUpdateView.as_view(), name='knowledgebaserelateditem_update'),
    path('knowledgebaserelateditem/<int:pk>/delete/', views.KnowledgeBaseRelatedItemDeleteView.as_view(), name='knowledgebaserelateditem_delete'),
] 