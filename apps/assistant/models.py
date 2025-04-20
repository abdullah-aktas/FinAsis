from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    page_context = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        app_label = 'assistant'

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['created_at']
        app_label = 'assistant'

class PagePrompt(models.Model):
    page_path = models.CharField(max_length=255)
    prompt_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['page_path']
        app_label = 'assistant' 