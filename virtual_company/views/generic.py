from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum, F
from django.core.cache import cache
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.db import models
from .models import (
    Product, StockMovement, ProductionOrder, BillOfMaterials, QualityControl,
    VirtualCompany, Department, Employee, Project,
    Task, Budget, Report, KnowledgeBase, KnowledgeBaseRelatedItem,
    DailyTask,
    UserDailyTask,
)
from .serializers import (
    ProductSerializer, StockMovementSerializer, ProductionOrderSerializer,
    BillOfMaterialsSerializer, QualityControlSerializer
)
from .services import ProductService, ProductionService, QualityControlService
from .forms import (
    VirtualCompanyForm, DepartmentForm, EmployeeForm,
    ProjectForm, TaskForm, BudgetForm, ReportForm,
    KnowledgeBaseForm, KnowledgeBaseRelatedItemFormSet,
    DailyTaskForm
)
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse

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

# Sanal Şirket View'ları
@login_required
def company_list(request):
    companies = VirtualCompany.objects.filter(created_by=request.user)
    search_query = request.GET.get('search', '')
    
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(industry__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(companies, 10)
    page = request.GET.get('page')
    companies = paginator.get_page(page)
    
    context = {
        'companies': companies,
        'search_query': search_query,
    }
    return render(request, 'virtual_company/company_list.html', context)

@login_required
def company_detail(request, pk):
    company = get_object_or_404(VirtualCompany, pk=pk, created_by=request.user)
    
    departments = company.departments.all()
    employees = company.employees.all()
    projects = company.projects.all()
    budgets = company.budgets.all()
    reports = company.reports.all()
    
    context = {
        'company': company,
        'departments': departments,
        'employees': employees,
        'projects': projects,
        'budgets': budgets,
        'reports': reports,
    }
    return render(request, 'virtual_company/company_detail.html', context)

@login_required
def company_create(request):
    if request.method == 'POST':
        form = VirtualCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, _('Şirket başarıyla oluşturuldu.'))
            return redirect('virtual_company:company_detail', pk=company.pk)
    else:
        form = VirtualCompanyForm()
    
    context = {
        'form': form,
        'title': _('Yeni Şirket'),
    }
    return render(request, 'virtual_company/company_form.html', context)

@login_required
def company_update(request, pk):
    company = get_object_or_404(VirtualCompany, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = VirtualCompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, _('Şirket başarıyla güncellendi.'))
            return redirect('virtual_company:company_detail', pk=company.pk)
    else:
        form = VirtualCompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'title': _('Şirketi Düzenle'),
    }
    return render(request, 'virtual_company/company_form.html', context)

