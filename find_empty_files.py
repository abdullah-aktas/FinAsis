import os

def find_empty_files(directory):
    excluded_dirs = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'migrations'}
    empty_files = []
    
    for root, dirs, files in os.walk(directory):
        # Hariç tutulan dizinleri atla
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content or content == '# -*- coding: utf-8 -*-':
                            empty_files.append(file_path)
                except Exception as e:
                    print(f"Hata oluştu ({file_path}): {str(e)}")
    
    return empty_files

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    empty_files = find_empty_files(current_dir)
    
    print("Boş Python Dosyaları:")
    for file in empty_files:
        print(f"- {file}")
    print(f"\nToplam {len(empty_files)} boş dosya bulundu.") 