#!/bin/bash
# Self-hosted runner VM'i için gerekli araçları kurar
# VM'de çalıştırın: bash scripts/setup-vm-for-runner.sh

set -e

echo "🔧 Self-hosted runner VM kurulumu başlatılıyor..."

# Docker kurulumu
echo "🐳 Docker kurulumu kontrol ediliyor..."
if ! command -v docker &> /dev/null; then
  echo "📦 Docker kuruluyor..."
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker $USER
  echo "✅ Docker kuruldu (logout/login gerekebilir)"
else
  echo "✅ Docker zaten kurulu"
fi

# gcloud CLI kurulumu
echo "☁️  gcloud CLI kurulumu kontrol ediliyor..."
if ! command -v gcloud &> /dev/null; then
  echo "📦 gcloud CLI kuruluyor..."
  curl https://sdk.cloud.google.com | bash
  exec -l $SHELL
  echo "✅ gcloud CLI kuruldu"
else
  echo "✅ gcloud CLI zaten kurulu"
fi

# Git kurulumu
echo "📝 Git kurulumu kontrol ediliyor..."
if ! command -v git &> /dev/null; then
  echo "📦 Git kuruluyor..."
  sudo apt-get update
  sudo apt-get install -y git
  echo "✅ Git kuruldu"
else
  echo "✅ Git zaten kurulu"
fi

# Docker servisini başlat
echo "🚀 Docker servisi başlatılıyor..."
sudo systemctl start docker
sudo systemctl enable docker

echo ""
echo "✅ VM kurulumu tamamlandı!"
echo ""
echo "📋 Kontrol:"
echo "   docker --version"
echo "   gcloud --version"
echo "   git --version"

