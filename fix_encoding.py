#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import chardet
import logging
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple

# Özel istisna sınıfı
class EncodingError(Exception):
    pass

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('encoding_fix.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# İşlenecek dosya uzantıları
SUPPORTED_EXTENSIONS = {
    '.py', '.html', '.js', '.css', '.po', '.txt', '.md', 
    '.json', '.yml', '.yaml', '.ini', '.conf', '.sh', '.bat'
}

# Hariç tutulacak dizinler
EXCLUDED_DIRS = {
    '.git', 'venv', '.venv', '__pycache__', 'node_modules',
    'build', 'dist', '.pytest_cache', '.mypy_cache'
}

EXCLUDED_FILES = {
    'xregexp.min.js',
    'swagger-ui-bundle.js',
    'swagger-ui-es-bundle.js',
    'swagger-ui-standalone-preset.js'
}

class EncodingStatistics:
    def __init__(self):
        self.total_files = 0
        self.fixed_files = 0
        self.failed_files = 0
        self.skipped_files = 0
        self.encoding_counts: Dict[str, int] = {}
        self.failed_files_list: List[Tuple[str, str]] = []
        self.fixed_files_list: List[Tuple[str, str, str]] = []
        self.start_time = time.time()

    def add_encoding(self, encoding: str):
        if encoding:
            normalized_encoding = encoding.lower()
            self.encoding_counts[normalized_encoding] = self.encoding_counts.get(normalized_encoding, 0) + 1

    def get_execution_time(self) -> float:
        return time.time() - self.start_time

def detect_encoding(file_path: str) -> str:
    """Dosyanın karakter kodlamasını tespit et"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            if not raw_data:
                return 'utf-8'  # Boş dosyalar için varsayılan UTF-8
            result = chardet.detect(raw_data)
            return result['encoding'] if result['encoding'] else 'utf-8'
    except Exception as e:
        logger.error(f"Kodlama tespiti başarısız ({file_path}): {str(e)}")
        return 'utf-8'

def fix_file_encoding(file_path: str, stats: EncodingStatistics) -> bool:
    """Dosyanın kodlamasını UTF-8'e çevir"""
    try:
        detected_encoding = detect_encoding(file_path)
        stats.add_encoding(detected_encoding)
        
        if not detected_encoding or detected_encoding.lower() == 'utf-8':
            stats.skipped_files += 1
            return False

        # Tüm dosyalar için denenecek kodlamalar
        encodings_to_try = [
            detected_encoding,
            'utf-8',
            'windows-1254',
            'iso-8859-9',
            'iso-8859-1',
            'windows-1252',
            'ascii',
            'latin1',
            'cp1254',
            'macroman'
        ]
        
        content = None
        used_encoding = detected_encoding
        
        for enc in encodings_to_try:
            if not enc:
                continue
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                used_encoding = enc
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Okuma hatası ({file_path}, {enc}): {str(e)}")
                continue
        
        if content is None:
            raise EncodingError(f"Hiçbir kodlama ile dosya okunamadı: {file_path}")
        
        # UTF-8 olarak yeniden yaz
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        
        stats.fixed_files += 1
        stats.fixed_files_list.append((file_path, str(used_encoding), 'utf-8'))  # str() ile dönüşüm
        logger.info(f"Düzeltildi: {file_path} ({used_encoding} -> utf-8)")
        return True

    except Exception as e:
        stats.failed_files += 1
        stats.failed_files_list.append((file_path, str(e)))
        logger.error(f"Hata oluştu ({file_path}): {str(e)}")
        return False

def should_process_file(file_path: str) -> bool:
    """Dosyanın işlenmesi gerekip gerekmediğini kontrol et"""
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Desteklenen uzantıları genişlet
    SUPPORTED_EXTENSIONS.update({
        '.jsx', '.tsx', '.ts', '.vue', '.php',
        '.rb', '.java', '.jsp', '.asp', '.aspx',
        '.htm', '.shtml', '.xml', '.svg', '.sql',
        '.properties', '.env', '.cfg', '.toml'
    })
    
    return (
        (file_ext in SUPPORTED_EXTENSIONS or not file_ext)  # Uzantısız dosyaları da işle
        and os.path.getsize(file_path) < 10 * 1024 * 1024  # 10MB'dan küçük dosyalar
        and file_name not in EXCLUDED_FILES
    )

def process_directory(directory: str, stats: EncodingStatistics):
    """Dizindeki tüm dosyaları paralel olarak işle"""
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for root, dirs, files in os.walk(directory):
            # Hariç tutulan dizinleri atla
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            
            for file in files:
                file_path = os.path.join(root, file)
                if should_process_file(file_path):
                    stats.total_files += 1
                    executor.submit(fix_file_encoding, file_path, stats)

def print_report(stats: EncodingStatistics):
    """Detaylı rapor yazdır"""
    print("\n=== Kodlama Düzeltme Raporu ===")
    print(f"\nİşlem Süresi: {stats.get_execution_time():.2f} saniye")
    print(f"\nİstatistikler:")
    print(f"- Toplam taranan dosya: {stats.total_files}")
    print(f"- Düzeltilen dosya: {stats.fixed_files}")
    print(f"- Atlanan dosya: {stats.skipped_files}")
    print(f"- Başarısız dosya: {stats.failed_files}")
    
    print("\nTespit Edilen Kodlamalar:")
    for encoding, count in sorted(stats.encoding_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"- {encoding}: {count} dosya")
    
    if stats.fixed_files_list:
        print("\nDüzeltilen Dosyalar:")
        for file_path, old_enc, new_enc in stats.fixed_files_list:
            print(f"- {file_path} ({old_enc} -> {new_enc})")
    
    if stats.failed_files_list:
        print("\nBaşarısız Olan Dosyalar:")
        for file_path, error in stats.failed_files_list:
            print(f"- {file_path}: {error}")

def main():
    current_dir = str(Path(__file__).resolve().parent)
    logger.info(f"İşlem başlatılıyor: {current_dir}")
    
    stats = EncodingStatistics()
    process_directory(current_dir, stats)
    print_report(stats)

if __name__ == '__main__':
    main() 