from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from xml.etree import ElementTree as ET
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
import importlib.resources as pkg_resources

from .xml_utils import escape_text, remove_empty_elements
from .xsd_validator import validate_xml
from .input_validator import validate_against_spec
from .field_validators import (
    validate_encf,
    validate_rnc,
)


REQUIRED_EMISOR_FIELDS = [
    "RNCEmisor",
    "RazonSocialEmisor",
    "DireccionEmisor",
    "FechaEmision",
]

REQUIRED_IDDOC_FIELDS = [
    "TipoeCF",
    "eNCF",
    "FechaVencimientoSecuencia",
    "TipoIngresos",
    "TipoPago",
]

REQUIRED_COMPRADOR_FIELDS = [
    "RNCComprador",
    "RazonSocialComprador",
]

REQUIRED_ITEM_FIELDS = [
    "NumeroLinea",
    "IndicadorFacturacion",
    "NombreItem",
    "IndicadorBienoServicio",
    "CantidadItem",
    "UnidadMedida",
    "PrecioUnitarioItem",
    "MontoItem",
]


def _add_if_present(parent: ET.Element, tag: str, value: Optional[str]) -> None:
    if value is not None and str(value) != "":
        ET.SubElement(parent, tag).text = escape_text(str(value))


def _to_dmy(date_str: str) -> str:
    s = str(date_str)
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return s


def _to_dmy_hms(datetime_str: str) -> str:
    s = str(datetime_str)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%d-%m-%Y %H:%M:%S")
        except Exception:
            pass
    return s


def build_ecf45_xml(data: Dict) -> str:
    try:
        errs = validate_against_spec(data, spec_name="ecf45.json")
        if errs:
            raise ValueError("; ".join(errs))
    except FileNotFoundError:
        pass

    root = ET.Element("ECF")

    encabezado_in = data.get("encabezado", {})
    encabezado = ET.SubElement(root, "Encabezado")

    version = encabezado_in.get("Version", "1.0")
    ET.SubElement(encabezado, "Version").text = escape_text(str(version))

    iddoc_in = encabezado_in.get("IdDoc", {})
    iddoc = ET.SubElement(encabezado, "IdDoc")
    for key in REQUIRED_IDDOC_FIELDS:
        val = iddoc_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en IdDoc: {key}")
        text_val = str(val)
        if key in ("FechaVencimientoSecuencia", "FechaLimitePago"):
            text_val = _to_dmy(text_val)
        ET.SubElement(iddoc, key).text = escape_text(text_val)
    validate_encf(iddoc_in.get("eNCF"))

    emisor_in = encabezado_in.get("Emisor", {})
    emisor = ET.SubElement(encabezado, "Emisor")
    for key in REQUIRED_EMISOR_FIELDS:
        val = emisor_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Emisor: {key}")
        text_val = _to_dmy(str(val)) if key == "FechaEmision" else str(val)
        ET.SubElement(emisor, key).text = escape_text(text_val)
    validate_rnc(emisor_in.get("RNCEmisor"), field_name="RNCEmisor")

    comprador_in = encabezado_in.get("Comprador", {})
    comprador = ET.SubElement(encabezado, "Comprador")
    for key in REQUIRED_COMPRADOR_FIELDS:
        val = comprador_in.get(key)
        if val is None or str(val) == "":
            raise ValueError(f"Falta campo requerido en Comprador: {key}")
        _add_if_present(comprador, key, val)

    totales_in = encabezado_in.get("Totales", {})
    totales = ET.SubElement(encabezado, "Totales")
    monto_total = totales_in.get("MontoTotal")
    if monto_total is None or str(monto_total) == "":
        raise ValueError("Falta campo requerido en Totales: MontoTotal")
    _add_if_present(totales, "TotalITBIS", totales_in.get("TotalITBIS"))
    ET.SubElement(totales, "MontoTotal").text = escape_text(str(monto_total))

    detalles_in = data.get("detalles", {})
    items: List[Dict] = detalles_in.get("items", [])
    if not items:
        raise ValueError("Se requiere al menos un Item en DetallesItems")
    detalles_el = ET.SubElement(root, "DetallesItems")
    sum_items = Decimal("0")
    for it_in in items:
        item_el = ET.SubElement(detalles_el, "Item")
        for key in REQUIRED_ITEM_FIELDS:
            val = it_in.get(key)
            if val is None or str(val) == "":
                raise ValueError(f"Falta campo requerido en Item: {key}")
            ET.SubElement(item_el, key).text = escape_text(str(val))
        # Para e-CF 45, el XSD de Detalles no define el nodo Retencion, por lo que no lo insertamos ni lo exigimos.
        try:
            sum_items += Decimal(str(it_in.get("MontoItem")))
        except (InvalidOperation, TypeError):
            raise ValueError("MontoItem inválido: debe ser número con hasta 2 decimales")

    fecha_firma = data.get("fecha_hora_firma")
    if not fecha_firma:
        raise ValueError("Falta campo requerido: fecha_hora_firma")
    ET.SubElement(root, "FechaHoraFirma").text = escape_text(_to_dmy_hms(str(fecha_firma)))

    ET.SubElement(root, "Signature").text = "-"

    try:
        total = Decimal(str(monto_total))
    except (InvalidOperation, TypeError):
        raise ValueError("MontoTotal inválido: debe ser número con hasta 2 decimales")
    if (sum_items - total).copy_abs() > Decimal("0.01"):
        raise ValueError(f"Inconsistencia Totales: suma(MontoItem)={sum_items} difiere de MontoTotal={total}")

    remove_empty_elements(root)

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def build_and_validate_ecf45(data: Dict) -> Tuple[str, bool, List[str]]:
    xml = build_ecf45_xml(data)
    ok, errors = validate_xml(xml, xsd_name="e-CF 45 v.1.0.xsd")
    return xml, ok, errors


