import pandas as pd
import numpy as np
from django.core.cache import cache
from django.conf import settings
import logging
from datetime import datetime, timedelta
import json
from .models import DashboardWidget, AnalyticsReport, DataSource

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Analitik servisleri sınıfı"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 saat
        self.max_data_points = 1000
        
    def get_widget_data(self, widget):
        """Widget verilerini getir"""
        cache_key = f"widget_data_{widget.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        try:
            data = self._fetch_widget_data(widget)
            cache.set(cache_key, data, self.cache_timeout)
            return data
        except Exception as e:
            logger.error(f"Widget verisi alınamadı: {str(e)}")
            raise
            
    def get_report_data(self, report):
        """Rapor verilerini getir"""
        cache_key = f"report_data_{report.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        try:
            data = self._execute_report_query(report)
            cache.set(cache_key, data, self.cache_timeout)
            return data
        except Exception as e:
            logger.error(f"Rapor verisi alınamadı: {str(e)}")
            raise
            
    def sync_data_source(self, source):
        """Veri kaynağını senkronize et"""
        try:
            if source.source_type == 'database':
                self._sync_database(source)
            elif source.source_type == 'api':
                self._sync_api(source)
            elif source.source_type == 'file':
                self._sync_file(source)
            elif source.source_type == 'stream':
                self._sync_stream(source)
                
            source.last_sync = datetime.now()
            source.save()
            
        except Exception as e:
            logger.error(f"Veri kaynağı senkronize edilemedi: {str(e)}")
            raise
            
    def _fetch_widget_data(self, widget):
        """Widget verilerini getir"""
        # Veri kaynağından veri çek
        raw_data = self._get_data_from_source(widget.data_source)
        
        # Widget tipine göre veriyi işle
        if widget.widget_type == 'line_chart':
            return self._process_line_chart_data(raw_data, widget.settings)
        elif widget.widget_type == 'bar_chart':
            return self._process_bar_chart_data(raw_data, widget.settings)
        elif widget.widget_type == 'pie_chart':
            return self._process_pie_chart_data(raw_data, widget.settings)
        elif widget.widget_type == 'table':
            return self._process_table_data(raw_data, widget.settings)
        elif widget.widget_type == 'metric':
            return self._process_metric_data(raw_data, widget.settings)
        elif widget.widget_type == 'gauge':
            return self._process_gauge_data(raw_data, widget.settings)
            
    def _process_line_chart_data(self, data, settings):
        """Çizgi grafik verilerini işle"""
        df = pd.DataFrame(data)
        
        # Zaman serisi verisi için
        if 'date_column' in settings:
            df[settings['date_column']] = pd.to_datetime(df[settings['date_column']])
            df = df.sort_values(settings['date_column'])
            
            labels = df[settings['date_column']].dt.strftime('%b %Y').tolist()
            datasets = []
            
            for column in settings['value_columns']:
                datasets.append({
                    'label': column,
                    'data': df[column].tolist(),
                    'color': settings.get('colors', {}).get(column, '#2193B0')
                })
                
            return {
                'labels': labels,
                'datasets': datasets
            }
            
        return {
            'labels': df[settings['label_column']].tolist(),
            'datasets': [{
                'label': settings.get('title', 'Veri'),
                'data': df[settings['value_column']].tolist(),
                'color': settings.get('color', '#2193B0')
            }]
        }
        
    def _process_bar_chart_data(self, data, settings):
        """Sütun grafik verilerini işle"""
        df = pd.DataFrame(data)
        
        return {
            'labels': df[settings['label_column']].tolist(),
            'datasets': [{
                'label': settings.get('title', 'Veri'),
                'data': df[settings['value_column']].tolist(),
                'color': settings.get('color', '#2193B0')
            }]
        }
        
    def _process_pie_chart_data(self, data, settings):
        """Pasta grafik verilerini işle"""
        df = pd.DataFrame(data)
        
        return {
            'labels': df[settings['label_column']].tolist(),
            'data': df[settings['value_column']].tolist(),
            'colors': settings.get('colors', [
                '#2193B0', '#6DD5ED', '#FF6B6B', '#4ECDC4',
                '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5'
            ])
        }
        
    def _process_table_data(self, data, settings):
        """Tablo verilerini işle"""
        df = pd.DataFrame(data)
        
        return {
            'headers': settings['columns'],
            'rows': df[settings['columns']].values.tolist()
        }
        
    def _process_metric_data(self, data, settings):
        """Metrik verilerini işle"""
        df = pd.DataFrame(data)
        
        current_value = df[settings['value_column']].iloc[-1]
        previous_value = df[settings['value_column']].iloc[-2]
        
        trend = ((current_value - previous_value) / previous_value) * 100 if previous_value != 0 else 0
        
        return {
            'value': f"{settings.get('prefix', '')}{current_value:,.2f}{settings.get('suffix', '')}",
            'label': settings.get('title', 'Metrik'),
            'trend': round(trend, 1)
        }
        
    def _process_gauge_data(self, data, settings):
        """Gösterge verilerini işle"""
        df = pd.DataFrame(data)
        
        value = df[settings['value_column']].iloc[-1]
        min_value = settings.get('min_value', 0)
        max_value = settings.get('max_value', 100)
        
        return {
            'value': value,
            'min': min_value,
            'max': max_value,
            'zones': settings.get('zones', [
                {'strokeStyle': "#F03E3E", 'min': 0, 'max': 20},
                {'strokeStyle': "#FFDD00", 'min': 20, 'max': 60},
                {'strokeStyle': "#30B32D", 'min': 60, 'max': 100}
            ])
        }
        
    def _execute_report_query(self, report):
        """Rapor sorgusunu çalıştır"""
        # Sorguyu çalıştır
        data = self._execute_query(report.query, report.parameters)
        
        # Veriyi işle
        processed_data = self._process_report_data(data, report.report_type)
        
        return processed_data
        
    def _get_data_from_source(self, source_id):
        """Veri kaynağından veri getir"""
        source = DataSource.objects.get(id=source_id)
        
        if source.source_type == 'database':
            return self._get_database_data(source)
        elif source.source_type == 'api':
            return self._get_api_data(source)
        elif source.source_type == 'file':
            return self._get_file_data(source)
        elif source.source_type == 'stream':
            return self._get_stream_data(source)
            
    def _process_widget_data(self, data, settings):
        """Widget verilerini işle"""
        # Veriyi pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)
        
        # Ayarlara göre veriyi işle
        if 'aggregation' in settings:
            df = self._aggregate_data(df, settings['aggregation'])
            
        if 'filter' in settings:
            df = self._filter_data(df, settings['filter'])
            
        if 'sort' in settings:
            df = self._sort_data(df, settings['sort'])
            
        # Veriyi JSON formatına dönüştür
        return df.to_dict('records')
        
    def _process_report_data(self, data, report_type):
        """Rapor verilerini işle"""
        # Veriyi pandas DataFrame'e dönüştür
        df = pd.DataFrame(data)
        
        # Rapor tipine göre veriyi işle
        if report_type == 'financial':
            df = self._process_financial_data(df)
        elif report_type == 'operational':
            df = self._process_operational_data(df)
        elif report_type == 'customer':
            df = self._process_customer_data(df)
        elif report_type == 'performance':
            df = self._process_performance_data(df)
            
        # Veriyi JSON formatına dönüştür
        return df.to_dict('records')
        
    def _aggregate_data(self, df, aggregation):
        """Veriyi topla"""
        return df.groupby(aggregation['by']).agg(aggregation['metrics']).reset_index()
        
    def _filter_data(self, df, filter_conditions):
        """Veriyi filtrele"""
        return df.query(filter_conditions)
        
    def _sort_data(self, df, sort_conditions):
        """Veriyi sırala"""
        return df.sort_values(**sort_conditions)
        
    def _process_financial_data(self, df):
        """Finansal verileri işle"""
        # Finansal metrikleri hesapla
        df['profit_margin'] = df['profit'] / df['revenue']
        df['roi'] = df['profit'] / df['investment']
        
        return df
        
    def _process_operational_data(self, df):
        """Operasyonel verileri işle"""
        # Operasyonel metrikleri hesapla
        df['efficiency'] = df['output'] / df['input']
        df['utilization'] = df['used'] / df['total']
        
        return df
        
    def _process_customer_data(self, df):
        """Müşteri verilerini işle"""
        # Müşteri metriklerini hesapla
        df['churn_rate'] = df['lost_customers'] / df['total_customers']
        df['lifetime_value'] = df['total_revenue'] / df['total_customers']
        
        return df
        
    def _process_performance_data(self, df):
        """Performans verilerini işle"""
        # Performans metriklerini hesapla
        df['response_time'] = df['total_time'] / df['requests']
        df['error_rate'] = df['errors'] / df['total']
        
        return df 