@login_required
def company_delete(request, pk):
    company = get_object_or_404(VirtualCompany, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        company.delete()
        messages.success(request, _('Şirket başarıyla silindi.'))
        return redirect('virtual_company:company_list')
    
    context = {
        'company': company,
    }
    return render(request, 'virtual_company/company_confirm_delete.html', context)

# Departman View'ları
@login_required
def department_list(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    departments = company.departments.all()
    
    context = {
        'company': company,
        'departments': departments,
    }
    return render(request, 'virtual_company/department_list.html', context)

@login_required
def department_create(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.company = company
            department.save()
            messages.success(request, _('Departman başarıyla oluşturuldu.'))
            return redirect('virtual_company:department_list', company_pk=company.pk)
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'company': company,
        'title': _('Yeni Departman'),
    }
    return render(request, 'virtual_company/department_form.html', context)

# Proje View'ları
@login_required
def project_list(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    projects = company.projects.all()
    
    context = {
        'company': company,
        'projects': projects,
    }
    return render(request, 'virtual_company/project_list.html', context)

@login_required
def project_create(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.company = company
            project.save()
            messages.success(request, _('Proje başarıyla oluşturuldu.'))
            return redirect('virtual_company:project_list', company_pk=company.pk)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'company': company,
        'title': _('Yeni Proje'),
    }
    return render(request, 'virtual_company/project_form.html', context)

# Görev View'ları
@login_required
def task_list(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if project.company.created_by != request.user:
        raise PermissionDenied
    
    tasks = project.tasks.all()
    
    context = {
        'project': project,
        'tasks': tasks,
    }
    return render(request, 'virtual_company/task_list.html', context)

@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if project.company.created_by != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            messages.success(request, _('Görev başarıyla oluşturuldu.'))
            return redirect('virtual_company:task_list', project_pk=project.pk)
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'project': project,
        'title': _('Yeni Görev'),
    }
    return render(request, 'virtual_company/task_form.html', context)

# Bütçe View'ları
@login_required
def budget_list(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    budgets = company.budgets.all()
    
    total_income = budgets.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = budgets.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    
    context = {
        'company': company,
        'budgets': budgets,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'virtual_company/budget_list.html', context)

@login_required
def budget_create(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.company = company
            budget.created_by = request.user
            budget.save()
            messages.success(request, _('Bütçe kaydı başarıyla oluşturuldu.'))
            return redirect('virtual_company:budget_list', company_pk=company.pk)
    else:
        form = BudgetForm()
    
    context = {
        'form': form,
        'company': company,
        'title': _('Yeni Bütçe Kaydı'),
    }
    return render(request, 'virtual_company/budget_form.html', context)

# Rapor View'ları
@login_required
def report_list(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    reports = company.reports.all()
    
    context = {
        'company': company,
        'reports': reports,
    }
    return render(request, 'virtual_company/report_list.html', context)

@login_required
def report_create(request, company_pk):
    company = get_object_or_404(VirtualCompany, pk=company_pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.company = company
            report.created_by = request.user
            report.save()
            messages.success(request, _('Rapor başarıyla oluşturuldu.'))
            return redirect('virtual_company:report_list', company_pk=company.pk)
    else:
        form = ReportForm()
    
    context = {
        'form': form,
        'company': company,
        'title': _('Yeni Rapor'),
    }
    return render(request, 'virtual_company/report_form.html', context)

# API View'ları
@login_required
@require_POST
def update_task_status(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.project.company.created_by != request.user:
        raise PermissionDenied
    
    status = request.POST.get('status')
    if status in dict(Task.STATUS_CHOICES):
        task.status = status
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@require_POST
def update_task_progress(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.project.company.created_by != request.user:
        raise PermissionDenied
    
    progress = request.POST.get('progress')
    try:
        progress = int(progress)
        if 0 <= progress <= 100:
            task.progress = progress
            task.save()
            return JsonResponse({'status': 'success'})
    except ValueError:
        pass
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def knowledge_base_list(request):
    """Bilgi bankası listesi görünümü"""
    
    # Filtreler
    category = request.GET.get('category', '')
    level = request.GET.get('level', '')
    tag = request.GET.get('tag', '')
    query = request.GET.get('q', '')
    
    knowledge_items = KnowledgeBase.objects.all()
    
    # Kullanıcı yönetici değilse aktif içerikleri göster
    if not request.user.is_staff:
        knowledge_items = knowledge_items.filter(active=True)
        
    # Filtreleri uygula
    if category:
        knowledge_items = knowledge_items.filter(category=category)
    if level:
        knowledge_items = knowledge_items.filter(level=level)
    if tag:
        knowledge_items = knowledge_items.filter(tags__icontains=tag)
    if query:
        knowledge_items = knowledge_items.filter(
            Q(title__icontains=query) | 
            Q(summary__icontains=query) | 
            Q(content__icontains=query)
        )
    
    # Öne çıkarılanları üste al ve tarihe göre sırala
    knowledge_items = knowledge_items.order_by('-is_featured', '-created_at')
    
    # Kategorileri getir
    categories = dict(KnowledgeBase.CATEGORY_CHOICES)
    
    # Seviyeleri getir
    levels = dict(KnowledgeBase.LEVEL_CHOICES)
    
    # Tüm etiketleri getir
    all_tags = []
    for item in KnowledgeBase.objects.values_list('tags', flat=True):
        if item:
            all_tags.extend([tag.strip() for tag in item.split(',') if tag.strip()])
    all_tags = sorted(list(set(all_tags)))
    
    context = {
        'knowledge_items': knowledge_items,
        'categories': categories,
        'levels': levels,
        'all_tags': all_tags,
        'selected_category': category,
        'selected_level': level,
        'selected_tag': tag,
        'query': query,
    }
    
    return render(request, 'virtual_company/knowledge_base_list.html', context)

@login_required
def knowledge_base_detail(request, pk):
    """Bilgi bankası detay görünümü"""
    
    knowledge_item = get_object_or_404(KnowledgeBase, pk=pk)
    
    # Kullanıcı yönetici değilse ve içerik aktif değilse 404 hatası göster
    if not request.user.is_staff and not knowledge_item.active:
        raise Http404(_("Bu içerik şu anda aktif değil"))
    
    # İlişkili öğeleri getir
    related_items = knowledge_item.knowledgebaserelateditem_set.order_by('order')
    
    # İlgili diğer bilgi bankası içeriklerini bul (benzer etiketlere sahip)
    if knowledge_item.tags:
        tags = [tag.strip() for tag in knowledge_item.tags.split(',') if tag.strip()]
        similar_items = KnowledgeBase.objects.filter(active=True)
        
        q_objects = Q()
        for tag in tags:
            q_objects |= Q(tags__icontains=tag)
        
        similar_items = similar_items.filter(q_objects).exclude(pk=pk).distinct()[:3]
    else:
        similar_items = KnowledgeBase.objects.filter(active=True, category=knowledge_item.category).exclude(pk=pk)[:3]
    
    context = {
        'knowledge_item': knowledge_item,
        'related_items': related_items,
        'similar_items': similar_items
    }
    
    return render(request, 'virtual_company/knowledge_base_detail.html', context)

@login_required
@staff_member_required
def knowledge_base_create(request):
    """Bilgi bankası oluşturma görünümü"""
    
    if request.method == 'POST':
        form = KnowledgeBaseForm(request.POST, request.FILES)
        formset = KnowledgeBaseRelatedItemFormSet(request.POST, prefix='related_items')
        
        if form.is_valid() and formset.is_valid():
            knowledge_item = form.save(commit=False)
            knowledge_item.created_by = request.user
            knowledge_item.save()
            
            # İlişkili öğeleri kaydet
            formset.instance = knowledge_item
            formset.save()
            
            messages.success(request, _('Bilgi bankası başarıyla oluşturuldu'))
            return redirect('knowledge_base_detail', pk=knowledge_item.pk)
    else:
        form = KnowledgeBaseForm()
        formset = KnowledgeBaseRelatedItemFormSet(prefix='related_items')
    
    context = {
        'form': form,
        'formset': formset,
        'form_title': _('Yeni Bilgi Bankası Öğesi Ekle'),
        'submit_text': _('Kaydet')
    }
    
    return render(request, 'virtual_company/knowledge_base_form.html', context)

@login_required
@staff_member_required
def knowledge_base_update(request, pk):
    """Bilgi bankası güncelleme görünümü"""
    
    knowledge_item = get_object_or_404(KnowledgeBase, pk=pk)
    
    if request.method == 'POST':
        form = KnowledgeBaseForm(request.POST, request.FILES, instance=knowledge_item)
        formset = KnowledgeBaseRelatedItemFormSet(request.POST, instance=knowledge_item, prefix='related_items')
        
        if form.is_valid() and formset.is_valid():
            knowledge_item = form.save(commit=False)
            knowledge_item.updated_at = timezone.now()
            knowledge_item.updated_by = request.user
            knowledge_item.save()
            
            # İlişkili öğeleri kaydet
            formset.save()
            
            messages.success(request, _('Bilgi bankası başarıyla güncellendi'))
            return redirect('knowledge_base_detail', pk=knowledge_item.pk)
    else:
        form = KnowledgeBaseForm(instance=knowledge_item)
        formset = KnowledgeBaseRelatedItemFormSet(instance=knowledge_item, prefix='related_items')
    
    context = {
        'form': form,
        'formset': formset,
        'knowledge_item': knowledge_item,
        'form_title': _('Bilgi Bankası Öğesini Düzenle'),
        'submit_text': _('Güncelle')
    }
    
    return render(request, 'virtual_company/knowledge_base_form.html', context)

@login_required
@staff_member_required
def knowledge_base_delete(request, pk):
    """Bilgi bankası silme görünümü"""
    
    knowledge_item = get_object_or_404(KnowledgeBase, pk=pk)
    
    if request.method == 'POST':
        knowledge_item.delete()
        messages.success(request, _('Bilgi bankası başarıyla silindi'))
        return redirect('knowledge_base_list')
    
    context = {
        'knowledge_item': knowledge_item
    }
    
    return render(request, 'virtual_company/knowledge_base_confirm_delete.html', context)

# Günlük Görevler
class DailyTaskListView(LoginRequiredMixin, ListView):
    model = DailyTask
    template_name = 'virtual_company/daily_task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        queryset = DailyTask.objects.filter(is_active=True)
        
        # Kategori filtreleme
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Zorluk filtreleme
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tasks = {ut.task_id: ut for ut in UserDailyTask.objects.filter(user=self.request.user)}
        
        # Göreve kullanıcı durumunu ekle
        for task in context['tasks']:
            if task.id in user_tasks:
                task.user_task = user_tasks[task.id]
            else:
                task.user_task = None
        
        context['categories'] = DailyTask.CATEGORY_CHOICES
        context['difficulties'] = DailyTask.DIFFICULTY_CHOICES
        return context

class DailyTaskDetailView(LoginRequiredMixin, DetailView):
    model = DailyTask
    template_name = 'virtual_company/daily_task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        
        user_task, created = UserDailyTask.objects.get_or_create(
            user=self.request.user,
            task=task,
            defaults={'status': 'BASLAMADI'}
        )
        
        context['user_task'] = user_task
        context['steps'] = enumerate(task.steps) if task.steps else []
        return context

class StartDailyTaskView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(DailyTask, pk=pk)
        user_task, created = UserDailyTask.objects.get_or_create(
            user=request.user,
            task=task,
            defaults={'status': 'BASLAMADI'}
        )
        
        if user_task.status == 'BASLAMADI':
            user_task.start_task()
            messages.success(request, f"'{task.title}' görevi başlatıldı.")
        else:
            messages.info(request, "Bu görev zaten başlatılmış.")
            
        return redirect('virtual_company:daily_task_detail', pk=pk)

class CompleteDailyTaskStepView(LoginRequiredMixin, View):
    def post(self, request, pk, step_index):
        task = get_object_or_404(DailyTask, pk=pk)
        user_task = get_object_or_404(UserDailyTask, user=request.user, task=task)
        
        if user_task.status == 'DEVAM_EDIYOR':
            if user_task.complete_step(step_index):
                messages.success(request, f"Adım {step_index+1} tamamlandı.")
            else:
                messages.info(request, "Bu adım zaten tamamlanmış.")
        elif user_task.status == 'TAMAMLANDI':
            messages.info(request, "Bu görev zaten tamamlanmış.")
        else:
            messages.warning(request, "Adımları tamamlamak için önce görevi başlatmalısınız.")
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'status': user_task.status,
                'completed_steps': user_task.completed_steps
            })
        
        return redirect('virtual_company:daily_task_detail', pk=pk)

class CompleteDailyTaskView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(DailyTask, pk=pk)
        user_task = get_object_or_404(UserDailyTask, user=request.user, task=task)
        
        if user_task.status != 'TAMAMLANDI':
            if user_task.complete_task():
                messages.success(request, f"'{task.title}' görevi tamamlandı! XP ve ödülleriniz hesabınıza eklendi.")
                
                # TODO: Kullanıcıya XP ve ödülleri ver
                # user_profile = request.user.profile
                # user_profile.add_xp(task.xp_reward)
                # user_profile.add_money(task.money_reward)
            else:
                messages.error(request, "Görev tamamlanırken bir hata oluştu.")
        else:
            messages.info(request, "Bu görev zaten tamamlanmış.")
            
        return redirect('virtual_company:daily_task_detail', pk=pk)

class DailyTaskCreateView(LoginRequiredMixin, CreateView):
    model = DailyTask
    form_class = DailyTaskForm
    template_name = 'virtual_company/daily_task_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _('Bu sayfaya erişim izniniz bulunmamaktadır.'))
            return redirect('virtual_company:daily_task_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, _('Günlük görev başarıyla oluşturuldu.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('virtual_company:daily_task_detail', kwargs={'pk': self.object.pk})

class DailyTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = DailyTask
    form_class = DailyTaskForm
    template_name = 'virtual_company/daily_task_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _('Bu sayfaya erişim izniniz bulunmamaktadır.'))
            return redirect('virtual_company:daily_task_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, _('Günlük görev başarıyla güncellendi.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('virtual_company:daily_task_detail', kwargs={'pk': self.object.pk})

class DailyTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = DailyTask
    template_name = 'virtual_company/daily_task_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _('Bu sayfaya erişim izniniz bulunmamaktadır.'))
            return redirect('virtual_company:daily_task_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Günlük görev başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('virtual_company:daily_task_list')

class ToggleDailyTaskActiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_staff:
            messages.error(request, _('Bu işlemi gerçekleştirme izniniz bulunmamaktadır.'))
            return redirect('virtual_company:daily_task_list')
            
        task = get_object_or_404(DailyTask, pk=pk)
        task.is_active = not task.is_active
        task.save()
        
        status_message = _('etkinleştirildi') if task.is_active else _('devre dışı bırakıldı')
        messages.success(request, _(f"'{task.title}' görevi {status_message}."))
        
        return redirect('virtual_company:daily_task_detail', pk=task.pk)

class AddDailyTaskNoteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(DailyTask, pk=pk)
        user_task = get_object_or_404(UserDailyTask, user=request.user, task=task)
        
        note = request.POST.get('note', '').strip()
        if note:
            user_task.notes = note
            user_task.save()
            messages.success(request, "Not başarıyla kaydedildi.")
        else:
            messages.warning(request, "Not boş olamaz.")
            
        return redirect('virtual_company:daily_task_detail', pk=pk) 