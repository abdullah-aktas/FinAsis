# -*- coding: utf-8 -*-
import logging
from typing import Dict, Any
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from ..models import MarketAnalysis

logger = logging.getLogger(__name__)

def get_market_analysis() -> Dict[str, Any]:
    """
    Piyasa analizi verilerini getirir
    
    Returns:
        dict: Piyasa analizi sonuçları
    """
    try:
        # BIST 100 endeksi
        bist = yf.Ticker("XU100.IS")
        bist_data = bist.history(period="1mo")
        
        # Dolar/TL
        usdtry = yf.Ticker("USDTRY=X")
        usdtry_data = usdtry.history(period="1mo")
        
        # Euro/TL
        eurtry = yf.Ticker("EURTRY=X")
        eurtry_data = eurtry.history(period="1mo")
        
        # Altın
        gold = yf.Ticker("GC=F")
        gold_data = gold.history(period="1mo")
        
        # Analiz sonuçları
        analysis = {
            'bist100': {
                'current': bist_data['Close'].iloc[-1],
                'change': ((bist_data['Close'].iloc[-1] - bist_data['Close'].iloc[0]) / bist_data['Close'].iloc[0]) * 100,
                'volume': bist_data['Volume'].iloc[-1],
                'trend': 'yükseliş' if bist_data['Close'].iloc[-1] > bist_data['Close'].iloc[0] else 'düşüş'
            },
            'usdtry': {
                'current': usdtry_data['Close'].iloc[-1],
                'change': ((usdtry_data['Close'].iloc[-1] - usdtry_data['Close'].iloc[0]) / usdtry_data['Close'].iloc[0]) * 100,
                'trend': 'yükseliş' if usdtry_data['Close'].iloc[-1] > usdtry_data['Close'].iloc[0] else 'düşüş'
            },
            'eurtry': {
                'current': eurtry_data['Close'].iloc[-1],
                'change': ((eurtry_data['Close'].iloc[-1] - eurtry_data['Close'].iloc[0]) / eurtry_data['Close'].iloc[0]) * 100,
                'trend': 'yükseliş' if eurtry_data['Close'].iloc[-1] > eurtry_data['Close'].iloc[0] else 'düşüş'
            },
            'gold': {
                'current': gold_data['Close'].iloc[-1],
                'change': ((gold_data['Close'].iloc[-1] - gold_data['Close'].iloc[0]) / gold_data['Close'].iloc[0]) * 100,
                'trend': 'yükseliş' if gold_data['Close'].iloc[-1] > gold_data['Close'].iloc[0] else 'düşüş'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Veritabanına kaydet
        MarketAnalysis.objects.create(
            analysis_data=analysis,
            timestamp=datetime.now()
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Piyasa analizi hatası: {str(e)}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        } 