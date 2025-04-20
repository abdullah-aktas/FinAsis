# FinAsis Monitoring & Alerting Kılavuzu

## 📊 Monitoring Sistemi

### 1. Prometheus Kurulumu
```bash
# Docker Compose ile kurulum
docker-compose -f docker-compose.prod.yml up -d prometheus

# Hedefleri kontrol et
curl -f http://localhost:9090/api/v1/targets
```

#### 1.1 Metrikler
- **Sistem Metrikleri**
  - CPU kullanımı
  - Memory kullanımı
  - Disk I/O
  - Network I/O

- **Uygulama Metrikleri**
  - Request sayısı
  - Response time
  - Error rate
  - Active users

- **Veritabanı Metrikleri**
  - Bağlantı sayısı
  - Query performansı
  - Transaction sayısı
  - Lock durumu

### 2. Grafana Kurulumu
```bash
# Docker Compose ile kurulum
docker-compose -f docker-compose.prod.yml up -d grafana

# Tarayıcıdan erişim
# http://grafana.finasis.com.tr
```

#### 2.1 Dashboardlar
- **Sistem Dashboard**
  - Sunucu durumu
  - Resource kullanımı
  - Network trafiği

- **Uygulama Dashboard**
  - API performansı
  - Error oranları
  - User sessions
  - Business metrics

- **Veritabanı Dashboard**
  - Query performansı
  - Connection pool
  - Cache hit ratio
  - Slow queries

### 3. Alerting Kuralları

#### 3.1 Sistem Alertleri
```yaml
# High CPU Usage
- alert: HighCPUUsage
  expr: avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) > 0.8
  for: 5m
  labels:
    severity: warning
  annotations:
    description: "CPU usage is above 80%"

# High Memory Usage
- alert: HighMemoryUsage
  expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
  for: 5m
  labels:
    severity: warning
  annotations:
    description: "Memory usage is above 90%"

# Disk Space
- alert: LowDiskSpace
  expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} < 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    description: "Less than 10% disk space left"
```

#### 3.2 Uygulama Alertleri
```yaml
# High Error Rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    description: "Error rate is above 5%"

# High Response Time
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
  for: 5m
  labels:
    severity: warning
  annotations:
    description: "95th percentile response time is above 2s"
```

#### 3.3 Veritabanı Alertleri
```yaml
# Connection Pool
- alert: HighDBConnections
  expr: pg_stat_activity_count > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    description: "Database has more than 100 active connections"

# Slow Queries
- alert: SlowQueries
  expr: rate(pg_stat_activity_max_tx_duration{datname="finasis"}[5m]) > 30
  for: 5m
  labels:
    severity: warning
  annotations:
    description: "Queries taking longer than 30 seconds"
```

### 4. Bildirim Kanalları

#### 4.1 Slack Entegrasyonu
```yaml
receivers:
- name: 'slack'
  slack_configs:
  - channel: '#finasis-alerts'
    send_resolved: true
    icon_url: https://avatars3.githubusercontent.com/u/3380462
    title: '{{ .GroupLabels.alertname }}'
    text: "{{ range .Alerts }}{{ .Annotations.description }}\n{{ end }}"
```

#### 4.2 Email Bildirimleri
```yaml
receivers:
- name: 'email'
  email_configs:
  - to: 'devops@finasis.com.tr'
    from: 'alertmanager@finasis.com.tr'
    smarthost: 'smtp.gmail.com:587'
    auth_username: '{{ .EmailUser }}'
    auth_password: '{{ .EmailPassword }}'
```

### 5. Escalation Politikası

#### 5.1 Severity Seviyeleri
- **INFO:** Bilgilendirme amaçlı, acil aksiyon gerektirmez
- **WARNING:** 4 saat içinde incelenmeli
- **CRITICAL:** 30 dakika içinde müdahale edilmeli
- **EMERGENCY:** Anında müdahale gerektirir

#### 5.2 On-Call Rotasyonu
```yaml
route:
  receiver: 'slack'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'
    continue: true
  - match:
      severity: emergency
    receiver: 'phone'
    continue: true
```

### 6. Troubleshooting

#### 6.1 Prometheus
```bash
# Prometheus status
curl -f http://localhost:9090/-/healthy

# Config reload
curl -X POST http://localhost:9090/-/reload

# Query API
curl -G --data-urlencode 'query=up' http://localhost:9090/api/v1/query
```

#### 6.2 Grafana
```bash
# Grafana health
curl -f http://localhost:3000/api/health

# Backup dashboards
curl -H "Authorization: Bearer $API_KEY" http://localhost:3000/api/dashboards/uid/$UID

# Reset admin password
docker-compose exec grafana grafana-cli admin reset-admin-password newpass
```

#### 6.3 AlertManager
```bash
# AlertManager status
curl -f http://localhost:9093/-/healthy

# Silence alert
curl -X POST http://localhost:9093/api/v1/silences \
  -d '{"matchers":[{"name":"alertname","value":"HighCPUUsage"}],"startsAt":"2023-01-01T00:00:00Z","endsAt":"2023-01-02T00:00:00Z","createdBy":"admin","comment":"Maintenance"}'
```

## 📱 Mobile App Monitoring

### 1. Crash Reporting
- Firebase Crashlytics entegrasyonu
- Error tracking
- User impact analysis

### 2. Performance Monitoring
- App start time
- Screen render time
- Network request latency

### 3. Usage Analytics
- Daily active users
- Session duration
- Feature usage
- Conversion rates

## 🎮 Game Module Monitoring

### 1. Performance Metrics
- FPS (Frames Per Second)
- Loading times
- Memory usage
- GPU utilization

### 2. User Metrics
- Active players
- Session length
- Completion rates
- Score distribution

## 📈 Business Metrics

### 1. KPI Dashboard
- Daily active users
- Monthly recurring revenue
- Customer acquisition cost
- Customer lifetime value
- Churn rate

### 2. E-Fatura Metrics
- Başarılı fatura sayısı
- Hata oranı
- İşlem süresi
- Entegrasyon durumu 