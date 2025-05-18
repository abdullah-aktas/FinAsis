# FinAsis API Dokümantasyonu v1.0.0

## 🔐 Kimlik Doğrulama
```bash
curl -X POST https://api.finasis.com/v1/auth
  -H "Content-Type: application/json"
  -d '{
    "api_key": "your_api_key"
  }'
```

## 📊 Endpoints

### Kullanıcı İşlemleri
```typescript
POST /api/v1/users
GET /api/v1/users/{id}
PUT /api/v1/users/{id}
DELETE /api/v1/users/{id}
```

### Finansal İşlemler
```typescript
POST /api/v1/transactions
GET /api/v1/portfolio/{userId}
GET /api/v1/market/realtime
POST /api/v1/trade/execute
```

### Simülasyon API
```typescript
POST /api/v1/simulation/start
GET /api/v1/simulation/state/{sessionId}
PUT /api/v1/simulation/configure
```

## 🔄 WebSocket API
```typescript
ws://api.finasis.com/v1/ws/market
ws://api.finasis.com/v1/ws/portfolio
```

## 📈 Rate Limits
| Plan     | Requests/min | Websocket Connections |
|----------|-------------|---------------------|
| Free     | 60          | 1                   |
| Pro      | 1000        | 10                  |
| Enterprise| Unlimited   | Unlimited           |
