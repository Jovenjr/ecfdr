"""
Builder de XML para e-CF con validación XSD integrada.

Este módulo centraliza:
- Construcción de XML (placeholder con ElementTree)
- Limpieza de tags vacíos
- Escape de texto según DGII
- Validación XSD por tipo (usando xsd_validator)

Uso de ejemplo:
    xml = build_ecf_xml(data, tipo="43")
    ok, errors = validate_ecf_xml(xml, tipo="43")
"""
from __future__ import annotations
from typing import Dict, Tuple, List
from xml.etree import ElementTree as ET

from .xml_utils import escape_text, remove_empty_elements
from .xsd_validator import validate_xml


# Mapa de tipo -> nombre de XSD empaquetado
XSD_BY_TIPO: Dict[str, str] = {
    "31": "e-CF 31 v.1.0.xsd",
    "32": "e-CF 32 v.1.0.xsd",
    "33": "e-CF 33 v.1.0.xsd",
    "34": "e-CF 34 v.1.0.xsd",
    "41": "e-CF 41 v.1.0.xsd",
    "43": "e-CF 43 v.1.0.xsd",
    "44": "e-CF 44 v.1.0.xsd",
    "45": "e-CF 45 v.1.0.xsd",
    "46": "e-CF 46 v.1.0.xsd",
    "47": "e-CF 47 v.1.0.xsd",
}


def build_ecf_xml(data: Dict, *, tipo: str) -> str:
    """Construye un XML e-CF básico (placeholder) a partir de un dict.
    NOTA: Esta función deberá ser reemplazada por un mapeo 1:1 contra XSD.
    """
    root = ET.Element("ECF")
    # ejemplo mínimo (placeholder): añadir algunos nodos comunes
    emisor = ET.SubElement(root, "Emisor")
    ET.SubElement(emisor, "RNCEmisor").text = escape_text(str(data.get("rnc_emisor", "")))

    receptor = ET.SubElement(root, "Receptor")
    if data.get("rnc_comprador"):
        ET.SubElement(receptor, "RNCComprador").text = escape_text(str(data.get("rnc_comprador")))

    cabecera = ET.SubElement(root, "Encabezado")
    ET.SubElement(cabecera, "ENCF").text = escape_text(str(data.get("encf", "")))
    ET.SubElement(cabecera, "TipoECF").text = escape_text(tipo)
    ET.SubElement(cabecera, "FechaEmision").text = escape_text(str(data.get("fecha_emision", "")))

    # Detalles placeholder
    detalles = ET.SubElement(root, "Detalles")
    for item in data.get("items", []):
        it = ET.SubElement(detalles, "Item")
        ET.SubElement(it, "Descripcion").text = escape_text(str(item.get("descripcion", "")))
        ET.SubElement(it, "Cantidad").text = escape_text(str(item.get("cantidad", "")))
        ET.SubElement(it, "PrecioUnitario").text = escape_text(str(item.get("precio_unitario", "")))

    # Limpieza de tags vacíos según regla DGII
    remove_empty_elements(root)

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def validate_ecf_xml(xml_content: str, *, tipo: str) -> Tuple[bool, List[str]]:
    xsd_name = XSD_BY_TIPO.get(tipo)
    if not xsd_name:
        return False, [f"No hay XSD mapeado para el tipo e-CF {tipo}"]
    return validate_xml(xml_content, xsd_name=xsd_name)
