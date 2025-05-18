import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Ortam değişkenlerini al veya varsayılan değerleri kullan
def get_env_value(key, default=None):
    """Ortam değişkenini al veya varsayılan değeri döndür"""
    return os.getenv(key, default)

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Genel ayarlar
SECRET_KEY = get_env_value('DJANGO_SECRET_KEY', 'your-secret-key-here')
DEBUG = str(get_env_value('DEBUG', 'False')).lower() == 'true'
