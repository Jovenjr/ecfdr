"""
Extractor de estructura desde XSD para generar especificaciones JSON por tipo e-CF.

Objetivo:
- Enumerar rutas de campos requeridos (minOccurs=1) dentro del elemento raíz ECF.
- Identificar campos fecha y datetime para ayudar a normalización.
- Guardar un spec JSON en csf_do/csf_do/specs/<slug>.json

Nota: Implementación heurística para los XSD e-CF 31/43 (y similares).
"""
from __future__ import annotations
from typing import Dict, List, Tuple
from lxml import etree
import json
import importlib.resources as pkg_resources
import os

XSD_PACKAGE_DIR = "csf_do.csf_do.xsd"
SPECS_DIR = "csf_do.csf_do.specs"

XS_NS = {"xs": "http://www.w3.org/2001/XMLSchema"}


def _load_xsd(xsd_name: str) -> etree._ElementTree:
    with pkg_resources.files(XSD_PACKAGE_DIR).joinpath(xsd_name).open("rb") as f:
        return etree.parse(f)


def _is_required(elem: etree._Element) -> bool:
    # minOccurs default is 1 if not present
    mo = elem.get("minOccurs")
    return mo is None or mo == "1"


def _get_type_name(elem: etree._Element) -> str | None:
    t = elem.get("type")
    return t


def _traverse_elements(node: etree._Element, base_path: str, required_paths: List[str], date_fields: List[str], datetime_fields: List[str], parent_required: bool) -> None:
    # Traverse xs:sequence children xs:element
    for el in node.xpath("./xs:sequence/xs:element", namespaces=XS_NS):
        name = el.get("name")
        if not name:
            continue
        path = f"{base_path}/{name}" if base_path else name
        required = _is_required(el)
        effective_required = parent_required and required
        tname = _get_type_name(el)

        # Identify date/datetime types by type name
        if tname == "FechaValidationType":
            date_fields.append(path)
        if tname == "DateTimeValidationType":
            datetime_fields.append(path)

        complex_type = el.find("xs:complexType", namespaces=XS_NS)
        if complex_type is not None:
            # Container element
            if effective_required:
                required_paths.append(path)
            # Traverse nested
            _traverse_elements(complex_type, path, required_paths, date_fields, datetime_fields, effective_required)
        else:
            # Leaf element
            if effective_required:
                required_paths.append(path)


def extract_spec(xsd_name: str) -> Dict:
    tree = _load_xsd(xsd_name)
    root_elts = tree.xpath("//xs:element[@name='ECF']", namespaces=XS_NS)
    if not root_elts:
        raise ValueError("No se encontró elemento raíz ECF en el XSD")
    ecf = root_elts[0]
    spec: Dict = {"required_paths": [], "date_fields": [], "datetime_fields": []}
    _traverse_elements(ecf.find("xs:complexType", namespaces=XS_NS), "", spec["required_paths"], spec["date_fields"], spec["datetime_fields"], True)
    # Unificar y ordenar
    spec["required_paths"] = sorted(set(spec["required_paths"]))
    spec["date_fields"] = sorted(set(spec["date_fields"]))
    spec["datetime_fields"] = sorted(set(spec["datetime_fields"]))
    return spec


def write_spec_json(xsd_name: str, out_name: str) -> str:
    spec = extract_spec(xsd_name)
    out_dir = pkg_resources.files(SPECS_DIR)
    os.makedirs(str(out_dir), exist_ok=True)
    out_path = out_dir.joinpath(out_name)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    return str(out_path)


if __name__ == "__main__":
    targets = [
        ("e-CF 31 v.1.0.xsd", "ecf31.json"),
        ("e-CF 32 v.1.0.xsd", "ecf32.json"),
        ("e-CF 43 v.1.0.xsd", "ecf43.json"),
    ]
    for xsd_name, out in targets:
        try:
            path = write_spec_json(xsd_name, out)
            print(f"✅ Spec generado: {xsd_name} -> {path}")
        except Exception as e:
            print(f"⚠️  No se pudo generar spec para {xsd_name}: {e}")
