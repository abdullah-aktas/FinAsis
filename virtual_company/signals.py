from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, StockMovement, ProductionOrder, Company, Department, Employee, Project, Task

@receiver(post_save, sender=StockMovement)
def update_product_stock(sender, instance, created, **kwargs):
    if created:
        cache.delete(f'product_stock_{instance.product.id}')

@receiver([post_save, post_delete], sender=ProductionOrder)
def clear_production_cache(sender, instance, **kwargs):
    cache.delete(f'production_orders_{instance.product.id}')
    cache.delete('active_production_orders')

@receiver(post_save, sender=Company)
def company_saved(sender, instance, created, **kwargs):
    """Şirket kaydedildiğinde önbelleği temizle."""
    cache.delete(f'company_{instance.id}')
    cache.delete('all_companies')

@receiver(post_delete, sender=Company)
def company_deleted(sender, instance, **kwargs):
    """Şirket silindiğinde önbelleği temizle."""
    cache.delete(f'company_{instance.id}')
    cache.delete('all_companies')

@receiver(post_save, sender=Department)
def department_saved(sender, instance, created, **kwargs):
    """Departman kaydedildiğinde önbelleği temizle."""
    cache.delete(f'department_{instance.id}')
    cache.delete(f'company_{instance.company.id}_departments')

@receiver(post_delete, sender=Department)
def department_deleted(sender, instance, **kwargs):
    """Departman silindiğinde önbelleği temizle."""
    cache.delete(f'department_{instance.id}')
    cache.delete(f'company_{instance.company.id}_departments')

@receiver(post_save, sender=Employee)
def employee_saved(sender, instance, created, **kwargs):
    """Çalışan kaydedildiğinde önbelleği temizle."""
    cache.delete(f'employee_{instance.id}')
    cache.delete(f'company_{instance.company.id}_employees')

@receiver(post_delete, sender=Employee)
def employee_deleted(sender, instance, **kwargs):
    """Çalışan silindiğinde önbelleği temizle."""
    cache.delete(f'employee_{instance.id}')
    cache.delete(f'company_{instance.company.id}_employees')

@receiver(post_save, sender=Project)
def project_saved(sender, instance, created, **kwargs):
    """Proje kaydedildiğinde önbelleği temizle."""
    cache.delete(f'project_{instance.id}')
    cache.delete(f'company_{instance.company.id}_projects')

@receiver(post_delete, sender=Project)
def project_deleted(sender, instance, **kwargs):
    """Proje silindiğinde önbelleği temizle."""
    cache.delete(f'project_{instance.id}')
    cache.delete(f'company_{instance.company.id}_projects')

@receiver(post_save, sender=Task)
def task_saved(sender, instance, created, **kwargs):
    """Görev kaydedildiğinde önbelleği temizle."""
    cache.delete(f'task_{instance.id}')
    cache.delete(f'project_{instance.project.id}_tasks')

@receiver(post_delete, sender=Task)
def task_deleted(sender, instance, **kwargs):
    """Görev silindiğinde önbelleği temizle."""
    cache.delete(f'task_{instance.id}')
    cache.delete(f'project_{instance.project.id}_tasks') 