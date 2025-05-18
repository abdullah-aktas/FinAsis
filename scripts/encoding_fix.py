#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import chardet
from pathlib import Path

def detect_and_fix_encoding(file_path):
    """Dosyanın encoding'ini tespit et ve UTF-8'e dönüştür"""
    try:
        # Dosya içeriğini oku
        with open(file_path, 'rb') as file:
            raw_content = file.read()
        
        # Encoding'i tespit et
        detection = chardet.detect(raw_content)
        detected_encoding = detection['encoding']
        
        # Eğer UTF-8 değilse, dönüştür
        if detected_encoding and detected_encoding.lower() != 'utf-8':
            content = raw_content.decode(detected_encoding)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✓ {file_path}: {detected_encoding} -> UTF-8")
        
    except Exception as e:
        print(f"✗ Hata ({file_path}): {str(e)}")

def main():
    project_root = Path(__file__).parent.parent
    extensions = ('.py', '.html', '.js', '.css', '.md', '.txt')
    
    print("Encoding Düzeltme Aracı")
    print("=======================")
    
    for path in project_root.rglob('*'):
        if path.is_file() and path.suffix in extensions:
            detect_and_fix_encoding(str(path))

if __name__ == "__main__":
    main()
