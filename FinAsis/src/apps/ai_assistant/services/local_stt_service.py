# -*- coding: utf-8 -*-
"""
Lightweight wrapper for optional Vosk-based speech-to-text.

Imported by accounting.api as `from src.apps.ai_assistant.services import LocalSTTService`.
The Vosk dependency is imported lazily in __init__ to avoid import-time failures.
"""
from __future__ import annotations

from typing import Any


class LocalSTTService:
    """Yerel Vosk tabanlı konuşma-yazı servisi (basit WAV/PCM giriş)."""

    def __init__(self, model_path: str):
        try:
            from vosk import Model, KaldiRecognizer  # type: ignore
        except Exception as exc:  # pragma: no cover - executed only if vosk is missing
            raise RuntimeError("Vosk kurulu değil veya yüklenemedi") from exc
        self._Model = Model
        self._KaldiRecognizer = KaldiRecognizer
        self.model = Model(model_path)

    def transcribe(self, wav_bytes: bytes) -> str:
        import wave, json
        import io
        wf = wave.open(io.BytesIO(wav_bytes), "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 44100]:
            raise ValueError('Lütfen mono PCM WAV (16-bit) yükleyin.')
        rec = self._KaldiRecognizer(self.model, wf.getframerate())
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
