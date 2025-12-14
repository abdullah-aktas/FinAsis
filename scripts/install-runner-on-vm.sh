#!/bin/bash
# VM üzerinde GitHub Actions runner kurulum scripti
# Bu script'i VM'e SSH ile bağlandıktan sonra çalıştırın

set -e

echo "🚀 GitHub Actions Runner kurulumu başlatılıyor..."

# Dizin hazırla
cd ~
mkdir -p actions-runner && cd actions-runner

# En son runner versiyonunu indir
RUNNER_VERSION="2.311.0"
echo "📥 Runner v${RUNNER_VERSION} indiriliyor..."
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
  -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo "📦 Runner arşivi açılıyor..."
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo "✅ Runner dosyaları hazır!"
echo ""
echo "📋 Sonraki adımlar:"
echo ""
echo "1. GitHub'dan token alın:"
echo "   https://github.com/abdullah-aktas/FinAsis/settings/actions/runners/new"
echo "   → 'Linux' seçin → Token'ı kopyalayın"
echo ""
echo "2. Runner'ı yapılandırın:"
echo "   ./config.sh --url https://github.com/abdullah-aktas/FinAsis --token YOUR_TOKEN"
echo ""
echo "3. Runner'ı servis olarak başlatın:"
echo "   sudo ./svc.sh install"
echo "   sudo ./svc.sh start"
echo ""
echo "4. Runner durumunu kontrol edin:"
echo "   sudo ./svc.sh status"

