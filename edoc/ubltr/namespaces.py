"""Common UBL and TR-specific namespaces and helpers."""

UBL_NS = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2",
    "udt": "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    # TR profile specific (commonly used identifiers)
    "eftr": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",  # document ns stays UBL Invoice-2
}


def ns(tag: str) -> str:
    """Return Clark-notation qualified tag like '{ns}LocalName' given 'prefix:LocalName'.

    Example: ns('cbc:ID') -> '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID'
    """
    if ":" not in tag:
        return tag
    prefix, local = tag.split(":", 1)
    uri = UBL_NS.get(prefix, prefix)
    return f"{{{uri}}}{local}"
