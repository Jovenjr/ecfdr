"""
Validador XSD para DGII e-CF usando lxml.

Uso:
    from csf_do.csf_do.utils.xsd_validator import validate_xml
    ok, errors = validate_xml(xml_string, xsd_name="e-CF 43 v.1.0.xsd")

- Carga los XSD desde el paquete `csf_do/csf_do/xsd/` usando importlib.resources.
- Retorna (True, []) si el XML es válido; si no, (False, [lista de errores]).
"""
from __future__ import annotations
from typing import Tuple, List
from lxml import etree
import re
import importlib.resources as pkg_resources


def _load_xsd_schema(xsd_name: str) -> etree.XMLSchema:
    # Los XSD deben estar ubicados en el paquete: csf_do.csf_do.xsd
    package = "csf_do.csf_do.xsd"
    try:
        with pkg_resources.files(package).joinpath(xsd_name).open("rb") as f:
            raw = f.read()
            try:
                text = raw.decode("utf-8")
            except Exception:
                text = raw.decode("latin-1")
            # Corrección defensiva: eliminar espacios accidentales antes del nombre de tipo o name
            # Caso conocido: name=" IndicadorServicioTodoIncluidoType"
            text = text.replace('name=" IndicadorServicioTodoIncluidoType"', 'name="IndicadorServicioTodoIncluidoType"')
            text = text.replace('type=" IndicadorServicioTodoIncluidoType"', 'type="IndicadorServicioTodoIncluidoType"')
            # Corrección genérica: compactar espacios inmediatamente después de "name=" y "type="
            text = re.sub(r'name="\s+([A-Za-z0-9_:-]+)"', r'name="\1"', text)
            text = re.sub(r'type="\s+([A-Za-z0-9_:-]+)"', r'type="\1"', text)
            xsd_doc = etree.fromstring(text.encode("utf-8"))
            return etree.XMLSchema(xsd_doc)
    except FileNotFoundError:
        raise FileNotFoundError(f"XSD no encontrado en el paquete: {xsd_name}")


def validate_xml(xml_content: str, *, xsd_name: str) -> Tuple[bool, List[str]]:
    """Valida un XML contra un XSD del paquete.
    xsd_name: nombre del archivo XSD (por ejemplo, "e-CF 43 v.1.0.xsd").
    """
    schema = _load_xsd_schema(xsd_name)
    parser = etree.XMLParser(remove_blank_text=False)
    try:
        xml_doc = etree.fromstring(xml_content.encode("utf-8"), parser)
    except etree.XMLSyntaxError as e:
        return False, [f"XMLSyntaxError: {e}"]

    is_valid = schema.validate(xml_doc)
    if is_valid:
        return True, []

    # Recopilar errores del esquema
    errors = []
    for error in schema.error_log:
        errors.append(f"Line {error.line}, Col {error.column}: {error.message}")
    return False, errors
