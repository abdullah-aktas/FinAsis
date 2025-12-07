"""Helpers for e-Defter output packaging (stubs for Sprint 1).

- build_output_name: deterministic file names per GİB conventions (simplified).
- package_zip: zip multiple artifacts into a bytes object (no filesystem writes).
"""
from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED


def build_output_name(company_vkn: str, year: int, month: int, kind: str) -> str:
    """Return output file name like: VKN_YYYYMM_kind.xml

    kind: 'yevmiye' | 'kebir' | 'berat'
    """
    ym = f"{year:04d}{month:02d}"
    return f"{company_vkn}_{ym}_{kind}.xml"


def package_zip(files: dict[str, bytes]) -> bytes:
    """Create an in-memory zip with given file contents.

    files: mapping of name -> content bytes
    """
    buf = BytesIO()
    with ZipFile(buf, mode="w", compression=ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()
