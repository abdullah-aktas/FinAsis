from datetime import date

from FinAsis.src.edoc.edefter.berat import JournalEntry, compute_hash_chain, build_berat_xml, validate_berat_xml


def test_hash_chain_deterministic():
    entries = [
        JournalEntry(date(2025, 9, 1), "1", 100.0, 0.0),
        JournalEntry(date(2025, 9, 2), "2", 0.0, 100.0),
    ]
    chain1 = compute_hash_chain(entries)
    chain2 = compute_hash_chain(entries)
    assert chain1 == chain2
    assert len(chain1[-1]) == 64


def test_build_minimal_berat_xml():
    xml_bytes = build_berat_xml("2025-09", "1234567890", "deadbeef" * 8)
    validate_berat_xml(xml_bytes)
    text = xml_bytes.decode("utf-8")
    # Minimal shape checks (namespace prefix may vary)
    assert "<Berat" in text or ":Berat" in text
    assert "CompanyVKN" in text
    assert "LastHash" in text
