# 3. AI Assistant Modülü

## 📌 Amaç
Bu dokümantasyon, FinAsis projesinin yapay zeka destekli özelliklerini, nakit akışı tahmini, müşteri risk skorlaması ve OCR sistemlerinin kullanımını detaylandırmaktadır.

## ⚙️ Teknik Yapı

### 1. Nakit Akışı Tahmini

#### 1.1. Prophet Modeli
```python
from prophet import Prophet
import pandas as pd

def train_cash_flow_model(historical_data):
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=True,
        changepoint_prior_scale=0.05
    )
    
    model.fit(historical_data)
    return model

def predict_cash_flow(model, future_dates):
    forecast = model.predict(future_dates)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
```

#### 1.2. ARIMA Modeli
```python
from statsmodels.tsa.arima.model import ARIMA

def train_arima_model(data, order=(1,1,1)):
    model = ARIMA(data, order=order)
    results = model.fit()
    return results

def predict_arima(model, steps=30):
    forecast = model.forecast(steps=steps)
    return forecast
```

### 2. Müşteri Risk Skorlaması

#### 2.1. LogisticRegression Modeli
```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def train_risk_model(customer_data):
    X = customer_data[['payment_history', 'credit_score', 'transaction_volume']]
    y = customer_data['risk_label']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression()
    model.fit(X_scaled, y)
    return model, scaler

def predict_risk_score(model, scaler, customer_features):
    X_scaled = scaler.transform(customer_features)
    risk_score = model.predict_proba(X_scaled)[:, 1]
    return risk_score
```

### 3. OCR Sistemi

#### 3.1. Tesseract Entegrasyonu
```python
import pytesseract
from PIL import Image

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='tur')
    return text
```

#### 3.2. Google Vision API Entegrasyonu
```python
from google.cloud import vision

def extract_text_google_vision(image_path):
    client = vision.ImageAnnotatorClient()
    
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    return texts[0].description if texts else ''
```

## 🔧 Kullanım Adımları

### 1. Nakit Akışı Tahmini

#### 1.1. Veri Hazırlama
```python
# Geçmiş nakit akışı verilerini yükleme
historical_data = pd.DataFrame({
    'ds': dates,
    'y': cash_flows
})

# Model eğitimi
model = train_cash_flow_model(historical_data)

# Tahmin
future_dates = model.make_future_dataframe(periods=30)
forecast = predict_cash_flow(model, future_dates)
```

### 2. Risk Skorlaması

#### 2.1. Müşteri Verilerini İşleme
```python
# Müşteri özelliklerini hazırlama
customer_features = pd.DataFrame({
    'payment_history': payment_scores,
    'credit_score': credit_scores,
    'transaction_volume': transaction_volumes
})

# Model eğitimi ve tahmin
model, scaler = train_risk_model(training_data)
risk_scores = predict_risk_score(model, scaler, customer_features)
```

### 3. OCR İşlemi

#### 3.1. Fatura ve Belge İşleme
```python
# Tesseract ile metin çıkarma
text = extract_text_from_image('fatura.jpg')

# Google Vision ile metin çıkarma
text = extract_text_google_vision('fatura.jpg')
```

## 🧪 Test Örnekleri

### 1. Nakit Akışı Modeli Testi
```python
def test_cash_flow_prediction():
    # Test verisi oluşturma
    test_data = pd.DataFrame({
        'ds': pd.date_range(start='2023-01-01', periods=100),
        'y': np.random.normal(1000, 100, 100)
    })
    
    # Model eğitimi ve tahmin
    model = train_cash_flow_model(test_data)
    forecast = predict_cash_flow(model, test_data)
    
    assert len(forecast) > 0
    assert 'yhat' in forecast.columns
```

### 2. Risk Skorlama Testi
```python
def test_risk_scoring():
    # Test verisi oluşturma
    test_features = pd.DataFrame({
        'payment_history': [0.8, 0.6, 0.9],
        'credit_score': [700, 650, 750],
        'transaction_volume': [10000, 5000, 15000]
    })
    
    # Model eğitimi ve tahmin
    model, scaler = train_risk_model(training_data)
    scores = predict_risk_score(model, scaler, test_features)
    
    assert len(scores) == len(test_features)
    assert all(0 <= score <= 1 for score in scores)
```

## 📝 Sık Karşılaşılan Sorunlar ve Çözümleri

### 1. Prophet Model Hataları
**Sorun**: Model eğitimi sırasında bellek hatası
**Çözüm**:
- Veri setini küçültün
- Changepoint sayısını azaltın
- Daha az mevsimsellik parametresi kullanın

### 2. OCR Doğruluk Sorunları
**Sorun**: Düşük metin tanıma doğruluğu
**Çözüm**:
- Görüntü ön işleme uygulayın
- Tesseract dil paketlerini güncelleyin
- Google Vision API'ye geçiş yapın

### 3. Risk Skorlama Performansı
**Sorun**: Yüksek yanlış pozitif oranı
**Çözüm**:
- Özellik mühendisliği yapın
- Model hiperparametrelerini optimize edin
- Daha fazla eğitim verisi ekleyin

## 📂 Dosya Yapısı ve Referanslar

```
finasis/
├── apps/
│   └── ai_assistant/
│       ├── models/
│       │   ├── cash_flow.py
│       │   ├── risk_scoring.py
│       │   └── ocr.py
│       ├── utils/
│       │   ├── data_preprocessing.py
│       │   └── model_evaluation.py
│       └── tests/
│           ├── test_cash_flow.py
│           ├── test_risk_scoring.py
│           └── test_ocr.py
└── data/
    ├── models/
    │   ├── cash_flow_model.pkl
    │   └── risk_model.pkl
    └── training/
        ├── cash_flow_data.csv
        └── customer_data.csv
```

## 🔍 Ek Kaynaklar

- [Prophet Dokümantasyonu](https://facebook.github.io/prophet/)
- [Scikit-learn Dokümantasyonu](https://scikit-learn.org/)
- [Tesseract OCR Dokümantasyonu](https://github.com/tesseract-ocr/tesseract)
- [Google Vision API Dokümantasyonu](https://cloud.google.com/vision/docs) 