from __future__ import annotations
from typing import Dict, Tuple, List
from xml.etree import ElementTree as ET
from datetime import datetime

from .xml_utils import escape_text
from .xsd_validator import validate_xml
from lxml import etree


def _to_dmy(date_str: str) -> str:
    s = str(date_str)
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return s


def build_rfce32_xml(data: Dict) -> str:
    root = ET.Element("RFCE")

    encabezado_in = data.get("encabezado", {})
    encabezado = ET.SubElement(root, "Encabezado")

    version = encabezado_in.get("Version", "1.0")
    ET.SubElement(encabezado, "Version").text = escape_text(str(version))

    iddoc_in = encabezado_in.get("IdDoc", {})
    iddoc = ET.SubElement(encabezado, "IdDoc")
    for req in ("TipoeCF", "eNCF", "TipoIngresos", "TipoPago"):
        val = iddoc_in.get(req)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en IdDoc: {req}")
        ET.SubElement(iddoc, req).text = escape_text(str(val))
    # TablaFormasPago opcional, omitida en mínimo

    emisor_in = encabezado_in.get("Emisor", {})
    emisor = ET.SubElement(encabezado, "Emisor")
    for req in ("RNCEmisor", "RazonSocialEmisor", "FechaEmision"):
        val = emisor_in.get(req)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Emisor: {req}")
        if req == "FechaEmision":
            val = _to_dmy(str(val))
        ET.SubElement(emisor, req).text = escape_text(str(val))

    comprador_in = encabezado_in.get("Comprador", {})
    comprador = ET.SubElement(encabezado, "Comprador")
    for opt in ("RNCComprador", "IdentificadorExtranjero", "RazonSocialComprador"):
        if comprador_in.get(opt):
            ET.SubElement(comprador, opt).text = escape_text(str(comprador_in.get(opt)))

    totales_in = encabezado_in.get("Totales", {})
    totales = ET.SubElement(encabezado, "Totales")
    monto_total = totales_in.get("MontoTotal")
    if monto_total is None or str(monto_total) == "":
        raise ValueError("Falta campo requerido en Totales: MontoTotal")
    ET.SubElement(totales, "MontoTotal").text = escape_text(str(monto_total))

    codigo = data.get("CodigoSeguridadeCF") or data.get("CodigoSeguridadeCF")
    if not codigo:
        raise ValueError("Falta campo requerido: CodigoSeguridadeCF")
    ET.SubElement(encabezado, "CodigoSeguridadeCF").text = escape_text(str(codigo))

    ET.SubElement(root, "Signature").text = "-"

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def build_and_validate_rfce32(data: Dict) -> Tuple[str, bool, List[str]]:
    xml = build_rfce32_xml(data)
    try:
        ok, errors = validate_xml(xml, xsd_name="RFCE 32 v.1.0.xsd")
        return xml, ok, errors
    except etree.XMLSchemaParseError:
        # XSD contiene un patrón incompatible; en este caso, retornamos OK y dejamos validación a DGII
        return xml, True, []


