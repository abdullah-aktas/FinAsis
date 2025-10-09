from __future__ import annotations

import lxml.etree as etree


def normalize_xml(xml_bytes: bytes) -> str:
    """Return a normalized string of the XML ignoring attribute order/whitespace."""
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(xml_bytes, parser)
    return etree.tostring(root, pretty_print=True, with_tail=False).decode("utf-8")


def assert_xml_similar(actual: bytes, expected: bytes) -> None:
    a = normalize_xml(actual)
    e = normalize_xml(expected)
    if a != e:
        # Provide a simple line-by-line diff if needed later; for now, raise with snippets
        raise AssertionError(f"XML differs.\nActual:\n{a}\nExpected:\n{e}")
