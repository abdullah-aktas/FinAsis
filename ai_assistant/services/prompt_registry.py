from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml


PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "role_prompts.yml"


class PromptNotFound(Exception):
    """Belirtilen rol veya intent için prompt bulunamadığında fırlatılır."""


@lru_cache(maxsize=1)
def _load_catalog() -> Dict[str, Any]:
    if not PROMPT_FILE.exists():
        return {"roles": {}}
    with PROMPT_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def list_roles() -> Iterable[str]:
    """Konfigürasyonda tanımlı rollerin kodlarını döndürür."""
    catalog = _load_catalog()
    roles = catalog.get("roles", {}) or {}
    return roles.keys()


def get_prompts_for_role(
    role: str, *, limit: int | None = None
) -> List[Dict[str, Any]]:
    """Rol bazlı prompt listesini döndürür."""
    catalog = _load_catalog()
    role_entry = (catalog.get("roles") or {}).get(role)
    if not role_entry:
        return []
    prompts = role_entry.get("prompts", []) or []
    if limit is not None:
        prompts = prompts[:limit]
    return [
        {
            "intent": item.get("intent"),
            "title": item.get("title"),
            "body": item.get("body"),
            "cta_label": item.get("cta_label"),
            "cta_href": item.get("cta_href"),
            "icon": item.get("icon", "bi-robot"),
            "prompt": item.get("prompt", ""),
        }
        for item in prompts
    ]


def get_prompt(role: str, intent: str) -> Dict[str, Any]:
    """Belirtilen rol ve intent için tek prompt döndürür."""
    for prompt in get_prompts_for_role(role):
        if prompt.get("intent") == intent:
            return prompt
    raise PromptNotFound(f"Rol='{role}' intent='{intent}' için prompt bulunamadı.")


__all__ = ["get_prompts_for_role", "get_prompt", "list_roles", "PromptNotFound"]
