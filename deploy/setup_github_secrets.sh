#!/bin/bash
# GitHub Secrets kurulum rehberi
# Bu script size adım adım rehberlik eder

echo "🔐 GitHub Secrets Kurulum Rehberi"
echo "=================================="
echo ""

# 1. SECRET_KEY oluştur
echo "📝 1. DJANGO_SECRET_KEY oluşturuluyor..."
if command -v python3 &> /dev/null; then
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(50)))")
else
    echo "⚠️  Python bulunamadı, manuel oluşturmanız gerekecek"
    SECRET_KEY=""
fi

if [ -n "$SECRET_KEY" ]; then
    echo "✅ SECRET_KEY oluşturuldu:"
    echo "   ${SECRET_KEY:0:20}... (ilk 20 karakter)"
    echo ""
    echo "📋 Tam değer:"
    echo "$SECRET_KEY"
    echo ""
else
    echo "⚠️  SECRET_KEY oluşturulamadı"
    echo "   Manuel olarak oluşturun: https://djecrety.ir/"
    echo ""
fi

# 2. Rehber
echo "=================================="
echo "📋 GitHub Secrets Ekleme Adımları:"
echo "=================================="
echo ""
echo "1. GitHub'a gidin: https://github.com/abdullah-aktas/FinAsis/settings/secrets/actions"
echo ""
echo "2. 'New repository secret' butonuna tıklayın"
echo ""
echo "3. DJANGO_SECRET_KEY ekleyin:"
echo "   - Name: DJANGO_SECRET_KEY"
if [ -n "$SECRET_KEY" ]; then
    echo "   - Secret: (yukarıdaki değeri kopyalayın)"
else
    echo "   - Secret: (https://djecrety.ir/ adresinden oluşturun)"
fi
echo ""
echo "4. Tekrar 'New repository secret' butonuna tıklayın"
echo ""
echo "5. DJANGO_DB_PASSWORD ekleyin:"
echo "   - Name: DJANGO_DB_PASSWORD"
echo "   - Secret: (PostgreSQL şifrenizi girin)"
echo "   - Not: Eğer şifreyi bilmiyorsanız, Cloud SQL'den reset edin:"
echo "     gcloud sql users set-password finasis-app --instance=finasis-db --password=YENI_SIFRE"
echo ""
echo "=================================="
echo "✅ Secrets'ları ekledikten sonra yeni bir deployment yapın!"
echo "=================================="

