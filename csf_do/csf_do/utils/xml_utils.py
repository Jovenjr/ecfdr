"""
XML utilities for DGII e-CF integration.
- Strict escaping of special characters
- Helpers to drop empty tags when building XML payloads
- Filename helpers according to DGII standard
"""
from __future__ import annotations
from xml.etree import ElementTree as ET
from typing import Optional

ESCAPE_MAP = {
    '"': "&quot;",
    "&": "&amp;",
    "'": "&apos;",
    "<": "&lt;",
    ">": "&gt;",
}


def escape_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    out = value
    for k, v in ESCAPE_MAP.items():
        out = out.replace(k, v)
    return out


def remove_empty_elements(elem: ET.Element, *, preserve: set[str] | None = None) -> None:
    """Remove elements that are empty (no text and no children).
    If 'preserve' is provided, elements with tag in 'preserve' will NOT be removed even if empty.
    """
    if preserve is None:
        preserve = set()
    # Work on a copy of children to avoid mutation during iteration issues
    for child in list(elem):
        remove_empty_elements(child, preserve=preserve)
        has_text = (child.text or "").strip() != ""
        if child.tag in preserve:
            continue
        if not has_text and len(child) == 0:
            elem.remove(child)


def standard_xml_filename(rnc_emisor: str, encf: str, rnc_comprador: Optional[str] = None) -> str:
    """Return filename following DGII convention.
    If rnc_comprador is provided and applicable, use it; otherwise use rnc_emisor.
    """
    if rnc_comprador:
        return f"{rnc_comprador}+{encf}.xml"
    return f"{rnc_emisor}+{encf}.xml"
