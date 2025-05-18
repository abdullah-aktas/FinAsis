import os

def add_utf8_encoding(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Eğer dosya boşsa veya sadece UTF-8 kodlama satırı varsa
        if not content.strip() or content.strip() == '# -*- coding: utf-8 -*-':
            return
        
        # Eğer dosyada zaten UTF-8 kodlama satırı varsa
        if '# -*- coding: utf-8 -*-' in content:
            return
        
        # Dosyanın başına UTF-8 kodlama satırı ekle
        new_content = '# -*- coding: utf-8 -*-\n' + content
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        print(f"UTF-8 kodlama satırı eklendi: {file_path}")
            
    except Exception as e:
        print(f"Hata oluştu ({file_path}): {str(e)}")

def process_directory(directory):
    excluded_dirs = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'migrations'}
    
    for root, dirs, files in os.walk(directory):
        # Hariç tutulan dizinleri atla
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                add_utf8_encoding(file_path)

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    process_directory(current_dir)
    print("İşlem tamamlandı!") 