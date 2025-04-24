from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, Tag, Vote, Badge, UserProfile

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'published_at', 'view_count', 'language')
    list_filter = ('status', 'created_at', 'language', 'tags')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {}
    raw_id_fields = ('author', 'tags')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at', 'is_answer')
    list_filter = ('created_at', 'is_answer')
    search_fields = ('content', 'author__username', 'post__title')
    raw_id_fields = ('post', 'author', 'parent')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'post', 'comment')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise_level', 'points', 'preferred_language')
    list_filter = ('expertise_level', 'preferred_language')
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'badges')
    filter_horizontal = ('badges',) 