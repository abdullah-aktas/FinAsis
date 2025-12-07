# -*- coding: utf-8 -*-
import json
import os
import re
from dataclasses import dataclass
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup  # type: ignore
import requests


SENSITIVE_PATTERNS = [
    re.compile(
        r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}['\"]?"
    ),
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


class KnowledgeCrawler:
    """Basit dış kaynak toplayıcı: URL içeriklerini indirip JSON indekse ekler.

    Notlar:
    - Sadece genel erişime açık sayfalar; robots.txt'a saygı gösterme ve hız limiti
      gerçek kullanımda eklenmelidir.
    - Çıktı güvenlik için sızıntı desenlerine karşı redakte edilir.
    """

    def __init__(self, out_path: str):
        self.out_path = out_path

    def _extract_main_text(self, html: str) -> Tuple[str, str]:
        soup = BeautifulSoup(html, "lxml")
        title = (soup.title.string if soup.title else "") or ""
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        texts = [t.strip() for t in soup.stripped_strings]
        content = "\n".join(t for t in texts if t)
        return title.strip(), _redact(content)

    def add_urls(self, urls: List[str]) -> int:
        # mevcut dosyayı yükle
        current = KnowledgeIndex.load(self.out_path)
        items: List[Dict[str, Any]] = (
            []
            if current is None
            else [
                {"id": ch.id, "path": ch.path, "title": ch.title, "content": ch.content}
                for ch in current.chunks
            ]
        )
        start_len = len(items)

        session = requests.Session()
        headers = {"User-Agent": "FinAsis-KB/1.0"}
        for u in urls:
            try:
                r = session.get(u, timeout=15, headers=headers)
                if r.status_code != 200:
                    continue
                title, content = self._extract_main_text(r.text)
                if not content:
                    continue
                items.append(
                    {
                        "id": len(items) + 1,
                        "path": u,
                        "title": title,
                        "content": content[:50000],  # boyut limiti
                    }
                )
            except Exception:
                continue

        os.makedirs(os.path.dirname(self.out_path), exist_ok=True)
        with open(self.out_path, "w", encoding="utf-8") as f:
            json.dump({"chunks": items}, f, ensure_ascii=False, indent=2)
        return len(items) - start_len

    def add_local_docs(self, docs: List[Dict[str, str]]) -> int:
        """Yerel içerikleri (başlık + içerik + path) indekse ekler.

        docs: [{ 'path': '/abs/path/or/logical', 'title': 'Başlık', 'content': '...' }]
        """
        current = KnowledgeIndex.load(self.out_path)
        items: List[Dict[str, Any]] = (
            []
            if current is None
            else [
                {"id": ch.id, "path": ch.path, "title": ch.title, "content": ch.content}
                for ch in current.chunks
            ]
        )
        # Mevcut kayıtlar için hızlı tekrar ekleme kontrolü (path+title ve içerik hash'i)
        existing_keys = set()
        existing_content_hashes = set()
        for it in items:
            key = f"{it.get('path','').strip()}:::{it.get('title','').strip()}"
            existing_keys.add(key)
            content_val = it.get("content", "")
            content_hash = hashlib.sha256(
                content_val.encode("utf-8", errors="ignore")
            ).hexdigest()
            existing_content_hashes.add(content_hash)
        start_len = len(items)
        for d in docs:
            try:
                title = str(d.get("title") or "").strip()
                path = str(d.get("path") or "").strip()
                content = _redact(str(d.get("content") or "")).strip()
                if not content:
                    continue
                key = f"{path}:::{title}"
                if key in existing_keys:
                    # Aynı path+title zaten eklenmiş
                    continue
                content_hash = hashlib.sha256(
                    content.encode("utf-8", errors="ignore")
                ).hexdigest()
                if content_hash in existing_content_hashes:
                    # İçerik zaten mevcut bir dokümanla aynı
                    continue
                items.append(
                    {
                        "id": len(items) + 1,
                        "path": path,
                        "title": title,
                        "content": content[:50000],
                    }
                )
                existing_keys.add(key)
                existing_content_hashes.add(content_hash)
            except Exception:
                continue
        out_dir = os.path.dirname(self.out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(self.out_path, "w", encoding="utf-8") as f:
            json.dump({"chunks": items}, f, ensure_ascii=False, indent=2)
        return len(items) - start_len
