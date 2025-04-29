# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.conf import settings
from ..base import BaseAPIIntegration
from ..services import IntegrationService, APIService

class ExternalService(APIService):
    """Harici servis entegrasyonu servisi"""
    
    def __init__(self):
        config = IntegrationService.get_integration_config('external_services')
        super().__init__(
            base_url=config.get('base_url'),
            headers={
                'Authorization': f"Bearer {config.get('api_key')}",
                'Content-Type': 'application/json'
            }
        )
    
    def get_weather_data(
        self,
        city: str,
        country: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Hava durumu verilerini al"""
        endpoint = "/weather"
        params = {
            'city': city,
            'country': country
        }
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(endpoint, params=params)
    
    def get_currency_rates(
        self,
        base_currency: str,
        target_currencies: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Döviz kurlarını al"""
        endpoint = "/currency/rates"
        params = {
            'base_currency': base_currency,
            'target_currencies': ','.join(target_currencies)
        }
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(endpoint, params=params)
    
    def get_stock_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = '1d'
    ) -> Dict[str, Any]:
        """Hisse senedi verilerini al"""
        endpoint = "/stocks"
        params = {
            'symbol': symbol,
            'interval': interval
        }
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(endpoint, params=params)
    
    def get_news(
        self,
        query: str,
        language: str = 'tr',
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Haberleri al"""
        endpoint = "/news"
        params = {
            'query': query,
            'language': language,
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_translation(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Metin çevirisi yap"""
        endpoint = "/translate"
        data = {
            'text': text,
            'source_language': source_language,
            'target_language': target_language
        }
        return self.post(endpoint, json=data)
    
    def get_geolocation(
        self,
        address: str,
        country: Optional[str] = None
    ) -> Dict[str, Any]:
        """Adres konumunu al"""
        endpoint = "/geolocation"
        params = {'address': address}
        if country:
            params['country'] = country
        return self.get(endpoint, params=params)
    
    def get_distance(
        self,
        origin: str,
        destination: str,
        mode: str = 'driving'
    ) -> Dict[str, Any]:
        """İki nokta arası mesafeyi al"""
        endpoint = "/distance"
        params = {
            'origin': origin,
            'destination': destination,
            'mode': mode
        }
        return self.get(endpoint, params=params)
    
    def get_timezone(
        self,
        latitude: float,
        longitude: float,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Saat dilimini al"""
        endpoint = "/timezone"
        params = {
            'latitude': latitude,
            'longitude': longitude
        }
        if timestamp:
            params['timestamp'] = timestamp.isoformat()
        return self.get(endpoint, params=params)
    
    def get_holidays(
        self,
        country: str,
        year: int,
        language: str = 'tr'
    ) -> Dict[str, Any]:
        """Tatil günlerini al"""
        endpoint = "/holidays"
        params = {
            'country': country,
            'year': year,
            'language': language
        }
        return self.get(endpoint, params=params)
    
    def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Hava kalitesi verilerini al"""
        endpoint = "/air-quality"
        params = {
            'latitude': latitude,
            'longitude': longitude
        }
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(endpoint, params=params)
    
    def get_traffic_data(
        self,
        city: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Trafik verilerini al"""
        endpoint = "/traffic"
        params = {'city': city}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        return self.get(endpoint, params=params)
    
    def get_public_transport(
        self,
        city: str,
        start_location: str,
        end_location: str,
        departure_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Toplu taşıma bilgilerini al"""
        endpoint = "/public-transport"
        params = {
            'city': city,
            'start_location': start_location,
            'end_location': end_location
        }
        if departure_time:
            params['departure_time'] = departure_time.isoformat()
        return self.get(endpoint, params=params)
    
    def get_restaurant_info(
        self,
        location: str,
        cuisine: Optional[str] = None,
        price_range: Optional[str] = None,
        rating: Optional[float] = None
    ) -> Dict[str, Any]:
        """Restoran bilgilerini al"""
        endpoint = "/restaurants"
        params = {'location': location}
        if cuisine:
            params['cuisine'] = cuisine
        if price_range:
            params['price_range'] = price_range
        if rating:
            params['rating'] = rating
        return self.get(endpoint, params=params)
    
    def get_hotel_info(
        self,
        location: str,
        check_in: datetime,
        check_out: datetime,
        guests: int = 1,
        price_range: Optional[str] = None,
        rating: Optional[float] = None
    ) -> Dict[str, Any]:
        """Otel bilgilerini al"""
        endpoint = "/hotels"
        params = {
            'location': location,
            'check_in': check_in.isoformat(),
            'check_out': check_out.isoformat(),
            'guests': guests
        }
        if price_range:
            params['price_range'] = price_range
        if rating:
            params['rating'] = rating
        return self.get(endpoint, params=params)
    
    def get_event_info(
        self,
        location: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Etkinlik bilgilerini al"""
        endpoint = "/events"
        params = {'location': location}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()
        if category:
            params['category'] = category
        return self.get(endpoint, params=params)
    
    def get_movie_info(
        self,
        title: str,
        year: Optional[int] = None,
        language: str = 'tr'
    ) -> Dict[str, Any]:
        """Film bilgilerini al"""
        endpoint = "/movies"
        params = {
            'title': title,
            'language': language
        }
        if year:
            params['year'] = year
        return self.get(endpoint, params=params)
    
    def get_music_info(
        self,
        query: str,
        type: str = 'track',
        limit: int = 20
    ) -> Dict[str, Any]:
        """Müzik bilgilerini al"""
        endpoint = "/music"
        params = {
            'query': query,
            'type': type,
            'limit': limit
        }
        return self.get(endpoint, params=params)
    
    def get_book_info(
        self,
        query: str,
        author: Optional[str] = None,
        language: str = 'tr'
    ) -> Dict[str, Any]:
        """Kitap bilgilerini al"""
        endpoint = "/books"
        params = {
            'query': query,
            'language': language
        }
        if author:
            params['author'] = author
        return self.get(endpoint, params=params)
    
    def get_system_settings(self) -> Dict[str, Any]:
        """Sistem ayarlarını al"""
        endpoint = "/settings"
        return self.get(endpoint)
    
    def update_system_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sistem ayarlarını güncelle"""
        endpoint = "/settings"
        return self.put(endpoint, json=data)
    
    def get_audit_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Denetim loglarını al"""
        endpoint = "/audit-logs"
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'page': page,
            'per_page': per_page
        }
        return self.get(endpoint, params=params)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Sistem durumunu kontrol et"""
        endpoint = "/status"
        return self.get(endpoint)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Entegrasyon durumunu kontrol et"""
        endpoint = "/integration/status"
        return self.get(endpoint)
    
    def sync_data(self, data_type: str) -> Dict[str, Any]:
        """Veri senkronizasyonu başlat"""
        endpoint = "/sync"
        data = {'data_type': data_type}
        return self.post(endpoint, json=data)
    
    def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """Senkronizasyon durumunu kontrol et"""
        endpoint = f"/sync/{sync_id}/status"
        return self.get(endpoint) 