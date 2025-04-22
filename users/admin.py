from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Kullanıcı Profili')
    fk_name = 'user'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Kişisel Bilgiler'), {'fields': ('username', 'first_name', 'last_name', 'phone_number', 'profile_image')}),
        (_('İzinler'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Önemli Tarihler'), {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    inlines = [UserProfileInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'job_title', 'birth_date')
    search_fields = ('user__email', 'user__username', 'company_name')
    list_filter = ('birth_date',)
    readonly_fields = ('user',) 