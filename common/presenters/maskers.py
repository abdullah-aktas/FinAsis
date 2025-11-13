from __future__ import annotations

import re
from typing import Callable

EMAIL_RE = re.compile(r"(?P<local>[A-Za-z0-9_.+-]+)@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,})")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-]{8,}\d)")
IBAN_RE = re.compile(r"\b([A-Z]{2}\d{2}[A-Z0-9]{1,30})\b", re.IGNORECASE)
TC_RE = re.compile(r"\b\d{11}\b")


def mask_email(value: str) -> str:
    def repl(match: re.Match[str]) -> str:
        local = match.group("local")
        domain = match.group("domain")
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    return EMAIL_RE.sub(repl, value)


def mask_phone(value: str) -> str:
    def repl(match: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) < 6:
            return match.group(0)
        masked = digits[:2] + "*" * (len(digits) - 4) + digits[-2:]
        return masked

    return PHONE_RE.sub(repl, value)


def mask_iban(value: str) -> str:
    def repl(match: re.Match[str]) -> str:
        iban = match.group(0).replace(" ", "")
        if len(iban) <= 8:
            return "*" * len(iban)
        return iban[:4] + "*" * (len(iban) - 8) + iban[-4:]

    return IBAN_RE.sub(repl, value)


def mask_tc(value: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tc = match.group(0)
        return tc[:3] + "*" * 6 + tc[-2:]

    return TC_RE.sub(repl, value)


MASK_PIPELINE: tuple[Callable[[str], str], ...] = (
    mask_email,
    mask_phone,
    mask_iban,
    mask_tc,
)


def mask_text(value: str) -> str:
    masked = value
    for fn in MASK_PIPELINE:
        masked = fn(masked)
    return masked


__all__ = [
    "mask_email",
    "mask_phone",
    "mask_iban",
    "mask_tc",
    "mask_text",
]

