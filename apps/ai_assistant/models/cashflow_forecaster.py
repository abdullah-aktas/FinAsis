import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta

class CashFlowForecaster:
    def __init__(self, model_type='prophet'):
        """
        Nakit akışı tahminleme modeli
        
        Args:
            model_type (str): Kullanılacak model tipi ('prophet', 'lstm', 'arima')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler()
        
    def prepare_data(self, data):
        """
        Veriyi model için hazırlar
        
        Args:
            data (pd.DataFrame): Tarih, gelir ve gider verilerini içeren DataFrame
        """
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['net_cash'] = df['cash_in'] - df['cash_out']
        return df
        
    def train(self, data):
        """
        Modeli eğitir
        
        Args:
            data (pd.DataFrame): Eğitim verisi
        """
        df = self.prepare_data(data)
        
        if self.model_type == 'prophet':
            prophet_df = df[['date', 'net_cash']].rename(columns={'date': 'ds', 'net_cash': 'y'})
            self.model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
            self.model.fit(prophet_df)
            
        elif self.model_type == 'lstm':
            # Veriyi normalize et
            scaled_data = self.scaler.fit_transform(df[['net_cash']])
            
            # LSTM için veri hazırlama
            X, y = [], []
            for i in range(30, len(scaled_data)):
                X.append(scaled_data[i-30:i, 0])
                y.append(scaled_data[i, 0])
            X, y = np.array(X), np.array(y)
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            
            # LSTM modeli oluştur
            self.model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(30, 1)),
                LSTM(50, return_sequences=False),
                Dense(25),
                Dense(1)
            ])
            self.model.compile(optimizer='adam', loss='mean_squared_error')
            self.model.fit(X, y, batch_size=32, epochs=100, verbose=0)
            
    def forecast(self, periods=90):
        """
        Gelecek dönemler için tahmin yapar
        
        Args:
            periods (int): Tahmin edilecek gün sayısı
            
        Returns:
            dict: Tahmin sonuçları
        """
        if self.model_type == 'prophet':
            future = self.model.make_future_dataframe(periods=periods)
            forecast = self.model.predict(future)
            
            # Sonuçları JSON formatına dönüştür
            results = {
                'dates': forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                'predictions': forecast['yhat'].round(2).tolist(),
                'lower_bound': forecast['yhat_lower'].round(2).tolist(),
                'upper_bound': forecast['yhat_upper'].round(2).tolist()
            }
            
        elif self.model_type == 'lstm':
            # Son 30 günlük veriyi kullanarak tahmin yap
            last_30_days = self.scaler.transform(self.last_data[['net_cash']])
            X = np.array([last_30_days])
            X = np.reshape(X, (X.shape[0], X.shape[1], 1))
            
            predictions = []
            for _ in range(periods):
                pred = self.model.predict(X)
                predictions.append(pred[0, 0])
                X = np.roll(X, -1)
                X[0, -1, 0] = pred[0, 0]
            
            # Tahminleri orijinal ölçeğe geri dönüştür
            predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
            
            # Tarihleri oluştur
            last_date = self.last_data['date'].iloc[-1]
            dates = [last_date + timedelta(days=x+1) for x in range(periods)]
            
            results = {
                'dates': [d.strftime('%Y-%m-%d') for d in dates],
                'predictions': predictions.flatten().round(2).tolist()
            }
            
        return results
    
    def plot_forecast(self, results):
        """
        Tahmin sonuçlarını görselleştirir
        
        Args:
            results (dict): Tahmin sonuçları
            
        Returns:
            plotly.graph_objects.Figure: Grafik
        """
        fig = go.Figure()
        
        # Tahmin çizgisi
        fig.add_trace(go.Scatter(
            x=results['dates'],
            y=results['predictions'],
            name='Tahmin',
            line=dict(color='blue')
        ))
        
        # Güven aralığı (Prophet için)
        if 'lower_bound' in results and 'upper_bound' in results:
            fig.add_trace(go.Scatter(
                x=results['dates'] + results['dates'][::-1],
                y=results['upper_bound'] + results['lower_bound'][::-1],
                fill='toself',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Güven Aralığı'
            ))
        
        fig.update_layout(
            title='Nakit Akışı Tahmini',
            xaxis_title='Tarih',
            yaxis_title='Net Nakit Akışı',
            template='plotly_white'
        )
        
        return fig 