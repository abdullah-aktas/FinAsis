# -*- coding: utf-8 -*-
import os
import codecs
from pathlib import Path

def detect_encoding(file_path):
    """Dosyanın karakter kodlamasını tespit et"""
    encodings = ['utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'iso-8859-9', 'windows-1254', 'ascii']
    
    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as f:
                f.read()
                return encoding
        except UnicodeDecodeError:
            continue
    return None

def fix_file_encoding(file_path):
    """Dosyanın kodlamasını UTF-8'e çevir"""
    try:
        # Önce mevcut kodlamayı tespit et
        detected_encoding = detect_encoding(file_path)
        
        if detected_encoding and detected_encoding != 'utf-8':
            # Dosyayı tespit edilen kodlama ile oku
            with codecs.open(file_path, 'r', encoding=detected_encoding) as f:
                content = f.read()
            
            # UTF-8 olarak kaydet
            with codecs.open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Düzeltildi: {file_path} ({detected_encoding} -> utf-8)")
            return True
        elif detected_encoding:
            print(f"Zaten UTF-8: {file_path}")
        else:
            print(f"Kodlama tespit edilemedi: {file_path}")
        
        return False
    except Exception as e:
        print(f"Hata oluştu ({file_path}): {str(e)}")
        return False

def process_po_files():
    """Tüm .po dosyalarını işle"""
    fixed_files = []
    excluded_dirs = {'.git', '__pycache__', 'node_modules', 'build', 'dist'}
    
    # Tüm dizinlerdeki .po dosyalarını bul
    for root, dirs, files in os.walk('.'):
        # Hariç tutulan dizinleri atla
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file.endswith('.po'):
                file_path = os.path.join(root, file)
                if fix_file_encoding(file_path):
                    fixed_files.append(file_path)
    
    return fixed_files

if __name__ == '__main__':
    print("PO dosyalarının kodlaması düzeltiliyor...")
    fixed_files = process_po_files()
    
    print("\nKodlama Düzeltme Raporu:")
    print(f"Toplam {len(fixed_files)} dosyanın kodlaması UTF-8'e çevrildi.")
    
    if fixed_files:
        print("\nDüzeltilen dosyalar:")
        for file in fixed_files:
            print(f"- {file}") 