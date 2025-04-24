from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    Company, Employee, Project, Budget, Report,
    Product, StockMovement, ProductionOrder, BillOfMaterials,
    QualityControl, ModuleSetting, UserDailyTask,
    KnowledgeBaseRelatedItem
)
from .forms import CompanyForm, EmployeeForm, ProjectForm

# Company Views
class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'virtual_company/company_list.html'
    context_object_name = 'companies'

class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'virtual_company/company_detail.html'

class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = 'virtual_company/company_form.html'
    form_class = CompanyForm
    success_url = reverse_lazy('virtual_company:company_list')

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    template_name = 'virtual_company/company_form.html'
    form_class = CompanyForm
    success_url = reverse_lazy('virtual_company:company_list')

class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'virtual_company/company_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:company_list')

# Employee Views
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'virtual_company/employee_list.html'
    context_object_name = 'employees'

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'virtual_company/employee_detail.html'

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    template_name = 'virtual_company/employee_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:employee_list')

class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    template_name = 'virtual_company/employee_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:employee_list')

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'virtual_company/employee_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:employee_list')

# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'virtual_company/project_list.html'
    context_object_name = 'projects'

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'virtual_company/project_detail.html'

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'virtual_company/project_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:project_list')

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'virtual_company/project_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:project_list')

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'virtual_company/project_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:project_list')

# Budget Views
class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'virtual_company/budget_list.html'
    context_object_name = 'budgets'

class BudgetDetailView(LoginRequiredMixin, DetailView):
    model = Budget
    template_name = 'virtual_company/budget_detail.html'

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    template_name = 'virtual_company/budget_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:budget_list')

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    template_name = 'virtual_company/budget_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:budget_list')

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = 'virtual_company/budget_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:budget_list')

# Report Views
class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'virtual_company/report_list.html'
    context_object_name = 'reports'

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'virtual_company/report_detail.html'

class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    template_name = 'virtual_company/report_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:report_list')

class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    template_name = 'virtual_company/report_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:report_list')

class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'virtual_company/report_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:report_list')

# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'virtual_company/product_list.html'
    context_object_name = 'products'

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'virtual_company/product_detail.html'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'virtual_company/product_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'virtual_company/product_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:product_list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'virtual_company/product_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:product_list')

# StockMovement Views
class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'virtual_company/stockmovement_list.html'
    context_object_name = 'movements'

class StockMovementDetailView(LoginRequiredMixin, DetailView):
    model = StockMovement
    template_name = 'virtual_company/stockmovement_detail.html'

class StockMovementCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    template_name = 'virtual_company/stockmovement_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:stockmovement_list')

class StockMovementUpdateView(LoginRequiredMixin, UpdateView):
    model = StockMovement
    template_name = 'virtual_company/stockmovement_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:stockmovement_list')

class StockMovementDeleteView(LoginRequiredMixin, DeleteView):
    model = StockMovement
    template_name = 'virtual_company/stockmovement_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:stockmovement_list')

# ProductionOrder Views
class ProductionOrderListView(LoginRequiredMixin, ListView):
    model = ProductionOrder
    template_name = 'virtual_company/productionorder_list.html'
    context_object_name = 'orders'

class ProductionOrderDetailView(LoginRequiredMixin, DetailView):
    model = ProductionOrder
    template_name = 'virtual_company/productionorder_detail.html'

class ProductionOrderCreateView(LoginRequiredMixin, CreateView):
    model = ProductionOrder
    template_name = 'virtual_company/productionorder_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:productionorder_list')

class ProductionOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductionOrder
    template_name = 'virtual_company/productionorder_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:productionorder_list')

class ProductionOrderDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductionOrder
    template_name = 'virtual_company/productionorder_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:productionorder_list')

# BillOfMaterials Views
class BillOfMaterialsListView(LoginRequiredMixin, ListView):
    model = BillOfMaterials
    template_name = 'virtual_company/billofmaterials_list.html'
    context_object_name = 'bills'

class BillOfMaterialsDetailView(LoginRequiredMixin, DetailView):
    model = BillOfMaterials
    template_name = 'virtual_company/billofmaterials_detail.html'

class BillOfMaterialsCreateView(LoginRequiredMixin, CreateView):
    model = BillOfMaterials
    template_name = 'virtual_company/billofmaterials_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:billofmaterials_list')

