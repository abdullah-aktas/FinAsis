from django.http import JsonResponse
from django.conf import settings
import requests
import yfinance as yf
from datetime import datetime
import json

def get_weather_data(request):
    """Kullanıcının IP adresine göre hava durumu bilgisini döndürür"""
    try:
        # IP adresinden şehir bilgisini al
        ip_response = requests.get('https://ipapi.co/json/')
        city = ip_response.json().get('city', 'Istanbul')
        
        # OpenWeatherMap API'den hava durumu bilgisini al
        weather_response = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather',
            params={
                'q': city,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'tr'
            }
        )
        weather_data = weather_response.json()
        
        return JsonResponse({
            'city': city,
            'temperature': round(weather_data['main']['temp']),
            'condition': weather_data['weather'][0]['description'].capitalize()
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def get_finance_data(request):
    """Güncel finans bilgilerini döndürür"""
    try:
        # BIST100 verisi
        bist100 = yf.Ticker("XU100.IS")
        bist100_data = bist100.history(period='1d')
        bist100_value = round(bist100_data['Close'].iloc[-1], 2)
        
        # Döviz kurları
        usd_try = yf.Ticker("USDTRY=X")
        eur_try = yf.Ticker("EURTRY=X")
        
        usd_data = usd_try.history(period='1d')
        eur_data = eur_try.history(period='1d')
        
        usd_value = round(usd_data['Close'].iloc[-1], 2)
        eur_value = round(eur_data['Close'].iloc[-1], 2)
        
        # Altın fiyatı (XAU/TRY)
        gold_try = yf.Ticker("XAUTRY=X")
        gold_data = gold_try.history(period='1d')
        gold_value = round(gold_data['Close'].iloc[-1], 2)
        
        return JsonResponse({
            'bist100': bist100_value,
            'usd': usd_value,
            'eur': eur_value,
            'gold': gold_value,
            'last_updated': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500) 