"""
Extractor de catálogos desde XSD (enumerations) a JSON.

Permite leer un XSD empaquetado en `csf_do/csf_do/xsd/` y extraer los valores
`<xs:enumeration value="..."/>` de un `xs:simpleType` por nombre.

Uso de ejemplo:
    from csf_do.csf_do.utils.xsd_catalog_extractor import extract_enumerations_to_json
    extract_enumerations_to_json(
        xsd_name="e-CF 43 v.1.0.xsd",
        simple_type_name="UnidadMedidaType",
        output_json_name="unidad_medida.json",
    )

Los JSON resultantes se guardan en `csf_do/csf_do/data/` para su uso en UI/validaciones.
"""
from __future__ import annotations
from typing import List, Tuple, Dict
from lxml import etree
import json
import importlib.resources as pkg_resources
import os


DATA_PACKAGE_DIR = "csf_do.csf_do.data"
XSD_PACKAGE_DIR = "csf_do.csf_do.xsd"


def _load_xsd_tree(xsd_name: str) -> etree._ElementTree:
    with pkg_resources.files(XSD_PACKAGE_DIR).joinpath(xsd_name).open("rb") as f:
        return etree.parse(f)


def extract_enumerations_with_labels(xsd_name: str, simple_type_name: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Extrae valores y etiquetas (labels) desde comentarios XML adyacentes a cada enumeración.

    Estrategia para label:
    - Si el siguiente hermano inmediato es un comentario, usar su texto.
    - Si no, y el hermano anterior es un comentario, usarlo.
    - En ausencia de comentario, usar el propio código como label.
    """
    tree = _load_xsd_tree(xsd_name)
    ns = {"xs": "http://www.w3.org/2001/XMLSchema"}
    # Seleccionar el simpleType por nombre
    type_nodes = tree.xpath(f"//xs:simpleType[@name='{simple_type_name}']", namespaces=ns)
    if not type_nodes:
        return [], []
    type_node = type_nodes[0]
    enums = type_node.xpath(".//xs:enumeration", namespaces=ns)

    values: List[str] = []
    entries: List[Dict[str, str]] = []
    for e in enums:
        code = e.get("value")
        if code is None:
            continue
        label = None
        # Comentario siguiente
        nxt = e.getnext()
        if nxt is not None and isinstance(nxt, etree._Comment):
            txt = (nxt.text or "").strip()
            if txt:
                label = txt
        # Si no hay siguiente comentario, verificar anterior
        if label is None:
            prev = e.getprevious()
            if prev is not None and isinstance(prev, etree._Comment):
                txt = (prev.text or "").strip()
                if txt:
                    label = txt
        if label is None:
            label = code
        values.append(code)
        entries.append({"code": code, "label": label})
    return values, entries


def extract_enumerations_to_json(*, xsd_name: str, simple_type_name: str, output_json_name: str) -> str:
    """Extrae enumeraciones y las guarda en `csf_do/csf_do/data/<output_json_name>`.
    Retorna la ruta absoluta del archivo generado (si es local) o el nombre del recurso.
    """
    values, entries = extract_enumerations_with_labels(xsd_name, simple_type_name)
    if not values and not entries:
        raise ValueError(f"No se encontraron enumeraciones para {simple_type_name} en {xsd_name}")

    # Resolver directorio físico del paquete de datos
    data_dir = pkg_resources.files(DATA_PACKAGE_DIR)
    # Asegurar que existe
    os.makedirs(str(data_dir), exist_ok=True)

    out_path = data_dir.joinpath(output_json_name)
    payload = {"type": simple_type_name}
    if entries:
        payload["entries"] = entries
        payload["values"] = values  # mantenemos compatibilidad
    else:
        payload["values"] = values

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return str(out_path)


if __name__ == "__main__":
    # Ejemplo rápido: generar catálogos comunes
    targets = [
        ("e-CF 43 v.1.0.xsd", "UnidadMedidaType", "unidad_medida.json"),
        ("e-CF 43 v.1.0.xsd", "TipoMonedaType", "tipo_moneda.json"),
        ("e-CF 46 v.1.0.xsd", "ProvinciaMunicipioType", "provincia_municipio.json"),
    ]
    for xsd_name, simple_type, out_name in targets:
        try:
            path = extract_enumerations_to_json(
                xsd_name=xsd_name,
                simple_type_name=simple_type,
                output_json_name=out_name,
            )
            print(f"✅ Generado catálogo {simple_type} -> {path}")
        except Exception as e:
            print(f"⚠️  No se pudo generar {simple_type} desde {xsd_name}: {e}")
