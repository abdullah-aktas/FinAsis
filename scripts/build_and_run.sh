#!/bin/bash

echo "FinAsis Kurulum ve Çalıştırma Scripti"
echo "================================="
echo ""

# Python yüklü mü kontrol et
if ! command -v python3 &> /dev/null; then
    echo "Python bulunamadı! Lütfen Python 3.9 veya üzerini yükleyin."
    echo "https://www.python.org/downloads/"
    exit 1
fi

# Sanal ortam var mı kontrol et
if [ ! -d "venv" ]; then
    echo "Sanal ortam oluşturuluyor..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Sanal ortam oluşturulamadı!"
        exit 1
    fi
fi

# Sanal ortamı etkinleştir
echo "Sanal ortam etkinleştiriliyor..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Sanal ortam etkinleştirilemedi!"
    exit 1
fi

# Gerekli paketleri yükle
echo "Gerekli paketler yükleniyor..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Paket yüklemesi başarısız oldu!"
    exit 1
fi

# PyInstaller yüklü mü kontrol et
if ! pip show pyinstaller &> /dev/null; then
    echo "PyInstaller yükleniyor..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "PyInstaller yüklenemedi!"
        exit 1
    fi
fi

# Masaüstü uygulaması derleme scripti var mı kontrol et
if [ ! -f "build_desktop.py" ]; then
    echo "build_desktop.py bulunamadı!"
    exit 1
fi

echo ""
echo "Masaüstü uygulaması derleniyor..."
python build_desktop.py
if [ $? -ne 0 ]; then
    echo "Masaüstü uygulaması derlenirken hata oluştu!"
    exit 1
fi

echo ""
echo "Derleme başarılı!"
echo ""

while true; do
    echo "Ne yapmak istersiniz?"
    echo "1 - Masaüstü uygulamasını çalıştır"
    echo "2 - Django geliştirme sunucusunu başlat"
    echo "3 - Veritabanını oluştur/güncelle"
    echo "4 - Çık"
    echo ""
    
    read -p "Seçiminiz: " choice
    
    case $choice in
        1)
            echo "Masaüstü uygulaması başlatılıyor..."
            if [ "$(uname)" == "Darwin" ]; then
                # macOS
                open dist/FinAsis.app
            else
                # Linux
                ./dist/FinAsis
            fi
            ;;
        2)
            echo "Django geliştirme sunucusu başlatılıyor..."
            python manage.py runserver
            ;;
        3)
            echo "Veritabanı oluşturuluyor/güncelleniyor..."
            python manage.py migrate
            echo ""
            echo "İşlem tamamlandı!"
            ;;
        4)
            echo ""
            echo "Çıkılıyor..."
            deactivate
            exit 0
            ;;
        *)
            echo ""
            echo "Geçersiz seçim!"
            ;;
    esac
    
    echo ""
done 