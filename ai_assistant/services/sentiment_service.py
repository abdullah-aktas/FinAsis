# -*- coding: utf-8 -*-
"""
Sentiment Analysis Service
Duygu analizi - metinlerin pozitif/negatif/nötr analizi
Local AI - External API kullanmaz
"""
import re
from typing import Dict, List
from ..models import SentimentAnalysis


class SentimentAnalysisService:
    """
    Local sentiment analysis service
    Türkçe metin duygu analizi - rule-based ve keyword matching
    """

    # Türkçe sentiment kelimeleri
    POSITIVE_KEYWORDS = [
        "memnun",
        "teşekkür",
        "harika",
        "mükemmel",
        "süper",
        "başarılı",
        "iyi",
        "kaliteli",
        "hızlı",
        "güzel",
        "çok iyi",
        "beğendim",
        "tavsiye",
        "profesyonel",
        "yardımcı",
        "işe yaradı",
        "kesinlikle",
        "mutlu",
        "sevindim",
        "takdir",
        "övgü",
        "olumlu",
    ]

    NEGATIVE_KEYWORDS = [
        "kötü",
        "berbat",
        "sorun",
        "problem",
        "şikayet",
        "memnun değil",
        "yavaş",
        "geç",
        "hata",
        "yanlış",
        "eksik",
        "yetersiz",
        "başarısız",
        "olmadı",
        "çalışmıyor",
        "bozuk",
        "kırgın",
        "üzgün",
        "pişman",
        "tavsiye etmem",
        "kullanmam",
    ]

    NEUTRAL_KEYWORDS = [
        "normal",
        "idare eder",
        "fena değil",
        "orta",
        "yeterli",
        "standart",
        "bilgi",
        "soru",
        "nasıl",
    ]

    @classmethod
    def analyze_text(cls, text: str, language: str = "tr") -> Dict:
        """
        Metni analiz eder ve sentiment skorları döner

        Args:
            text: Analiz edilecek metin
            language: Dil kodu (tr, en)

        Returns:
            {
                'sentiment': 'positive'|'neutral'|'negative',
                'confidence_score': 0.0-1.0,
                'positive_score': 0.0-1.0,
                'neutral_score': 0.0-1.0,
                'negative_score': 0.0-1.0,
                'keywords': [...],
                'entities': [...]
            }
        """
        text_lower = text.lower()

        # Keyword matching
        positive_count = sum(1 for kw in cls.POSITIVE_KEYWORDS if kw in text_lower)
        negative_count = sum(1 for kw in cls.NEGATIVE_KEYWORDS if kw in text_lower)
        neutral_count = sum(1 for kw in cls.NEUTRAL_KEYWORDS if kw in text_lower)

        total_keywords = positive_count + negative_count + neutral_count

        if total_keywords == 0:
            # Keyword bulunamadı - varsayılan nötr
            return {
                "sentiment": "neutral",
                "confidence_score": 0.5,
                "positive_score": 0.33,
                "neutral_score": 0.34,
                "negative_score": 0.33,
                "keywords": [],
                "entities": [],
            }

        # Skorları hesapla
        positive_score = positive_count / total_keywords if total_keywords > 0 else 0
        negative_score = negative_count / total_keywords if total_keywords > 0 else 0
        neutral_score = neutral_count / total_keywords if total_keywords > 0 else 0

        # Dominant sentiment
        scores = {
            "positive": positive_score,
            "neutral": neutral_score,
            "negative": negative_score,
        }
        sentiment = max(scores, key=scores.get)
        confidence = max(scores.values())

        # Anahtar kelimeleri çıkar
        found_keywords = []
        for kw in cls.POSITIVE_KEYWORDS + cls.NEGATIVE_KEYWORDS + cls.NEUTRAL_KEYWORDS:
            if kw in text_lower:
                found_keywords.append(kw)

        # Entity extraction (basit - email, para, tarih)
        entities = cls._extract_entities(text)

        return {
            "sentiment": sentiment,
            "confidence_score": confidence,
            "positive_score": positive_score,
            "neutral_score": neutral_score,
            "negative_score": negative_score,
            "keywords": found_keywords[:10],  # İlk 10
            "entities": entities,
        }

    @classmethod
    def _extract_entities(cls, text: str) -> List[Dict]:
        """
        Metinden entity'leri çıkarır (email, para, tarih, vb.)
        """
        entities = []

        # Email
        emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
        )
        for email in emails:
            entities.append({"type": "email", "value": email})

        # Para (TL, USD, EUR)
        money_patterns = re.findall(r"\d+(?:[.,]\d+)?\s*(?:TL|USD|EUR|₺|\$|€)", text)
        for money in money_patterns:
            entities.append({"type": "money", "value": money})

        # Tarih (dd.mm.yyyy, dd/mm/yyyy)
        dates = re.findall(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b", text)
        for date in dates:
            entities.append({"type": "date", "value": date})

        return entities

    @classmethod
    def analyze_and_save(
        cls,
        text: str,
        user,
        source_type: str = "document",
        reference_model: str = "",
        reference_id: int = None,
        language: str = "tr",
    ) -> SentimentAnalysis:
        """
        Analiz yap ve veritabanına kaydet
        """
        analysis_result = cls.analyze_text(text, language)

        sentiment_obj = SentimentAnalysis.objects.create(
            user=user,
            source_type=source_type,
            text_content=text[:1000],  # İlk 1000 karakter
            sentiment=analysis_result["sentiment"],
            confidence_score=analysis_result["confidence_score"],
            positive_score=analysis_result["positive_score"],
            neutral_score=analysis_result["neutral_score"],
            negative_score=analysis_result["negative_score"],
            keywords=analysis_result["keywords"],
            entities=analysis_result["entities"],
            language=language,
            reference_model=reference_model,
            reference_id=reference_id,
        )

        return sentiment_obj

    @classmethod
    def get_sentiment_statistics(cls, user=None, days=30) -> Dict:
        """
        Sentiment istatistiklerini döner
        """
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Count, Avg

        queryset = SentimentAnalysis.objects.all()

        if user:
            queryset = queryset.filter(user=user)

        # Son X gün
        since = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=since)

        # Sentiment dağılımı
        sentiment_counts = queryset.values("sentiment").annotate(count=Count("id"))

        # Ortalama confidence
        avg_confidence = queryset.aggregate(avg=Avg("confidence_score"))["avg"] or 0

        # Kaynak tiplerine göre sentiment
        by_source = queryset.values("source_type", "sentiment").annotate(
            count=Count("id")
        )

        return {
            "total_analyses": queryset.count(),
            "sentiment_distribution": list(sentiment_counts),
            "average_confidence": round(avg_confidence, 2),
            "by_source": list(by_source),
            "period_days": days,
        }