class BillOfMaterialsUpdateView(LoginRequiredMixin, UpdateView):
    model = BillOfMaterials
    template_name = 'virtual_company/billofmaterials_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:billofmaterials_list')

class BillOfMaterialsDeleteView(LoginRequiredMixin, DeleteView):
    model = BillOfMaterials
    template_name = 'virtual_company/billofmaterials_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:billofmaterials_list')

# QualityControl Views
class QualityControlListView(LoginRequiredMixin, ListView):
    model = QualityControl
    template_name = 'virtual_company/qualitycontrol_list.html'
    context_object_name = 'controls'

class QualityControlDetailView(LoginRequiredMixin, DetailView):
    model = QualityControl
    template_name = 'virtual_company/qualitycontrol_detail.html'

class QualityControlCreateView(LoginRequiredMixin, CreateView):
    model = QualityControl
    template_name = 'virtual_company/qualitycontrol_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:qualitycontrol_list')

class QualityControlUpdateView(LoginRequiredMixin, UpdateView):
    model = QualityControl
    template_name = 'virtual_company/qualitycontrol_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:qualitycontrol_list')

class QualityControlDeleteView(LoginRequiredMixin, DeleteView):
    model = QualityControl
    template_name = 'virtual_company/qualitycontrol_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:qualitycontrol_list')

# ModuleSetting Views
class ModuleSettingListView(LoginRequiredMixin, ListView):
    model = ModuleSetting
    template_name = 'virtual_company/modulesetting_list.html'
    context_object_name = 'settings'

class ModuleSettingDetailView(LoginRequiredMixin, DetailView):
    model = ModuleSetting
    template_name = 'virtual_company/modulesetting_detail.html'

class ModuleSettingCreateView(LoginRequiredMixin, CreateView):
    model = ModuleSetting
    template_name = 'virtual_company/modulesetting_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:modulesetting_list')

class ModuleSettingUpdateView(LoginRequiredMixin, UpdateView):
    model = ModuleSetting
    template_name = 'virtual_company/modulesetting_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:modulesetting_list')

class ModuleSettingDeleteView(LoginRequiredMixin, DeleteView):
    model = ModuleSetting
    template_name = 'virtual_company/modulesetting_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:modulesetting_list')

# UserDailyTask Views
class UserDailyTaskListView(LoginRequiredMixin, ListView):
    model = UserDailyTask
    template_name = 'virtual_company/userdailytask_list.html'
    context_object_name = 'tasks'

class UserDailyTaskDetailView(LoginRequiredMixin, DetailView):
    model = UserDailyTask
    template_name = 'virtual_company/userdailytask_detail.html'

class UserDailyTaskCreateView(LoginRequiredMixin, CreateView):
    model = UserDailyTask
    template_name = 'virtual_company/userdailytask_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:userdailytask_list')

class UserDailyTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = UserDailyTask
    template_name = 'virtual_company/userdailytask_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:userdailytask_list')

class UserDailyTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = UserDailyTask
    template_name = 'virtual_company/userdailytask_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:userdailytask_list')

# KnowledgeBaseRelatedItem Views
class KnowledgeBaseRelatedItemListView(LoginRequiredMixin, ListView):
    model = KnowledgeBaseRelatedItem
    template_name = 'virtual_company/knowledgebaserelateditem_list.html'
    context_object_name = 'items'

class KnowledgeBaseRelatedItemDetailView(LoginRequiredMixin, DetailView):
    model = KnowledgeBaseRelatedItem
    template_name = 'virtual_company/knowledgebaserelateditem_detail.html'

class KnowledgeBaseRelatedItemCreateView(LoginRequiredMixin, CreateView):
    model = KnowledgeBaseRelatedItem
    template_name = 'virtual_company/knowledgebaserelateditem_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:knowledgebaserelateditem_list')

class KnowledgeBaseRelatedItemUpdateView(LoginRequiredMixin, UpdateView):
    model = KnowledgeBaseRelatedItem
    template_name = 'virtual_company/knowledgebaserelateditem_form.html'
    fields = '__all__'
    success_url = reverse_lazy('virtual_company:knowledgebaserelateditem_list')

class KnowledgeBaseRelatedItemDeleteView(LoginRequiredMixin, DeleteView):
    model = KnowledgeBaseRelatedItem
    template_name = 'virtual_company/knowledgebaserelateditem_confirm_delete.html'
    success_url = reverse_lazy('virtual_company:knowledgebaserelateditem_list') 