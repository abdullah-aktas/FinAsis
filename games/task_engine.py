from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import yaml


CATALOG_PATH = Path(__file__).resolve().parent / "data" / "mission_catalog.yml"


@dataclass(frozen=True)
class Task:
    id: str
    audience: str
    kind: str
    title: str
    description: str
    icon: str = "bi-flag"
    link_label: str | None = None
    link_href: str | None = None
    reward_xp: int | None = None
    tags: Sequence[str] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Task":
        return cls(
            id=str(data.get("id")),
            audience=str(data.get("audience")),
            kind=str(data.get("kind")),
            title=str(data.get("title")),
            description=str(data.get("description")),
            icon=str(data.get("icon", "bi-flag")),
            link_label=data.get("link", {}).get("label"),
            link_href=data.get("link", {}).get("href"),
            reward_xp=data.get("reward", {}).get("xp"),
            tags=tuple(data.get("tags", []) or []),
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "cta_label": self.link_label,
            "cta_href": self.link_href,
            "href": self.link_href,
            "reward_xp": self.reward_xp,
            "tags": list(self.tags),
        }


@lru_cache(maxsize=1)
def _load_catalog() -> List[Task]:
    if not CATALOG_PATH.exists():
        return []
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    tasks = []
    for item in payload.get("tasks", []) or []:
        try:
            tasks.append(Task.from_mapping(item))
        except Exception:
            continue
    return tasks


def get_tasks(
    *, audience: str, kind: str | None = None, limit: int | None = None
) -> List[Dict[str, Any]]:
    """Görev motorundan persona/kategori bazlı görev listesi sağlar."""
    results: Iterable[Task] = (
        task
        for task in _load_catalog()
        if task.audience == audience and (kind is None or task.kind == kind)
    )
    tasks = [task.as_dict() for task in results]
    if limit is not None:
        tasks = tasks[:limit]
    return tasks


def get_brief(*, audience: str) -> Dict[str, Any]:
    """Görevlerin toplu brifing özetini döndürür."""
    tasks = [task for task in _load_catalog() if task.audience == audience]
    total_xp = sum(task.reward_xp or 0 for task in tasks)
    return {
        "audience": audience,
        "task_count": len(tasks),
        "total_reward_xp": total_xp,
        "tags": sorted({tag for task in tasks for tag in task.tags}),
    }


__all__ = ["get_tasks", "get_brief"]
