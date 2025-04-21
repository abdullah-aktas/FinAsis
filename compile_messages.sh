#!/bin/bash
# compile_messages.sh - Django çeviri dosyalarını derler
set -e

echo "FinAsis Çeviri Derleme Betiği"
echo "============================="

# Sanal ortamın etkin olup olmadığını kontrol et
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Hata: Sanal ortam (virtualenv) etkin değil!"
    echo "Lütfen önce sanal ortamı etkinleştirin:"
    echo "  source venv/bin/activate    # Linux/macOS"
    echo "  venv\\Scripts\\activate       # Windows"
    exit 1
fi

# Django'nun yüklü olup olmadığını kontrol et
if ! python -c "import django" &> /dev/null; then
    echo "Hata: Django yüklü değil!"
    echo "Lütfen önce gerekli paketleri yükleyin:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# gettext'in yüklü olup olmadığını kontrol et
if ! command -v msgfmt &> /dev/null; then
    echo "Hata: gettext yüklü değil!"
    echo "Lütfen gettext paketini yükleyin:"
    echo "  sudo apt-get install gettext    # Ubuntu/Debian"
    echo "  brew install gettext            # macOS"
    echo "  choco install gettext           # Windows (Chocolatey)"
    exit 1
fi

# Çeviri Derle
echo "Çeviri dosyaları derleniyor..."
python manage.py compilemessages

if [ $? -eq 0 ]; then
    echo "✓ Çeviri dosyaları başarıyla derlendi."
else
    echo "✗ Çeviri dosyaları derlenirken bir hata oluştu!"
    exit 1
fi

# Çevrilebilir metinleri çıkar
echo "Çevrilebilir metinler çıkartılıyor..."
python manage.py makemessages -l tr
python manage.py makemessages -l en
python manage.py makemessages -l ar
python manage.py makemessages -l ku
python manage.py makemessages -l de

if [ $? -eq 0 ]; then
    echo "✓ Çevrilebilir metinler başarıyla çıkartıldı."
else
    echo "✗ Çevrilebilir metinler çıkartılırken bir hata oluştu!"
    exit 1
fi

echo ""
echo "Şimdi 'locale/' dizinindeki .po dosyalarını düzenleyebilirsiniz."
echo "Düzenlemeyi tamamladıktan sonra bu betiği tekrar çalıştırın." 