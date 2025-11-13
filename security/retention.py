from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable, List, Mapping

import yaml
from django.apps import apps
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

RETENTION_PROFILES_PATH = Path(settings.BASE_DIR) / "retention" / "profiles"


@dataclass
class RetentionRule:
    model: str
    action: str
    older_than_days: int
    timestamp_field: str = "created_at"
    filters: Mapping[str, Any] = field(default_factory=dict)
    mask_fields: Mapping[str, str] = field(default_factory=dict)
    batch_size: int = 500

    def cutoff(self) -> timezone.datetime:
        return timezone.now() - timedelta(days=self.older_than_days)


def load_profile(profile_name: str) -> List[RetentionRule]:
    profile_path = RETENTION_PROFILES_PATH / f"{profile_name}.yml"
    if not profile_path.exists():
        raise FileNotFoundError(f"Retention profili bulunamadı: {profile_path}")

    with profile_path.open("r", encoding="utf-8") as fp:
        raw_rules = yaml.safe_load(fp) or []

    rules: List[RetentionRule] = []
    for rule in raw_rules:
        rules.append(
            RetentionRule(
                model=rule["model"],
                action=rule.get("action", "delete"),
                older_than_days=int(rule.get("older_than_days", 365)),
                timestamp_field=rule.get("timestamp_field", "created_at"),
                filters=rule.get("filters", {}),
                mask_fields=rule.get("mask_fields", {}),
                batch_size=int(rule.get("batch_size", 500)),
            )
        )
    return rules


def _get_model(model_label: str) -> models.Model:
    try:
        return apps.get_model(model_label, require_ready=True)
    except LookupError as exc:  # pragma: no cover - konfigürasyon hatası
        raise LookupError(f"Model bulunamadı: {model_label}") from exc


def _build_queryset(model: models.Model, rule: RetentionRule) -> models.QuerySet:
    timestamp_lookup = {f"{rule.timestamp_field}__lt": rule.cutoff()}
    return model.objects.filter(**rule.filters).filter(**timestamp_lookup)


def execute_rule(rule: RetentionRule, *, dry_run: bool = False) -> dict[str, Any]:
    model = _get_model(rule.model)
    queryset = _build_queryset(model, rule)
    total = queryset.count()

    if total == 0:
        logger.info("Retention kuralı için uygun kayıt bulunamadı", extra={"model": rule.model})
        return {"model": rule.model, "action": rule.action, "affected": 0}

    if dry_run:
        logger.info(
            "Retention dry-run: %s kaydı etkilenecek",
            total,
            extra={"model": rule.model, "action": rule.action},
        )
        return {"model": rule.model, "action": rule.action, "affected": total}

    if rule.action == "delete":
        deleted, _ = queryset.delete()
        logger.info(
            "Retention delete: %s kaydı silindi",
            deleted,
            extra={"model": rule.model},
        )
        return {"model": rule.model, "action": "delete", "affected": deleted}

    if rule.action == "anonymize":
        return _anonymize_records(queryset, rule)

    raise ValueError(f"Bilinmeyen retention aksiyonu: {rule.action}")


def _anonymize_records(queryset: models.QuerySet, rule: RetentionRule) -> dict[str, Any]:
    if not rule.mask_fields:
        raise ValueError("Anonymize aksiyonu için mask_fields tanımlanmalı.")

    affected = 0
    with transaction.atomic():
        for batch in _iterate_queryset(queryset, rule.batch_size):
            ids = [obj.pk for obj in batch]
            if not ids:
                continue
            update_kwargs = {field: value for field, value in rule.mask_fields.items()}
            queryset.model.objects.filter(pk__in=ids).update(**update_kwargs)
            affected += len(ids)

    logger.info(
        "Retention anonymize: %s kayıt anonimleştirildi",
        affected,
        extra={"model": rule.model},
    )
    return {"model": rule.model, "action": "anonymize", "affected": affected}


def _iterate_queryset(queryset: models.QuerySet, batch_size: int) -> Iterable[list[models.Model]]:
    start = 0
    while True:
        batch = list(queryset[start : start + batch_size])
        if not batch:
            break
        yield batch
        start += batch_size


def execute_profile(profile_name: str, *, dry_run: bool = False) -> list[dict[str, Any]]:
    rules = load_profile(profile_name)
    results: list[dict[str, Any]] = []
    for rule in rules:
        logger.debug("Retention kuralı çalışıyor", extra={"model": rule.model, "action": rule.action})
        results.append(execute_rule(rule, dry_run=dry_run))
    return results


__all__ = ["RetentionRule", "execute_profile", "execute_rule", "load_profile"]

