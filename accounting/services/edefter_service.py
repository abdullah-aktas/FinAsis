import hashlib
import time
from decimal import Decimal

import requests
from requests.adapters import HTTPAdapter

try:
    # requests vendor packages urllib3; Retry is commonly available
    from urllib3.util.retry import Retry  # type: ignore
except Exception:  # pragma: no cover
    Retry = None  # type: ignore

from django.conf import settings
from django.core.files.base import ContentFile
from ..models import EDefter
from ..models import GLJournalEntry as _GLJournalEntry, GLJournalLine as _GLJournalLine
import logging

try:
    from FinAsis.src.edoc.edefter.generator import (
        JournalEntryDTO,
        JournalLine,
        build_yevmiye,
        build_kebir,
    )
    from FinAsis.src.edoc.edefter.berat import build_berat_xml
    from FinAsis.src.edoc.edefter.packaging import build_output_name, package_zip
    from FinAsis.src.edoc.signing.providers import (
        DummySigner,
        DummyTimestampProvider,
        Signer,
        TimestampProvider,
    )
except Exception:  # pragma: no cover - fallback when optional FinAsis package missing
    from dataclasses import dataclass

    @dataclass
    class JournalLine:
        account: str
        debit: Decimal
        credit: Decimal
        description: str = ""

    @dataclass
    class JournalEntryDTO:
        date_: any
        number: str
        lines: list[JournalLine]

    def build_yevmiye(entries: list[JournalEntryDTO]) -> bytes:
        return b"<yevmiye/>"

    def build_kebir(entries: list[JournalEntryDTO]) -> bytes:
        return b"<kebir/>"

    def build_berat_xml(period: str, vkn: str, last_hash: str) -> bytes:
        return f"<berat period='{period}' vkn='{vkn}' hash='{last_hash}'/>".encode()

    def build_output_name(company, year: int, month: int) -> str:
        return f"edefter_{getattr(company, 'id', 'company')}_{year}_{month}".lower()

    def package_zip(output_name: str, files: dict[str, bytes]) -> bytes:
        # simple zip placeholder
        import io
        from zipfile import ZipFile

        buffer = io.BytesIO()
        with ZipFile(buffer, "w") as zf:
            for filename, content in files.items():
                zf.writestr(filename, content)
        return buffer.getvalue()

    class DummySigner:
        def sign(self, content: bytes) -> bytes:
            return content

    class DummyTimestampProvider:
        def timestamp(self, content: bytes) -> bytes:
            return content

    Signer = DummySigner
    TimestampProvider = DummyTimestampProvider

defter_logger = logging.getLogger("edefter")


# --- HTTP helpers (retry/timeout) ---
def _get_retry_session() -> requests.Session:
    """Create a requests session with retry/backoff if available."""
    s = requests.Session()
    retries = int(getattr(settings, "EDEFTER_HTTP_RETRIES", 3))
    backoff = float(getattr(settings, "EDEFTER_HTTP_BACKOFF", 0.5))
    status_forcelist = (500, 502, 503, 504)
    if Retry is not None and retries > 0:
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff,
            status=retries,
            allowed_methods=("GET", "POST"),
            status_forcelist=status_forcelist,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
    return s


def _company_vkn(company) -> str:
    return str(getattr(company, "vkn", getattr(company, "tax_number", "0000000000")))


# --- DTO eşleme yardımcıları ---
def _line_to_dto(ln: _GLJournalLine) -> JournalLine:
    return JournalLine(
        account=getattr(getattr(ln, "account", None), "code", ""),
        debit=ln.debit if ln.debit is not None else Decimal("0.00"),
        credit=ln.credit if ln.credit is not None else Decimal("0.00"),
        description=ln.description or "",
    )


