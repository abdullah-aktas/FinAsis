import os
import re
from pathlib import Path

# Ayarlar
APP_NAME = "crm"  # Django app adınız
MODELS_FILE = Path(f"{APP_NAME}/models.py")
MODELS_DIR = Path(f"{APP_NAME}/models")
INIT_FILE = MODELS_DIR / "__init__.py"

# Hedef dizini oluştur
MODELS_DIR.mkdir(exist_ok=True)

# models.py içeriğini oku
with open(MODELS_FILE, encoding='utf-8') as f:
    lines = f.readlines()

header_lines = []
model_blocks = []

buffer = []
in_model = False
model_name = ""

# Tüm sınıfları bloklara ayır
for line in lines:
    # İçe aktarmaları ayır
    if not in_model and not line.strip().startswith("class"):
        header_lines.append(line)
        continue

    # Model başlangıcı
    match = re.match(r"^class\s+(\w+)\((models\.Model|.+?)\):", line)
    if match:
        if buffer:
            model_blocks.append((model_name, buffer))
        model_name = match.group(1)
        buffer = [line]
        in_model = True
    elif in_model:
        buffer.append(line)

# Son modeli ekle
if buffer:
    model_blocks.append((model_name, buffer))

# Her model için ayrı dosya oluştur
print("📦 Modeller modüllere bölünüyor...\n")
init_imports = []

for model_name, block in model_blocks:
    file_name = f"{model_name.lower()}.py"
    file_path = MODELS_DIR / file_name
    with open(file_path, "w", encoding='utf-8') as f:
        f.writelines(header_lines)
        f.write("\n")
        f.writelines(block)
    init_imports.append(f"from .{model_name.lower()} import {model_name}")
    print(f"✅ {file_name} oluşturuldu.")

# __init__.py dosyasını oluştur
with open(INIT_FILE, "w", encoding='utf-8') as f:
    f.write("\n".join(init_imports))
    f.write("\n")

print("\n🎉 Tüm modeller başarıyla modüllere ayrıldı!")
