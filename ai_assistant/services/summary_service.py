# -*- coding: utf-8 -*-
"""
Document Summarization Service
Doküman özetleme - uzun metinleri kısa özetlere dönüştürme
Local AI - External API kullanmaz
"""
import re
from typing import Dict, List
from collections import Counter
from ..models import DocumentSummary


class DocumentSummarizationService:
    """
    Local document summarization service
    Extractive summarization - önemli cümleleri seçerek özet oluşturur
    """

    @classmethod
    def summarize_text(
        cls, text: str, max_sentences: int = 5, language: str = "tr"
    ) -> Dict:
        """
        Metni özetler - extractive summarization

        Args:
            text: Özetlenecek metin
            max_sentences: Özette maksimum cümle sayısı
            language: Dil kodu

        Returns:
            {
                'summary': 'Özet metin',
                'summary_length': int,
                'original_length': int,
                'compression_ratio': float,
                'key_points': [...],
                'entities': [...]
            }
        """
        # Cümlelere ayır
        sentences = cls._split_into_sentences(text)

        if len(sentences) == 0:
            return {
                "summary": "",
                "summary_length": 0,
                "original_length": 0,
                "compression_ratio": 0,
                "key_points": [],
                "entities": [],
            }

        # Eğer zaten kısa ise, tamamını döndür
        if len(sentences) <= max_sentences:
            summary = " ".join(sentences)
            return {
                "summary": summary,
                "summary_length": len(summary.split()),
                "original_length": len(text.split()),
                "compression_ratio": 1.0,
                "key_points": sentences,
                "entities": cls._extract_entities(text),
            }

        # Cümle skorlama - kelime frekansı bazlı
        word_frequencies = cls._calculate_word_frequencies(text, language)
        sentence_scores = cls._score_sentences(sentences, word_frequencies)

        # En yüksek skorlu cümleleri seç
        top_sentences = sorted(
            sentence_scores.items(), key=lambda x: x[1], reverse=True
        )[:max_sentences]

        # Orijinal sırayla sırala
        summary_sentences = [
            sent
            for sent, score in sorted(
                top_sentences, key=lambda x: sentences.index(x[0])
            )
        ]

        summary = " ".join(summary_sentences)
        summary_words = summary.split()
        original_words = text.split()

        return {
            "summary": summary,
            "summary_length": len(summary_words),
            "original_length": len(original_words),
            "compression_ratio": (
                round(len(summary_words) / len(original_words), 2)
                if original_words
                else 0
            ),
            "key_points": summary_sentences,
            "entities": cls._extract_entities(summary),
        }

    @classmethod
    def _split_into_sentences(cls, text: str) -> List[str]:
        """Metni cümlelere ayırır"""
        # Nokta, soru işareti, ünlem ile bitenleri cümle olarak al
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    @classmethod
    def _calculate_word_frequencies(cls, text: str, language: str) -> Dict[str, int]:
        """Kelime frekanslarını hesaplar (stop words hariç)"""
        # Türkçe stop words (yaygın kelimeler)
        stop_words_tr = {
            "ve",
            "veya",
            "ile",
            "için",
            "bir",
            "bu",
            "şu",
            "o",
            "de",
            "da",
            "mi",
            "mı",
            "mu",
            "mü",
            "gibi",
            "kadar",
            "daha",
            "çok",
            "az",
            "var",
            "yok",
            "ama",
            "fakat",
            "ancak",
            "ne",
            "neden",
            "nasıl",
        }

        words = text.lower().split()
        # Stop words ve kısa kelimeleri filtrele
        filtered_words = [
            word for word in words if len(word) > 2 and word not in stop_words_tr
        ]

        return dict(Counter(filtered_words))

    @classmethod
    def _score_sentences(
        cls, sentences: List[str], word_frequencies: Dict[str, int]
    ) -> Dict[str, float]:
        """Her cümleyi skorlar"""
        scores = {}

        for sentence in sentences:
            words = sentence.lower().split()
            score = sum(word_frequencies.get(word, 0) for word in words)

            # Normalize et (cümle uzunluğuna göre)
            if len(words) > 0:
                score = score / len(words)

            scores[sentence] = score

        return scores

    @classmethod
    def _extract_entities(cls, text: str) -> List[Dict]:
        """Metinden entity'leri çıkarır"""
        entities = []

        # Para birimi
        money = re.findall(r"\d+(?:[.,]\d+)?\s*(?:TL|USD|EUR|₺|\$|€)", text)
        for m in money:
            entities.append({"type": "money", "value": m})

        # Tarih
        dates = re.findall(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b", text)
        for d in dates:
            entities.append({"type": "date", "value": d})

        # Yüzde
        percentages = re.findall(r"\d+(?:[.,]\d+)?%", text)
        for p in percentages:
            entities.append({"type": "percentage", "value": p})

        return entities

    @classmethod
    def summarize_and_save(
        cls,
        text: str,
        user,
        document_type: str = "other",
        max_sentences: int = 5,
        language: str = "tr",
        document_file=None,
    ) -> DocumentSummary:
        """
        Özetle ve veritabanına kaydet
        """
        result = cls.summarize_text(text, max_sentences, language)

        summary_obj = DocumentSummary.objects.create(
            user=user,
            document_type=document_type,
            original_text=text,
            summary=result["summary"],
            summary_length=result["summary_length"],
            original_length=result["original_length"],
            compression_ratio=result["compression_ratio"],
            key_points=result["key_points"],
            entities_mentioned=result["entities"],
            language=language,
            document_file=document_file,
        )

        return summary_obj

    @classmethod
    def batch_summarize(cls, documents: List[Dict], user) -> List[DocumentSummary]:
        """
        Toplu doküman özetleme

        Args:
            documents: [{'text': '...', 'type': '...', 'max_sentences': 5}, ...]
            user: Kullanıcı

        Returns:
            DocumentSummary listesi
        """
        summaries = []

        for doc in documents:
            summary = cls.summarize_and_save(
                text=doc.get("text", ""),
                user=user,
                document_type=doc.get("type", "other"),
                max_sentences=doc.get("max_sentences", 5),
            )
            summaries.append(summary)

        return summaries