def fetch_journal_dtos(company, year: int, month: int) -> list[JournalEntryDTO]:
    qs = (
        _GLJournalEntry.objects.filter(
            company=company, date__year=year, date__month=month
        )
        .prefetch_related("lines__account")
        .order_by("date", "id")
    )
    result: list[JournalEntryDTO] = []
    for je in qs:
        line_qs = _GLJournalLine.objects.filter(entry=je).select_related("account")
        lines = [_line_to_dto(ln) for ln in line_qs]
        result.append(
            JournalEntryDTO(date_=je.date, number=str(je.number), lines=lines)
        )
    return result


def generate_yevmiye_defter(
    company, year, month, entries: list[JournalEntryDTO] | None = None
) -> bytes:
    """Yevmiye defterini üretir (minimal XML).

    entries dolu değilse boş bir defter üretir (toplamlar 0)."""
    if entries is None:
        entries = fetch_journal_dtos(company, year, month)
    else:
        entries = entries
    return build_yevmiye(entries)


def generate_kebir_defter(
    company, year, month, entries: list[JournalEntryDTO] | None = None
) -> bytes:
    """Kebir defterini üretir (minimal XML)."""
    if entries is None:
        entries = fetch_journal_dtos(company, year, month)
    else:
        entries = entries
    return build_kebir(entries)


def package_edefter(company, year, month, entries: list[JournalEntryDTO] | None = None):
    """e-Defter paketleme: Yevmiye XML ve berat içeriklerini döner.

    Not: Sprint 1'de XSD/doğrulama ve imzalama haricen ele alınır.
    """
    # 1) Yevmiye
    yevmiye_xml: bytes = generate_yevmiye_defter(company, year, month, entries)

    # 2) Berat (son hash)
    period = f"{year:04d}-{month:02d}"
    vkn = _company_vkn(company)
    last_hash = hashlib.sha256(yevmiye_xml).hexdigest()
    berat_xml: bytes = build_berat_xml(period, vkn, last_hash)

    return (yevmiye_xml, berat_xml)


def package_edefter_zip(
    company,
    year,
    month,
    entries: list[JournalEntryDTO] | None = None,
    *,
    include_signed: bool | None = None,
) -> bytes:
    """Yevmiye, Kebir ve Berat dosyalarını ZIP olarak paketler.

    include_signed True ise imzalı/zaman damgalı varyantlar da eklenir.
    Varsayılan: settings.EDEFTER_INCLUDE_SIGNED (yoksa False)
    """
    yevmiye_xml, berat_xml = package_edefter(company, year, month, entries)
    kebir_xml = generate_kebir_defter(company, year, month, entries)

    vkn = _company_vkn(company)
    files = {
        build_output_name(vkn, year, month, "yevmiye"): yevmiye_xml,
        build_output_name(vkn, year, month, "kebir"): kebir_xml,
        build_output_name(vkn, year, month, "berat"): berat_xml,
    }

    if include_signed is None:
        include_signed = bool(getattr(settings, "EDEFTER_INCLUDE_SIGNED", False))
    if include_signed:
        signer: Signer = getattr(settings, "EDEFTER_SIGNER", DummySigner())
        tsp: TimestampProvider = getattr(
            settings, "EDEFTER_TSP", DummyTimestampProvider()
        )
        files[build_output_name(vkn, year, month, "yevmiye") + ".sig"] = signer.sign(
            yevmiye_xml
        )
        files[build_output_name(vkn, year, month, "kebir") + ".sig"] = signer.sign(
            kebir_xml
        )
        files[build_output_name(vkn, year, month, "berat") + ".sig"] = signer.sign(
            berat_xml
        )
        # Zaman damgası örneği (imzalı üzerine eklemek tercih edilebilir)
        files[build_output_name(vkn, year, month, "yevmiye") + ".ts"] = tsp.timestamp(
            yevmiye_xml
        )
        files[build_output_name(vkn, year, month, "kebir") + ".ts"] = tsp.timestamp(
            kebir_xml
        )
        files[build_output_name(vkn, year, month, "berat") + ".ts"] = tsp.timestamp(
            berat_xml
        )
    return package_zip(files)


