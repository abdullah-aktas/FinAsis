# FinAsis CI/CD Süreçleri

*Son Güncelleme: 22.04.2025*

## 📋 Genel Bakış

FinAsis CI/CD (Sürekli Entegrasyon/Sürekli Dağıtım) süreçleri, yazılım geliştirme ve dağıtım süreçlerini otomatikleştiren, kalite ve güvenliği artıran bir çözümdür.

## 🎯 Özellikler

- Otomatik test çalıştırma
- Kod kalite kontrolü
- Güvenlik taraması
- Otomatik dağıtım
- Versiyon yönetimi
- Çevre yönetimi
- Geri alma mekanizması
- İzleme ve raporlama

## 🔧 Kurulum

### Gereksinimler
- Git 2.30+
- Docker 20.10+
- Jenkins 2.300+
- SonarQube 8.0+
- Kubernetes 1.20+

### Kurulum Adımları
1. Jenkins kurulumu:
```bash
docker run -d -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
```

2. SonarQube kurulumu:
```bash
docker run -d -p 9000:9000 sonarqube:latest
```

3. CI/CD pipeline'ını yapılandırın:
```bash
cp .github/workflows/ci-cd.yml.example .github/workflows/ci-cd.yml
```

## 🛠️ Yapılandırma

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t finasis .'
            }
        }
        stage('Test') {
            steps {
                sh 'python manage.py test'
                sh 'npm run test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl apply -f k8s/'
            }
        }
    }
}
```

### GitHub Actions
```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python manage.py test
```

## 📊 Kullanım

### Kod Push Etme
```bash
# Yeni özellik dalı oluştur
git checkout -b feature/new-feature

# Değişiklikleri commit et
git add .
git commit -m "Yeni özellik eklendi"

# Uzak depoya gönder
git push origin feature/new-feature
```

### Pull Request Oluşturma
```bash
# GitHub'da PR oluştur
gh pr create --title "Yeni özellik" --body "Açıklama"

# PR'ı birleştir
gh pr merge 1 --merge
```

### Manuel Dağıtım
```bash
# Staging ortamına dağıt
kubectl apply -f k8s/staging/

# Production ortamına dağıt
kubectl apply -f k8s/production/
```

## 🔍 Örnek Kullanımlar

### Otomatik Test Çalıştırma
```yaml
- name: Run Tests
  run: |
    python manage.py test
    npm run test
    sonar-scanner
```

### Güvenlik Taraması
```yaml
- name: Security Scan
  run: |
    trivy image finasis:latest
    snyk test
```

## 🧪 Test

### Test Ortamı
```bash
# Test ortamını başlat
docker-compose -f docker-compose.test.yml up -d

# Testleri çalıştır
pytest tests/
```

### Test Kapsamı
- Birim testleri
- Entegrasyon testleri
- E2E testleri
- Performans testleri
- Güvenlik testleri

## 📈 Performans

### Ölçümler
- Build süresi: < 5 dakika
- Test süresi: < 10 dakika
- Dağıtım süresi: < 5 dakika
- Geri alma süresi: < 2 dakika

### Optimizasyon
- Paralel test çalıştırma
- Önbellekleme
- Artırımlı build
- Kaynak optimizasyonu

## 🔒 Güvenlik

### CI/CD Güvenliği
- Kimlik doğrulama
- Yetkilendirme
- Gizli bilgi yönetimi
- Güvenlik taraması

### Dağıtım Güvenliği
- Şifreleme
- Erişim kontrolü
- Denetim kayıtları
- Güvenlik politikaları

## 📚 Dokümantasyon

### API Dokümantasyonu
- [API Referansı](api.md)
- [Örnek Kodlar](examples.md)
- [Hata Kodları](errors.md)

### Kullanıcı Kılavuzu
- [Başlangıç Kılavuzu](getting_started.md)
- [Gelişmiş Özellikler](advanced_features.md)
- [SSS](faq.md)

## 🤝 Katkıda Bulunma

### Geliştirme Kuralları
1. PEP 8 standartlarına uyun
2. Birim testleri yazın
3. Dokümantasyonu güncelleyin
4. Pull request açın

### Kod İnceleme Süreci
1. Kod incelemesi
2. Test sonuçları
3. Performans değerlendirmesi
4. Onay ve birleştirme

## 📞 Destek

### İletişim
- E-posta: cicd-support@finasis.com
- Slack: #cicd-support
- GitHub Issues

### SLA
- Yanıt süresi: 24 saat
- Çözüm süresi: 72 saat
- Uptime: %99.9 