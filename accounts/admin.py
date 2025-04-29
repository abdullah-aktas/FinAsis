# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    Özelleştirilmiş kullanıcı admin paneli.
    Kullanıcı rollerini ve sanal şirket kullanıcısı olup olmadığını gösterir.
    """
    list_display = ('username', 'email', 'role', 'is_virtual_company_user', 'is_staff', 'is_active')
    list_filter = ('role', 'is_virtual_company_user', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email')}),
        ('İzinler', {'fields': ('role', 'is_virtual_company_user', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_virtual_company_user'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin) 