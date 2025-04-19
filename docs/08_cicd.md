# 8. CI/CD Süreçleri

## 📌 Amaç
Bu dokümantasyon, FinAsis projesinin sürekli entegrasyon ve sürekli dağıtım (CI/CD) süreçlerini detaylandırmaktadır.

## ⚙️ Teknik Yapı

### 1. GitHub Actions Yapılandırması

#### 1.1. Ana CI/CD İş Akışı
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: finasis_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/finasis_test
        REDIS_URL: redis://localhost:6379/0
      run: |
        python manage.py test
    
    - name: Run linting
      run: |
        flake8 .
        black . --check
        isort . --check-only

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: eu-central-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: finasis
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster finasis-cluster --service finasis-service --force-new-deployment
```

#### 1.2. Güvenlik Taraması
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
    
    - name: Run Bandit
      run: |
        pip install bandit
        bandit -r .
    
    - name: Run Safety
      run: |
        pip install safety
        safety check
```

### 2. Docker Yapılandırması

#### 2.1. Geliştirme Ortamı
```dockerfile
# Dockerfile.dev
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### 2.2. Üretim Ortamı
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "finasis.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 3. Kubernetes Yapılandırması

#### 3.1. Deployment
```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finasis
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finasis
  template:
    metadata:
      labels:
        app: finasis
    spec:
      containers:
      - name: finasis
        image: ${ECR_REGISTRY}/finasis:${IMAGE_TAG}
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: finasis-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: finasis-secrets
              key: redis-url
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 3.2. Service
```yaml
# k8s/service.yml
apiVersion: v1
kind: Service
metadata:
  name: finasis
  namespace: production
spec:
  selector:
    app: finasis
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔧 Kullanım Adımları

### 1. Geliştirme Ortamı Kurulumu

#### 1.1. Docker Compose ile Başlatma
```bash
# Geliştirme ortamını başlat
docker-compose -f docker-compose.dev.yml up -d

# Logları izle
docker-compose -f docker-compose.dev.yml logs -f

# Servisleri durdur
docker-compose -f docker-compose.dev.yml down
```

#### 1.2. Veritabanı Migrasyonları
```bash
# Migrasyon oluştur
docker-compose -f docker-compose.dev.yml exec web python manage.py makemigrations

# Migrasyonları uygula
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### 2. Üretim Ortamı Dağıtımı

#### 2.1. Manuel Dağıtım
```bash
# AWS ECR'a giriş yap
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com

# Docker imajını oluştur ve gönder
docker build -t finasis .
docker tag finasis:latest ${AWS_ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com/finasis:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com/finasis:latest

# Kubernetes'e dağıt
kubectl apply -f k8s/
```

#### 2.2. Otomatik Dağıtım
```bash
# GitHub Actions ile dağıtımı tetikle
git push origin main
```

## 🧪 Test Örnekleri

### 1. CI Pipeline Testi
```python
# tests/test_ci.py
import os
import subprocess

def test_ci_pipeline():
    # Linting testleri
    result = subprocess.run(['flake8', '.'], capture_output=True, text=True)
    assert result.returncode == 0, f"Linting failed: {result.stdout}"
    
    # Format testleri
    result = subprocess.run(['black', '.', '--check'], capture_output=True, text=True)
    assert result.returncode == 0, f"Formatting failed: {result.stdout}"
    
    # Import sıralama testleri
    result = subprocess.run(['isort', '.', '--check-only'], capture_output=True, text=True)
    assert result.returncode == 0, f"Import sorting failed: {result.stdout}"
```

### 2. Docker Build Testi
```python
# tests/test_docker.py
import docker

def test_docker_build():
    client = docker.from_env()
    
    # Docker imajını oluştur
    image, logs = client.images.build(
        path=".",
        tag="finasis:test",
        rm=True
    )
    
    assert image is not None, "Docker build failed"
    
    # Test container'ı başlat
    container = client.containers.run(
        "finasis:test",
        detach=True,
        remove=True
    )
    
    # Sağlık kontrolü
    response = container.exec_run("curl -f http://localhost:8000/health/")
    assert response.exit_code == 0, "Health check failed"
```

## 📝 Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. CI Pipeline Hataları
**Sorun**: Pipeline başarısız oluyor
**Çözüm**:
- Test hatalarını kontrol edin
- Linting sorunlarını düzeltin
- Bağımlılıkları güncelleyin

### 2. Docker Build Hataları
**Sorun**: Docker imajı oluşturulamıyor
**Çözüm**:
- Dockerfile'ı kontrol edin
- Disk alanını temizleyin
- Önbelleği temizleyin

### 3. Kubernetes Dağıtım Hataları
**Sorun**: Pod'lar başlatılamıyor
**Çözüm**:
- Kaynak limitlerini kontrol edin
- Secret'ları doğrulayın
- Log'ları inceleyin

## 📂 Dosya Yapısı ve Referanslar

```
finasis/
├── .github/
│   └── workflows/
│       ├── main.yml
│       └── security.yml
├── k8s/
│   ├── deployment.yml
│   └── service.yml
├── Dockerfile
├── Dockerfile.dev
└── docker-compose.dev.yml
```

## 🔍 Ek Kaynaklar

- [GitHub Actions Dokümantasyonu](https://docs.github.com/en/actions)
- [Docker Dokümantasyonu](https://docs.docker.com/)
- [Kubernetes Dokümantasyonu](https://kubernetes.io/docs/)
- [AWS ECS Dokümantasyonu](https://docs.aws.amazon.com/ecs/) 