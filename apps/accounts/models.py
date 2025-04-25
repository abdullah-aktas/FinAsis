from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Company(models.Model):
    name = models.CharField(max_length=100)
    tax_number = models.CharField(max_length=20)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    user_limit = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_active_user_count(self):
        return self.user_set.filter(is_active=True).count()

    def can_add_user(self):
        return self.get_active_user_count() < self.user_limit

    def create_default_roles(self):
        default_roles = [
            {
                'name': 'İnsan Kaynakları Yöneticisi',
                'permissions': {
                    'can_manage_employees': True,
                    'can_view_employee_data': True,
                    'can_manage_leave_requests': True,
                    'can_manage_recruitment': True,
                    'can_view_hr_reports': True
                }
            },
            {
                'name': 'Müşteri İlişkileri Sorumlusu',
                'permissions': {
                    'can_manage_customers': True,
                    'can_view_customer_data': True,
                    'can_manage_support_tickets': True,
                    'can_send_customer_communications': True,
                    'can_view_customer_reports': True
                }
            },
            {
                'name': 'Lojistik Sorumlusu',
                'permissions': {
                    'can_manage_inventory': True,
                    'can_manage_shipments': True,
                    'can_view_supply_chain': True,
                    'can_manage_warehouse': True,
                    'can_view_logistics_reports': True
                }
            }
        ]
        
        for role_data in default_roles:
            Role.objects.create(
                name=role_data['name'],
                description=f"{role_data['name']} için varsayılan rol",
                permissions=role_data['permissions'],
                company=self
            )

class Role(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    permissions = models.JSONField(default=dict)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

    class Meta:
        unique_together = ('name', 'company')

class User(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=50, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_company_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}"
        return self.username[0:2].upper()

    def has_permission(self, permission):
        if self.is_superuser:
            return True
        if not self.role:
            return False
        return permission in self.role.permissions

    def save(self, *args, **kwargs):
        if self.company and not self.company.can_add_user():
            raise ValueError("Kullanıcı limiti aşıldı")
        super().save(*args, **kwargs)

class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}" 