def generate_and_attach_edefter(
    edefter: EDefter,
    company,
    year: int,
    month: int,
    entries: list[JournalEntryDTO] | None = None,
) -> None:
    """Yevmiye ve Berat dosyalarını üretip `EDefter` nesnesine iliştirir.

    Varsayılan olarak `edefter.xml_file` ve `edefter.berat_file` alanları
    kullanılır; mevcutsa üzerine yazar. Başarıyla tamamlanınca `status='generated'`
    olarak güncellenir.
    """
    yevmiye_xml, berat_xml = package_edefter(company, year, month, entries)
    vkn = _company_vkn(company)
    yevmiye_name = build_output_name(vkn, year, month, "yevmiye")
    berat_name = build_output_name(vkn, year, month, "berat")

    # FileField.save(name, ContentFile(...), save=False) -> sonra tek seferde save
    if hasattr(edefter, "xml_file") and edefter.xml_file is not None:
        edefter.xml_file.save(yevmiye_name, ContentFile(yevmiye_xml), save=False)
    if hasattr(edefter, "berat_file") and edefter.berat_file is not None:
        edefter.berat_file.save(berat_name, ContentFile(berat_xml), save=False)
    if hasattr(edefter, "status"):
        edefter.status = "generated"
    edefter.save()


def send_edefter_to_gib(edefter: EDefter):
    xml_data = edefter.xml_file.read()
    base_url = getattr(
        settings, "GIB_EDEFTER_BASE_URL", "https://edefter-test.edefter.gov.tr/api"
    )
    url = f"{base_url}/sendDefter"
    headers = {
        "Content-Type": "application/xml; charset=utf-8",
        "Accept": "application/xml, text/xml, */*",
    }
    timeout = float(getattr(settings, "EDEFTER_HTTP_TIMEOUT", 15))
    sess = _get_retry_session()
    try:
        t0 = time.perf_counter()
        response = sess.post(
            url,
            data=xml_data,
            headers=headers,
            auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD),
            timeout=timeout,
        )
        elapsed = (time.perf_counter() - t0) * 1000.0
        edefter.status = "sent" if response.status_code == 200 else "error"
        edefter.save()
        preview = (response.text or "")[:500]
        defter_logger.info(
            f"e-Defter {edefter.pk} GİB'e gönderildi. Status: {response.status_code}, Süre: {elapsed:.1f}ms, Yanıt: {preview}"
        )
        return response
    except Exception as e:
        defter_logger.error(f"e-Defter {edefter.pk} GİB gönderim hatası: {str(e)}")
        if hasattr(edefter, "status"):
            edefter.status = "error"
            edefter.save()
        raise


def get_edefter_berat(edefter: EDefter):
    base_url = getattr(
        settings, "GIB_EDEFTER_BASE_URL", "https://edefter-test.edefter.gov.tr/api"
    )
    url = f"{base_url}/getBerat/{edefter.pk}"
    timeout = float(getattr(settings, "EDEFTER_HTTP_TIMEOUT", 15))
    sess = _get_retry_session()
    try:
        t0 = time.perf_counter()
        response = sess.get(
            url, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD), timeout=timeout
        )
        elapsed = (time.perf_counter() - t0) * 1000.0
        if response.status_code == 200:
            name = f"berat_{edefter.pk}.xml"
            if hasattr(edefter, "berat_file") and edefter.berat_file is not None:
                edefter.berat_file.save(name, ContentFile(response.content), save=False)
            if hasattr(edefter, "status"):
                edefter.status = "berat_alindi"
            edefter.save()
            defter_logger.info(
                f"e-Defter {edefter.pk} berat alındı. Status: {response.status_code}, Süre: {elapsed:.1f}ms"
            )
        else:
            preview = (response.text or "")[:500]
            defter_logger.warning(
                f"e-Defter {edefter.pk} berat alınamadı. Status: {response.status_code}, Süre: {elapsed:.1f}ms, Yanıt: {preview}"
            )
        return response
    except Exception as e:
        defter_logger.error(f"e-Defter {edefter.pk} berat alma hatası: {str(e)}")
        if hasattr(edefter, "status"):
            edefter.status = "error"
            edefter.save()
        raise
