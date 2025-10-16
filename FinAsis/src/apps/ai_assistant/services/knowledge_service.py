# -*- coding: utf-8 -*-
import json
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple


SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}['\"]?"),
    re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----"),
]


def _redact(text: str) -> str:
    redacted = text
    for pat in SENSITIVE_PATTERNS:
        redacted = pat.sub("[REDACTED]", redacted)
    return redacted


@dataclass
class KnowledgeChunk:
    id: str
    path: str
    title: str
    content: str


class KnowledgeIndex:
    def __init__(self, items: List[Dict[str, Any]]):
        self.chunks: List[KnowledgeChunk] = [
            KnowledgeChunk(
                id=str(i.get("id") or idx),
                path=str(i.get("path") or ""),
                title=str(i.get("title") or ""),
                content=_redact(str(i.get("content") or "")),
            )
            for idx, i in enumerate(items)
        ]

    @staticmethod
    def load(path: str) -> Optional["KnowledgeIndex"]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("chunks") if isinstance(data, dict) else data
            if not isinstance(items, list):
                return None
            return KnowledgeIndex(items)
        except Exception:
            return None

    def search(self, query: str, top_k: int = 3) -> List[KnowledgeChunk]:
        q = query.lower()
        q_tokens = [t for t in re.findall(r"[\wçğıöşü]+", q) if len(t) > 2]
        if not q_tokens:
            return []
        scores: List[Tuple[float, KnowledgeChunk]] = []
        for ch in self.chunks:
            text = (ch.title + "\n" + ch.content).lower()
            # çok basit bir puanlama: token eşleşme sayısı + başlık boost
            match = sum(text.count(t) for t in q_tokens)
            if ch.title:
                match += sum((3 if t in ch.title.lower() else 0) for t in q_tokens)
            if match > 0:
                scores.append((float(match), ch))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scores[:top_k]]
