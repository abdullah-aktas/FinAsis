from django.contrib import admin
from .models import (
    Theme, Banner, NavigationMenu, MenuItem, Page,
    Widget, UIComponent, UserThemePreference
)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_default', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_default', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'thumbnail')
        }),
        ('Renkler', {
            'fields': ('primary_color', 'secondary_color', 'success_color', 'danger_color', 'warning_color', 'info_color', 'background_color', 'text_color')
        }),
        ('Tipografi', {
            'fields': ('font_family', 'font_size_base')
        }),
        ('Layout', {
            'fields': ('border_radius', 'box_shadow')
        }),
        ('Özel', {
            'fields': ('custom_css',),
            'classes': ('collapse',)
        }),
        ('Durum', {
            'fields': ('is_active', 'is_default', 'created_by')
        }),
    )


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'position', 'is_active', 'priority', 'start_date', 'end_date', 'view_count', 'click_count')
    search_fields = ('title', 'message')
    list_filter = ('banner_type', 'position', 'is_active', 'created_at')
    readonly_fields = ('view_count', 'click_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('İçerik', {
            'fields': ('title', 'message', 'banner_type', 'position')
        }),
        ('Aksiyon', {
            'fields': ('button_text', 'button_url')
        }),
        ('Hedefleme', {
            'fields': ('show_to_guests', 'show_to_authenticated', 'target_roles')
        }),
        ('Zamanlama', {
            'fields': ('start_date', 'end_date', 'priority')
        }),
        ('Ayarlar', {
            'fields': ('is_active', 'is_dismissible', 'created_by')
        }),
        ('İstatistikler', {
            'fields': ('view_count', 'click_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NavigationMenu)
class NavigationMenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'menu_type', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('menu_type', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ('title', 'url', 'icon', 'order', 'is_active', 'badge_text', 'badge_color')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'parent', 'url', 'order', 'is_active')
    search_fields = ('title', 'url')
    list_filter = ('menu', 'is_active', 'created_at')
    inlines = [MenuItemInline]


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'page_type', 'is_published', 'view_count', 'author', 'created_at')
    search_fields = ('title', 'content', 'meta_description')
    list_filter = ('page_type', 'is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'page_type', 'excerpt', 'featured_image')
        }),
        ('İçerik', {
            'fields': ('content',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Tema & Özelleştirme', {
            'fields': ('theme', 'custom_css', 'custom_js'),
            'classes': ('collapse',)
        }),
        ('Yayın', {
            'fields': ('is_published', 'published_at', 'author')
        }),
        ('İstatistikler', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'position', 'order', 'is_active', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('widget_type', 'position', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UIComponent)
class UIComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'component_type', 'version', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('component_type', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserThemePreference)
class UserThemePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'dark_mode', 'auto_dark_mode', 'font_size', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('dark_mode', 'auto_dark_mode', 'font_size', 'updated_at')
    readonly_fields = ('updated_at',)

