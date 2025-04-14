"""
Ortak yardımcı fonksiyonlar
"""
import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def generate_unique_filename(original_filename):
    """
    Benzersiz dosya adı oluşturur
    """
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4()}{ext}"

def save_uploaded_file(uploaded_file, path):
    """
    Yüklenen dosyayı kaydeder
    """
    filename = generate_unique_filename(uploaded_file.name)
    filepath = os.path.join(path, filename)
    saved_path = default_storage.save(filepath, ContentFile(uploaded_file.read()))
    return saved_path

def format_currency(amount, currency='TRY'):
    """
    Para birimini formatlar
    """
    from django.contrib.humanize.templatetags.humanize import intcomma
    return f"{intcomma(amount)} {currency}"

def get_client_ip(request):
    """
    İstemci IP adresini alır
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_activity(user, action, model, object_id, changes=None, request=None):
    """
    Kullanıcı aktivitelerini loglar
    """
    from .models import AuditLog
    
    ip_address = get_client_ip(request) if request else None
    
    AuditLog.objects.create(
        user=user,
        action=action,
        model=model,
        object_id=object_id,
        changes=changes or {},
        ip_address=ip_address
    ) 