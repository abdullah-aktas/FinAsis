#!/bin/bash
# Git merge conflict çözümü - Cloud Shell için
# Kullanım: bash scripts/fix-git-merge-conflict.sh

set -e

echo "🔧 Git merge conflict çözülüyor..."

# Çakışan migration dosyalarını sil (zaten uygulanmış)
echo "🗑️  Çakışan migration dosyaları temizleniyor..."
rm -f accounting/migrations/0018_alter_bankaccount_options_alter_product_options.py
rm -f accounts/migrations/0014_alter_rolebaseduserprofile_options.py
rm -f ai_assistant/migrations/0004_alter_financialreport_options_and_more.py
rm -f corporate/migrations/0004_alter_partnerapplication_options_and_more.py
rm -f education/migrations/0014_alter_badge_options_alter_tournament_options.py
rm -f finance/accounting/migrations/0007_alter_invoice_options.py
rm -f finance/migrations/0017_alter_account_options_alter_invoice_options_and_more.py
rm -f games/migrations/0016_alter_badge_options_alter_playerinventory_options_and_more.py
rm -f games/trade_sim/migrations/0002_alter_tournament_options.py
rm -f kobi_analysis/migrations/0004_alter_performancemetric_options.py
rm -f management/migrations/0005_alter_notification_options_and_more.py
rm -f security/migrations/0004_alter_securityincident_options.py
rm -f virtual_company/migrations/0003_alter_financereport_options_alter_invoice_options_and_more.py

echo "✅ Dosyalar temizlendi"

# Git pull tekrar dene
echo "📥 Git pull yapılıyor..."
git pull origin main

echo "✅ Git pull tamamlandı"

# Common migration'ını uygula
echo "🔄 Common migration'ı uygulanıyor..."
python manage.py migrate common

echo "✅ Tüm işlemler tamamlandı!"

