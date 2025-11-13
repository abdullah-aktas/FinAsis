from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import lxml.etree as etree

from ..shared.config import EdocSettings
from ..shared.errors import SchemaValidationError

# Common UBL XSD candidate paths. We also try a best-effort glob search.
_INVOICE_XSD_CANDIDATES = (
    "maindoc/UBL-Invoice-2.1.xsd",
    "maindoc/UBL-Invoice-2.3.xsd",
    "UBL-TR-2.3/maindoc/UBL-Invoice-2.1.xsd",
    "UBL-TR-2.3/maindoc/UBL-Invoice-2.3.xsd",
)

_DISPATCH_XSD_CANDIDATES = (
    "maindoc/UBL-DespatchAdvice-2.1.xsd",
    "maindoc/UBL-DespatchAdvice-2.3.xsd",
    "UBL-TR-2.3/maindoc/UBL-DespatchAdvice-2.1.xsd",
    "UBL-TR-2.3/maindoc/UBL-DespatchAdvice-2.3.xsd",
)


def _safe_parse_xsd(path: Path) -> etree.XMLSchema:
    with path.open("rb") as f:
        doc = etree.parse(f)
    return etree.XMLSchema(doc)


def _find_invoice_xsd(schemas_dir: Path) -> Optional[Path]:
    # Try known candidate paths first
    for rel in _INVOICE_XSD_CANDIDATES:
        candidate = schemas_dir / rel
        if candidate.exists():
            return candidate
    # Best-effort search: look for any UBL-Invoice*.xsd under maindoc/*
    maindoc = schemas_dir / "maindoc"
    if maindoc.exists():
        for p in maindoc.rglob("UBL-Invoice-*.xsd"):
            return p
    # Also try a broader search (limited depth) to avoid heavy scans
    for p in schemas_dir.glob("**/maindoc/UBL-Invoice-*.xsd"):
        return p
    return None


def _find_dispatch_xsd(schemas_dir: Path) -> Optional[Path]:
    for rel in _DISPATCH_XSD_CANDIDATES:
        candidate = schemas_dir / rel
        if candidate.exists():
            return candidate
    maindoc = schemas_dir / "maindoc"
    if maindoc.exists():
        for p in maindoc.rglob("UBL-DespatchAdvice-*.xsd"):
            return p
    for p in schemas_dir.glob("**/maindoc/UBL-DespatchAdvice-*.xsd"):
        return p
    return None


@lru_cache(maxsize=8)
def _get_cached_invoice_schema(schemas_dir_str: str) -> Optional[etree.XMLSchema]:
    schemas_dir = Path(schemas_dir_str)
    if not schemas_dir.exists():
        return None
    xsd_path = _find_invoice_xsd(schemas_dir)
    if not xsd_path:
        return None
    try:
        return _safe_parse_xsd(xsd_path)
    except (etree.XMLSchemaParseError, OSError):
        return None


@lru_cache(maxsize=8)
def _get_cached_dispatch_schema(schemas_dir_str: str) -> Optional[etree.XMLSchema]:
    schemas_dir = Path(schemas_dir_str)
    if not schemas_dir.exists():
        return None
    xsd_path = _find_dispatch_xsd(schemas_dir)
    if not xsd_path:
        return None
    try:
        return _safe_parse_xsd(xsd_path)
    except (etree.XMLSchemaParseError, OSError):
        return None


def has_invoice_schema(settings: Optional[EdocSettings] = None) -> bool:
    """Return True if an Invoice XSD can be loaded from configured schema dir."""
    settings = settings or EdocSettings.from_env()
    schemas_dir = settings.schemas_dir or os.environ.get("EDOC_SCHEMAS_DIR")
    if not schemas_dir:
        return False
    return _get_cached_invoice_schema(schemas_dir) is not None


def has_dispatch_schema(settings: Optional[EdocSettings] = None) -> bool:
    settings = settings or EdocSettings.from_env()
    schemas_dir = settings.schemas_dir or os.environ.get("EDOC_SCHEMAS_DIR")
    if not schemas_dir:
        return False
    return _get_cached_dispatch_schema(schemas_dir) is not None


def validate_invoice_xml(xml_bytes: bytes, settings: Optional[EdocSettings] = None) -> None:
    """Validate Invoice XML against UBL XSD if available.

    Looks for EDOC_SCHEMAS_DIR env or settings.schemas_dir. If a suitable
    UBL Invoice XSD cannot be found, the function returns without error
    (graceful skip) so that environments without XSDs can still run tests.
    """
    settings = settings or EdocSettings.from_env()
    schemas_dir = settings.schemas_dir or os.environ.get("EDOC_SCHEMAS_DIR")
    if not schemas_dir:
        return  # graceful skip

    schema = _get_cached_invoice_schema(schemas_dir)
    if schema is None:
        return  # skip if schemas not present

    try:
        xml_doc = etree.fromstring(xml_bytes)
        schema.assertValid(xml_doc)
    except etree.DocumentInvalid as exc:
        # Build actionable error from error_log
        log = schema.error_log
        if log:
            last = log.last_error
            if last is None:
                first = log[0]
                msg = f"Schema validation error at line {first.line}, column {first.column}: {first.message}"
            else:
                msg = f"Schema validation error at line {last.line}, column {last.column}: {last.message}"
        else:
            msg = str(exc)
        raise SchemaValidationError(msg) from exc


def validate_dispatch_xml(xml_bytes: bytes, settings: Optional[EdocSettings] = None) -> None:
    settings = settings or EdocSettings.from_env()
    schemas_dir = settings.schemas_dir or os.environ.get("EDOC_SCHEMAS_DIR")
    if not schemas_dir:
        return
    schema = _get_cached_dispatch_schema(schemas_dir)
    if schema is None:
        return
    try:
        xml_doc = etree.fromstring(xml_bytes)
        schema.assertValid(xml_doc)
    except etree.DocumentInvalid as exc:
        log = schema.error_log
        if log:
            last = log.last_error or log[0]
            msg = f"Schema validation error at line {last.line}, column {last.column}: {last.message}"
        else:
            msg = str(exc)
        raise SchemaValidationError(msg) from exc
