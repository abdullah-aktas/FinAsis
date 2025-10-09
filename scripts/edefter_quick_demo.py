from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

# Ensure repository root is on sys.path when running this script directly
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from FinAsis.src.edoc.edefter.generator import (
    JournalEntryDTO,
    JournalLine,
    build_kebir,
    build_yevmiye,
)
from FinAsis.src.edoc.edefter.berat import build_berat_xml
from FinAsis.src.edoc.edefter.packaging import build_output_name, package_zip


def build_sample_entries(year: int, month: int) -> list[JournalEntryDTO]:
    # Minimal, balanced sample entries for the given period
    d1 = date(year, month, 1)
    d2 = date(year, month, 2)

    entries: list[JournalEntryDTO] = [
        JournalEntryDTO(
            date_=d1,
            number="1",
            lines=[
                JournalLine("100", debit=Decimal("100.00")),
                JournalLine("600", credit=Decimal("100.00")),
            ],
        ),
        JournalEntryDTO(
            date_=d2,
            number="2",
            lines=[
                JournalLine("101", debit=Decimal("250.00")),
                JournalLine("320", credit=Decimal("250.00")),
            ],
        ),
    ]
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate e-Defter demo ZIP (Yevmiye/Kebir/Berat)")
    parser.add_argument("--year", type=int, required=True, help="Year, e.g. 2025")
    parser.add_argument("--month", type=int, required=True, choices=range(1, 13), help="Month 1-12")
    parser.add_argument("--vkn", type=str, required=True, help="Company VKN/TCKN, e.g. 1234567890")
    parser.add_argument("--out", type=str, help="Optional path to write the ZIP file")
    args = parser.parse_args()

    year: int = args.year
    month: int = args.month
    vkn: str = args.vkn

    # Build sample entries and generate XMLs
    entries = build_sample_entries(year, month)
    yxml = build_yevmiye(entries)
    kxml = build_kebir(entries)

    # Minimal berat: hash of yevmiye xml
    period = f"{year:04d}-{month:02d}"
    last_hash = hashlib.sha256(yxml).hexdigest()
    berat = build_berat_xml(period, vkn, last_hash)

    files = {
        build_output_name(vkn, year, month, "yevmiye"): yxml,
        build_output_name(vkn, year, month, "kebir"): kxml,
        build_output_name(vkn, year, month, "berat"): berat,
    }

    zip_bytes = package_zip(files)

    print("Artifacts:")
    for name, data in files.items():
        print(f" - {name}: {len(data)} bytes")
    print(f"ZIP size: {len(zip_bytes)} bytes")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(zip_bytes)
        print(f"Written ZIP -> {out_path}")


if __name__ == "__main__":
    main()
