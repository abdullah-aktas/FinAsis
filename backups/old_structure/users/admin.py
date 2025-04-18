from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'company', 'position', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'company')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'company')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('username', 'first_name', 'last_name', 'phone')}),
        ('Şirket Bilgileri', {'fields': ('company', 'position')}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
class AIModelAdmin(admin.ModelAdmin):
    readonly_fields = ('last_trained',)
    exclude = ('last_trained',)
