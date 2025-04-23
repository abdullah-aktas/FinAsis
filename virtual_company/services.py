from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Product, StockMovement, ProductionOrder, BillOfMaterials, QualityControl
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.core.cache import cache
from .models import Company, Department, Employee, Project, Task, PerformanceReview

class ProductService:
    @staticmethod
    def create_product(data):
        with transaction.atomic():
            product = Product.objects.create(**data)
            return product

    @staticmethod
    def update_stock_quantity(product_id, quantity, movement_type, reference, user):
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=product_id)
            
            if movement_type == 'out' and product.stock_quantity < quantity:
                raise ValidationError(_('Yetersiz stok miktarı'))
            
            if movement_type == 'in':
                product.stock_quantity += quantity
            elif movement_type == 'out':
                product.stock_quantity -= quantity
            
            product.save()
            
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                unit_price=product.unit_price,
                reference=reference,
                created_by=user
            )
            
            return product

class ProductionService:
    @staticmethod
    def create_production_order(data, user):
        with transaction.atomic():
            # Ürün ağacını kontrol et
            product = data['product']
            quantity = data['quantity']
            bom_items = BillOfMaterials.objects.filter(product=product, is_active=True)
            
            # Malzeme yeterliliğini kontrol et
            for bom_item in bom_items:
                required_quantity = bom_item.quantity * quantity
                if bom_item.component.stock_quantity < required_quantity:
                    raise ValidationError(
                        _('Yetersiz malzeme: %(component)s (Gereken: %(required)s, Mevcut: %(available)s)'),
                        params={
                            'component': bom_item.component.name,
                            'required': required_quantity,
                            'available': bom_item.component.stock_quantity
                        }
                    )
            
            # Üretim emrini oluştur
            data['created_by'] = user
            production_order = ProductionOrder.objects.create(**data)
            
            return production_order

    @staticmethod
    def update_production_status(order_id, new_status, user):
        with transaction.atomic():
            order = ProductionOrder.objects.select_for_update().get(id=order_id)
            
            if new_status == 'completed':
                # Üretilen ürünü stoka ekle
                ProductService.update_stock_quantity(
                    product_id=order.product.id,
                    quantity=order.quantity,
                    movement_type='in',
                    reference=f'Üretim Emri #{order.order_number}',
                    user=user
                )
                
                # Kullanılan malzemeleri stoktan düş
                bom_items = BillOfMaterials.objects.filter(product=order.product, is_active=True)
                for bom_item in bom_items:
                    ProductService.update_stock_quantity(
                        product_id=bom_item.component.id,
                        quantity=bom_item.quantity * order.quantity,
                        movement_type='out',
                        reference=f'Üretim Emri #{order.order_number}',
                        user=user
                    )
            
            order.status = new_status
            order.save()
            
            return order

class QualityControlService:
    @staticmethod
    def create_quality_control(data, user):
        with transaction.atomic():
            data['inspector'] = user
            quality_control = QualityControl.objects.create(**data)
            
            # Kalite kontrol sonucuna göre üretim emrini güncelle
            if quality_control.result == 'failed':
                production_order = quality_control.production_order
                production_order.status = 'cancelled'
                production_order.save()
            
            return quality_control

class CompanyService:
    """Şirket servisi."""
    
    @staticmethod
    def get_company_stats(company_id):
        """Şirket istatistiklerini getirir."""
        cache_key = f'company_stats_{company_id}'
        stats = cache.get(cache_key)
        
        if stats is None:
            company = Company.objects.get(id=company_id)
            stats = {
                'total_employees': Employee.objects.filter(company=company).count(),
                'total_departments': Department.objects.filter(company=company).count(),
                'total_projects': Project.objects.filter(company=company).count(),
                'active_projects': Project.objects.filter(
                    company=company, 
                    status='in_progress'
                ).count(),
                'total_budget': Department.objects.filter(
                    company=company
                ).aggregate(total=Sum('budget'))['total'] or 0,
            }
            cache.set(cache_key, stats, 3600)  # 1 saat önbellek
        
        return stats

class DepartmentService:
    """Departman servisi."""
    
    @staticmethod
    def get_department_performance(department_id):
        """Departman performansını hesaplar."""
        department = Department.objects.get(id=department_id)
        
        # Proje tamamlanma oranı
        total_projects = Project.objects.filter(department=department).count()
        completed_projects = Project.objects.filter(
            department=department,
            status='completed'
        ).count()
        completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
        
        # Ortalama görev tamamlanma süresi
        avg_task_completion = Task.objects.filter(
            project__department=department,
            status='completed'
        ).aggregate(avg=Avg('due_date'))['avg']
        
        return {
            'completion_rate': completion_rate,
            'avg_task_completion': avg_task_completion,
            'employee_count': Employee.objects.filter(department=department).count(),
            'budget_utilization': department.budget_utilization,
        }

class EmployeeService:
    """Çalışan servisi."""
    
    @staticmethod
    def get_employee_performance(employee_id):
        """Çalışan performansını hesaplar."""
        employee = Employee.objects.get(id=employee_id)
        
        # Görev tamamlanma oranı
        total_tasks = Task.objects.filter(assigned_to=employee.user).count()
        completed_tasks = Task.objects.filter(
            assigned_to=employee.user,
            status='completed'
        ).count()
        task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Son performans değerlendirmesi
        last_review = PerformanceReview.objects.filter(
            employee=employee
        ).order_by('-review_date').first()
        
        return {
            'task_completion_rate': task_completion_rate,
            'last_review_rating': last_review.rating if last_review else None,
            'last_review_date': last_review.review_date if last_review else None,
            'active_projects': Project.objects.filter(
                manager=employee.user,
                status='in_progress'
            ).count(),
        }

class ProjectService:
    """Proje servisi."""
    
    @staticmethod
    def get_project_progress(project_id):
        """Proje ilerlemesini hesaplar."""
        project = Project.objects.get(id=project_id)
        
        # Görev tamamlanma oranı
        total_tasks = Task.objects.filter(project=project).count()
        completed_tasks = Task.objects.filter(
            project=project,
            status='completed'
        ).count()
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Bütçe kullanımı
        budget_utilization = project.budget_utilization
        
        return {
            'completion_rate': completion_rate,
            'budget_utilization': budget_utilization,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': Task.objects.filter(
                project=project,
                due_date__lt=timezone.now().date(),
                status__in=['planning', 'in_progress']
            ).count(),
        }

class TaskService:
    """Görev servisi."""
    
    @staticmethod
    def get_task_metrics(task_id):
        """Görev metriklerini hesaplar."""
        task = Task.objects.get(id=task_id)
        
        # Görev süresi
        task_duration = (task.due_date - task.created_at.date()).days
        
        # Öncelik puanı
        priority_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'urgent': 4
        }
        priority_score = priority_scores.get(task.priority, 1)
        
        return {
            'duration': task_duration,
            'priority_score': priority_score,
            'is_overdue': task.due_date < timezone.now().date(),
            'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else None,
        } 