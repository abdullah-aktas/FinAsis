# -*- coding: utf-8 -*-
# Services paketi için boş __init__.py dosyası 
from .financial_service import FinancialAIService
from .chat_service import ChatAIService
from .ocr_service import OCRService
from .market_service import get_market_analysis
from .ml_service import RecommendationService
try:
    from vosk import Model, KaldiRecognizer
except Exception:
    Model = None
    KaldiRecognizer = None

class LocalSTTService:
    """Yerel Vosk tabanlı konuşma-yazı servisi (basit WAV/PCM giriş)."""
    def __init__(self, model_path: str):
        if Model is None:
            raise RuntimeError('Vosk kurulu değil')
        self.model = Model(model_path)

    def transcribe(self, wav_bytes: bytes) -> str:
        import wave, json
        import io
        wf = wave.open(io.BytesIO(wav_bytes), "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 44100]:
            raise ValueError('Lütfen mono PCM WAV (16-bit) yükleyin.')
        rec = KaldiRecognizer(self.model, wf.getframerate())
        result_text = ''
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result_text += ' ' + res.get('text', '')
        res_final = json.loads(rec.FinalResult())
        result_text += ' ' + res_final.get('text', '')
        return result_text.strip()

__all__ = [
    'FinancialAIService',
    'ChatAIService',
    'OCRService',
    'get_market_analysis',
    'LocalSTTService',
    'RecommendationService'
] 