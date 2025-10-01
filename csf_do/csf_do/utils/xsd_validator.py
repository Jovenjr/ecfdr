"""Validador XSD para DGII e-CF con resolución dinámica de versión.

Uso básico::

    from csf_do.csf_do.utils.xsd_validator import validate_xml
    ok, errors = validate_xml(xml_string, schema_id="e-CF 43")

Características:
- Descubre automáticamente los XSD disponibles en `csf_do/csf_do/xsd/`.
- Soporta especificar `schema_id` (e.g. ``"e-CF 43"``) y selecciona la versión
  más reciente (`v.X.Y.xsd`) o una versión puntual (`version="1.0"`).
- Aplica *caching* de esquemas XSD para evitar recargas repetitivas.
- Permite seguir usando `xsd_name="e-CF 43 v.1.0.xsd"` para compatibilidad.
- Ejecuta reglas adicionales DGII después de la validación XSD.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from datetime import datetime
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Tuple

import importlib.resources as pkg_resources
from lxml import etree

__all__ = [
    "validate_xml",
    "list_available_schemas",
    "resolve_xsd_filename",
    "clear_schema_cache",
]

_XSD_PACKAGE = "csf_do.csf_do.xsd"
_NAME_VERSION_RE = re.compile(r"^(?P<name>.+?)\s+v\.?\s*(?P<version>[0-9][0-9._-]*)$", re.IGNORECASE)


@dataclass(frozen=True)
class SchemaInfo:
    key: str
    version: Optional[str]
    filename: str


_SCHEMA_CACHE: Dict[str, etree.XMLSchema] = {}


def _extract_schema_key(filename: str) -> SchemaInfo:
    base = filename.rsplit(".", 1)[0]
    match = _NAME_VERSION_RE.match(base)
    if match:
        name = match.group("name").strip()
        version = match.group("version").strip()
        return SchemaInfo(key=name, version=version, filename=filename)
    return SchemaInfo(key=base.strip(), version=None, filename=filename)


def _version_sort_key(version: Optional[str]) -> Tuple:
    if version is None:
        return ()
    parts: List = []
    for token in re.split(r"[._-]", version):
        if token.isdigit():
            parts.append(int(token))
        else:
            parts.append(token.lower())
    return tuple(parts)


@lru_cache(maxsize=1)
def _discover_schemas() -> Dict[str, List[SchemaInfo]]:
    registry: Dict[str, List[SchemaInfo]] = {}
    package_root = pkg_resources.files(_XSD_PACKAGE)
    for entry in package_root.iterdir():
        if not entry.name.lower().endswith(".xsd"):
            continue
        info = _extract_schema_key(entry.name)
        registry.setdefault(info.key.lower(), []).append(info)

    for infos in registry.values():
        infos.sort(key=lambda i: _version_sort_key(i.version), reverse=True)
    return registry


def list_available_schemas() -> Dict[str, List[str]]:
    """Regresa las versiones disponibles por «schema_id».

    Returns:
        dict: {"e-cf 31": ["1.0"], ...}
    """

    discovered = _discover_schemas()
    output: Dict[str, List[str]] = {}
    for key, infos in discovered.items():
        output[key] = [info.version for info in infos if info.version]
    return output


def resolve_xsd_filename(schema_id: str, version: Optional[str] = None) -> str:
    """Obtiene el nombre del archivo XSD para *schema_id*.

    - ``schema_id`` puede ser "e-CF 31", "e-CF 31 v.1.0" o el nombre completo
      del archivo.
    - Si `version` es `None`, se selecciona la versión más reciente.
    """

    schema_id = schema_id.strip()
    if schema_id.lower().endswith(".xsd"):
        return schema_id

    # Permitir que schema_id ya incluya versión al estilo "e-CF 31 v.1.0"
    extracted = _extract_schema_key(f"{schema_id}.xsd")
    key = extracted.key.lower()
    explicit_version = version or extracted.version

    registry = _discover_schemas()
    infos = registry.get(key)
    if not infos:
        raise FileNotFoundError(f"No se encontró un XSD registrado para '{schema_id}'.")

    if explicit_version:
        normalized_version = explicit_version.strip().lower()
        for info in infos:
            if info.version and info.version.lower() == normalized_version:
                return info.filename
        raise FileNotFoundError(
            f"No se encontró versión '{explicit_version}' para el esquema '{schema_id}'."
        )

    return infos[0].filename


def clear_schema_cache() -> None:
    """Limpia el cache de esquemas cargados."""

    _SCHEMA_CACHE.clear()
    _discover_schemas.cache_clear()  # type: ignore[attr-defined]


def _load_xsd_schema(filename: str) -> etree.XMLSchema:
    if filename in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[filename]

    package = _XSD_PACKAGE
    try:
        with pkg_resources.files(package).joinpath(filename).open("rb") as handle:
            raw = handle.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"XSD no encontrado en el paquete: {filename}") from exc

    try:
        text = raw.decode("utf-8")
    except Exception:
        text = raw.decode("latin-1")

    text = text.replace('name=" IndicadorServicioTodoIncluidoType"', 'name="IndicadorServicioTodoIncluidoType"')
    text = text.replace('type=" IndicadorServicioTodoIncluidoType"', 'type="IndicadorServicioTodoIncluidoType"')
    text = re.sub(r'name="\s+([A-Za-z0-9_:-]+)"', r'name="\1"', text)
    text = re.sub(r'type="\s+([A-Za-z0-9_:-]+)"', r'type="\1"', text)

    xsd_doc = etree.fromstring(text.encode("utf-8"))
    schema = etree.XMLSchema(xsd_doc)
    _SCHEMA_CACHE[filename] = schema
    return schema


def _apply_additional_rules(root: etree._Element, schema_key: Optional[str]) -> List[str]:
    errors: List[str] = []
    if schema_key and schema_key.lower().startswith("e-cf"):
        signature_el = root.find(".//Signature")
        if signature_el is None or not (signature_el.text or "").strip():
            errors.append("Signature: no debe estar vacío.")

        fecha_firma = root.findtext(".//FechaHoraFirma")
        if fecha_firma:
            normalized = fecha_firma.strip()
            # formatos permitidos: dd-mm-yyyy HH:MM:SS o ISO (fallback)
            parse_ok = False
            for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    datetime.strptime(normalized, fmt)
                    parse_ok = True
                    break
                except ValueError:
                    continue
            if not parse_ok:
                errors.append("FechaHoraFirma: formato inválido, se espera 'DD-MM-YYYY HH:MM:SS'.")

    return errors


def validate_xml(
    xml_content: str,
    *,
    schema_id: Optional[str] = None,
    version: Optional[str] = None,
    xsd_name: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """Valida `xml_content` contra un XSD del paquete.

    Args:
        xml_content: Contenido XML en UTF-8.
        schema_id: Identificador lógico (ej. "e-CF 43").
        version: Versión específica cuando se usa ``schema_id``.
        xsd_name: Nombre explícito del archivo (compatibilidad).
    """

    if not schema_id and not xsd_name:
        raise ValueError("Debe especificar 'schema_id' o 'xsd_name'.")

    if schema_id and xsd_name:
        raise ValueError("Use solo uno de los parámetros: 'schema_id' o 'xsd_name'.")

    filename = xsd_name or resolve_xsd_filename(schema_id, version)  # type: ignore[arg-type]
    schema_info = _extract_schema_key(filename)
    schema = _load_xsd_schema(filename)

    parser = etree.XMLParser(remove_blank_text=False)
    try:
        xml_doc = etree.fromstring(xml_content.encode("utf-8"), parser)
    except etree.XMLSyntaxError as exc:
        return False, [f"XMLSyntaxError: {exc}"]

    is_valid = schema.validate(xml_doc)
    additional_errors = _apply_additional_rules(xml_doc, schema_info.key)

    if is_valid and not additional_errors:
        return True, []

    errors: List[str] = []
    if not is_valid:
        for error in schema.error_log:
            errors.append(f"Line {error.line}, Col {error.column}: {error.message}")

    errors.extend(additional_errors)
    return False, errors
