from __future__ import annotations

from datetime import datetime
from typing import Optional
import importlib.resources as pkg_resources
import json
from xml.etree import ElementTree as ET

from .xml_utils import escape_text

CATALOG_FILE_BY_TYPE: dict[str, str] = {
    "UnidadMedidaType": "unidad_medida.json",
    "TipoMonedaType": "tipo_moneda.json",
    "ProvinciaMunicipioType": "provincia_municipio.json",
}

_catalog_cache: dict[str, list[str]] = {}


def load_catalog_values(catalog_type: str) -> list[str]:
    """Return cached catalog values for the given DGII catalog type."""
    filename = CATALOG_FILE_BY_TYPE.get(catalog_type)
    if not filename:
        return []
    if catalog_type in _catalog_cache:
        return _catalog_cache[catalog_type]

    data_pkg = "csf_do.csf_do.data"
    try:
        with pkg_resources.files(data_pkg).joinpath(filename).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        values: list[str] = []
    else:
        raw_values = payload.get("values")
        if raw_values is not None:
            values = [str(v) for v in raw_values]
        else:
            values = [
                str(entry.get("code"))
                for entry in payload.get("entries", [])
                if entry.get("code") is not None
            ]
    _catalog_cache[catalog_type] = values
    return values


def validate_catalog_value(field: str, value: Optional[str], *, catalog_type: str) -> None:
    """Validate that *value* belongs to the DGII catalog indicated by *catalog_type*."""
    if value is None or str(value) == "":
        return
    allowed = load_catalog_values(catalog_type)
    if allowed and str(value) not in allowed:
        raise ValueError(
            f"Valor inválido para {field}: '{value}'. Debe pertenecer a catálogo {catalog_type}."
        )


def add_text_if_not_empty(parent: ET.Element, tag: str, value: Optional[str]) -> Optional[ET.Element]:
    """Append *tag* to *parent* when *value* is meaningful. Return the created element or ``None``."""
    if value is None:
        return None
    text = str(value)
    if text == "":
        return None
    element = ET.SubElement(parent, tag)
    element.text = escape_text(text)
    return element


def to_dmy(date_input: str) -> str:
    """Convert an ISO date (YYYY-MM-DD) into DGII format DD-MM-YYYY when possible."""
    date_str = str(date_input)
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%d-%m-%Y")
    except Exception:
        return date_str


def to_dmy_hms(datetime_input: str) -> str:
    """Convert an ISO datetime into DGII format DD-MM-YYYY HH:MM:SS when possible."""
    dt_str = str(datetime_input)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(dt_str, fmt)
            return parsed.strftime("%d-%m-%Y %H:%M:%S")
        except Exception:
            continue
    return dt_str
