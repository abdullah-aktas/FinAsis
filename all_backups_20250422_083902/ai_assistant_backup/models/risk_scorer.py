import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import joblib

class CustomerRiskScorer:
    def __init__(self, model_type='logistic'):
        """
        Müşteri risk skorlama modeli
        
        Args:
            model_type (str): Kullanılacak model tipi ('logistic', 'tree')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, data):
        """
        Özellikleri hazırlar
        
        Args:
            data (dict): Müşteri verileri
        """
        features = {
            'payment_delay_avg': data.get('payment_delay_avg', 0),
            'payment_delay_count': data.get('payment_delay_count', 0),
            'transaction_amount_avg': data.get('transaction_amount_avg', 0),
            'transaction_count': data.get('transaction_count', 0),
            'days_since_last_payment': data.get('days_since_last_payment', 0),
            'sector_risk_score': data.get('sector_risk_score', 0)
        }
        return pd.DataFrame([features])
        
    def train(self, training_data):
        """
        Modeli eğitir
        
        Args:
            training_data (pd.DataFrame): Eğitim verisi
        """
        X = training_data.drop('risk_label', axis=1)
        y = training_data['risk_label']
        
        # Veriyi ölçeklendir
        X_scaled = self.scaler.fit_transform(X)
        
        # Model seçimi ve eğitimi
        if self.model_type == 'logistic':
            self.model = LogisticRegression(max_iter=1000)
        else:
            self.model = DecisionTreeClassifier(max_depth=5)
            
        self.model.fit(X_scaled, y)
        
    def predict_risk_score(self, customer_data):
        """
        Müşteri için risk skoru tahmin eder
        
        Args:
            customer_data (dict): Müşteri verileri
            
        Returns:
            dict: Risk skoru ve açıklaması
        """
        features = self.prepare_features(customer_data)
        features_scaled = self.scaler.transform(features)
        
        # Risk olasılığını tahmin et
        risk_prob = self.model.predict_proba(features_scaled)[0][1]
        
        # 0-100 arası skora dönüştür
        risk_score = int(risk_prob * 100)
        
        # Risk seviyesini belirle
        if risk_score >= 80:
            risk_level = 'Yüksek'
            color = 'red'
        elif risk_score >= 60:
            risk_level = 'Orta'
            color = 'orange'
        else:
            risk_level = 'Düşük'
            color = 'green'
            
        # Risk açıklaması oluştur
        explanation = self._generate_explanation(customer_data, risk_score)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'color': color,
            'explanation': explanation
        }
        
    def _generate_explanation(self, customer_data, risk_score):
        """
        Risk skoru için açıklama oluşturur
        
        Args:
            customer_data (dict): Müşteri verileri
            risk_score (int): Risk skoru
            
        Returns:
            str: Risk açıklaması
        """
        explanations = []
        
        if customer_data.get('payment_delay_count', 0) > 0:
            explanations.append(f"Son dönemde {customer_data['payment_delay_count']} kez ödeme gecikmesi yaşandı")
            
        if customer_data.get('payment_delay_avg', 0) > 15:
            explanations.append(f"Ortalama ödeme gecikmesi {customer_data['payment_delay_avg']:.1f} gün")
            
        if customer_data.get('transaction_amount_avg', 0) < 1000:
            explanations.append("İşlem hacmi düşük")
            
        if customer_data.get('days_since_last_payment', 0) > 30:
            explanations.append(f"Son ödemeden bu yana {customer_data['days_since_last_payment']} gün geçti")
            
        if not explanations:
            explanations.append("Risk faktörü tespit edilmedi")
            
        return ". ".join(explanations)
        
    def save_model(self, path):
        """
        Modeli kaydeder
        
        Args:
            path (str): Kayıt yolu
        """
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type
        }
        joblib.dump(model_data, path)
        
    def load_model(self, path):
        """
        Modeli yükler
        
        Args:
            path (str): Model dosyası yolu
        """
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type'] 