from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

import yaml
from django.apps import apps
from django.conf import settings

BASE_DIR = Path(settings.BASE_DIR)
CHECKLIST_DIR = BASE_DIR / "compliance" / "checklists"


@dataclass
class CheckResult:
    id: str
    title: str
    severity: str
    passed: bool
    skipped: bool
    message: str
    component: str | None = None


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _setting_equals(params: Dict[str, Any]) -> tuple[bool, str]:
    path = params["path"]
    expected = params.get("expected")
    actual = getattr(settings, path, None)
    return actual == expected, f"Beklenen={expected!r}, mevcut={actual!r}"


def _setting_contains(params: Dict[str, Any]) -> tuple[bool, str]:
    path = params["path"]
    expected = params.get("expected")
    value = getattr(settings, path, [])
    contains = False
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        contains = expected in value
    return (
        contains,
        f"{expected} değeri {path} içinde {'bulundu' if contains else 'bulunamadı'}.",
    )


def _model_exists(params: Dict[str, Any]) -> tuple[bool, str]:
    model_path = params["model"]
    try:
        app_label, model_name = model_path.split(".", 1)
        apps.get_model(app_label, model_name)
        return True, "Model bulunuyor."
    except Exception as exc:  # pragma: no cover - unexpected formatting
        return False, f"Model bulunamadı: {exc}"


def _app_installed(params: Dict[str, Any]) -> tuple[bool, str]:
    app_label = params["app"]
    installed = app_label in settings.INSTALLED_APPS
    return installed, f"{app_label} {'yüklü' if installed else 'yüklü değil'}."


CHECK_HANDLERS: Dict[str, Callable[[Dict[str, Any]], tuple[bool, str]]] = {
    "setting_equals": _setting_equals,
    "setting_contains": _setting_contains,
    "model_exists": _model_exists,
    "app_installed": _app_installed,
}


def load_checklist(profile: str) -> List[Dict[str, Any]]:
    path = CHECKLIST_DIR / f"{profile}.yml"
    if not path.exists():
        raise FileNotFoundError(f"{profile} checklist bulunamadı ({path}).")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or []
    return data


def run_check(entry: Dict[str, Any], *, debug: bool) -> CheckResult:
    check_id = entry.get("id", "unknown")
    title = entry.get("title", check_id)
    severity = entry.get("severity", "info")
    skip_if_debug = entry.get("skip_if_debug", False)
    component = entry.get("component")

    if skip_if_debug and debug:
        return CheckResult(
            id=check_id,
            title=title,
            severity=severity,
            passed=True,
            skipped=True,
            message="DEBUG modunda atlandı.",
            component=component,
        )

    handler = CHECK_HANDLERS.get(entry.get("type"))
    if handler is None:
        return CheckResult(
            id=check_id,
            title=title,
            severity=severity,
            passed=False,
            skipped=False,
            message=f"Desteklenmeyen kontrol tipi: {entry.get('type')}",
            component=component,
        )

    passed, message = handler(entry)
    return CheckResult(
        id=check_id,
        title=title,
        severity=severity,
        passed=passed,
        skipped=False,
        message=message,
        component=component,
    )
