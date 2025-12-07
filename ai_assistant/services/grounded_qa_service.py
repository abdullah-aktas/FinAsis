# -*- coding: utf-8 -*-
"""
Basit Grounded QA servisi: Sadece bilgi tabanından (yerel + toplanan URL'ler) bulunan
parçalardan alıntı yaparak yanıt üretir, halüsinasyon yapmaz. Her yanıtla birlikte
kaynaklar (citation) döner.
"""
from __future__ import annotations

from typing import Any, Dict, List
from dataclasses import dataclass
from .knowledge_service import KnowledgeIndex


@dataclass
class QAResult:
    answer: str
    citations: List[Dict[str, str]]  # [{'title':..., 'path':..., 'snippet':...}]


class GroundedQAService:
    def __init__(self, index_path: str):
        self.index = KnowledgeIndex.load(index_path)

    def answer(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        if not self.index:
            return {
                "answer": "Bilgi tabanı bulunamadı. Lütfen önce kaynakları içeri alın.",
                "citations": [],
            }
        chunks = self.index.search(query, top_k=top_k)
        snippets: List[str] = []
        cites: List[Dict[str, str]] = []
        for ch in chunks:
            # basit: ilk 400 karakterlik alıntı
            snippet = (ch.content or "")[:400]
            snippets.append(f"[{ch.title}] {snippet}")
            cites.append({"title": ch.title, "path": ch.path, "snippet": snippet})
        # Yanıt: sadece alıntıları özetleyen birleştirme (halüsinasyon yok)
        answer_text = (
            "\n\n".join(snippets)
            if snippets
            else "Sorgunuza uygun doğrulanmış içerik bulunamadı."
        )
        return {"answer": answer_text, "citations": cites}
