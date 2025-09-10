"""
Validador de entrada basado en specs generadas desde XSD.

- Carga spec JSON desde csf_do/csf_do/specs/<name>.json
- Verifica presencia de rutas requeridas en el dict de entrada.
- Opcionalmente, normaliza fechas si el builder no lo hace (builders actuales ya normalizan).
"""
from __future__ import annotations
from typing import Dict, List
import json
import importlib.resources as pkg_resources

SPECS_DIR = "csf_do.csf_do.specs"

# Mapeo de nombres XSD -> claves en el dict de entrada
SEGMENT_MAP = {
    "Encabezado": "encabezado",
    "FechaHoraFirma": "fecha_hora_firma",
    "DetallesItems": "detalles",
    "Item": "items",
}


def _load_spec(name: str) -> Dict:
    with pkg_resources.files(SPECS_DIR).joinpath(name).open("r", encoding="utf-8") as f:
        return json.load(f)


def _norm(s: str) -> str:
    return s.replace("_", "").lower()


def _get_by_path(data: Dict, path: str):
    parts = path.split("/")
    cur = data
    for p in parts:
        if not isinstance(cur, dict):
            return None
        # aplicar mapeo de segmento si existe
        mapped = SEGMENT_MAP.get(p, p)
        # construir índice normalizado del nivel actual
        idx = { _norm(k): k for k in cur.keys() }
        key = idx.get(_norm(mapped))
        if key is None:
            return None
        cur = cur.get(key)
        # Si llegamos a una lista (items), consideramos presente si no está vacía y dejamos de descender
        if isinstance(cur, list):
            return cur if len(cur) > 0 else None
    return cur


FRIENDLY_MESSAGES = {
    "Encabezado/IdDoc/TipoeCF": "Falta el tipo de e-CF (Encabezado/IdDoc/TipoeCF)",
    "Encabezado/IdDoc/eNCF": "Falta el eNCF (Encabezado/IdDoc/eNCF)",
    "Encabezado/IdDoc/TipoPago": "Falta el TipoPago (Encabezado/IdDoc/TipoPago)",
    "Encabezado/IdDoc/TipoIngresos": "Falta el TipoIngresos (Encabezado/IdDoc/TipoIngresos)",
    "Encabezado/Emisor/RNCEmisor": "Falta el RNC del Emisor",
    "Encabezado/Emisor/RazonSocialEmisor": "Falta la Razón Social del Emisor",
    "Encabezado/Totales/MontoTotal": "Falta MontoTotal en Totales",
    "FechaHoraFirma": "Falta FechaHoraFirma",
}


def validate_against_spec(data: Dict, *, spec_name: str) -> List[str]:
    """Retorna lista de errores. Vacía si todo OK."""
    spec = _load_spec(spec_name)
    errors: List[str] = []
    for path in spec.get("required_paths", []):
        # Ignorar requerimientos que pasan por estructuras opcionales que en input tienen otra forma
        # Los builders validan por su cuenta campos de items
        if path.startswith("DetallesItems/Item/"):
            continue
        val = _get_by_path(data, path)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            errors.append(FRIENDLY_MESSAGES.get(path, f"Falta campo requerido: {path}"))
        # Arreglo especial: si la ruta es contenedor (dict) se da por presente si existe
        # La comprobación de hojas se apoya en builders y/o XSD final.
    return errors
