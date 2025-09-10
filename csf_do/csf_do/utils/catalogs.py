"""
Utilidades para cargar catálogos (entries/values) generados desde XSD.

- Lee JSON desde el paquete `csf_do.csf_do.data`.
- Expone funciones para UI (entries con code/label) y validación (values).
"""
from __future__ import annotations
from typing import List, Dict, Tuple
import json
import importlib.resources as pkg_resources

DATA_PKG = "csf_do.csf_do.data"


def load_catalog(name: str) -> Dict:
    """Carga un catálogo JSON por nombre de archivo (p. ej., "provincia_municipio.json")."""
    with pkg_resources.files(DATA_PKG).joinpath(name).open("r", encoding="utf-8") as f:
        return json.load(f)


def get_entries(name: str) -> List[Dict[str, str]]:
    """Retorna lista de entries [{code,label}]. Si no existen, deriva entries desde values.
    """
    payload = load_catalog(name)
    entries = payload.get("entries")
    if entries is not None:
        return entries  # ya vienen con code/label
    # Derivar desde values si no hay entries
    vals = payload.get("values", [])
    return [{"code": str(v), "label": str(v)} for v in vals]


def get_values(name: str) -> List[str]:
    """Retorna la lista de valores (codes) para validaciones.
    """
    payload = load_catalog(name)
    vals = payload.get("values")
    if vals is not None:
        return [str(v) for v in vals]
    # Derivar desde entries si "values" no está presente
    entries = payload.get("entries", [])
    return [str(e.get("code")) for e in entries if e.get("code") is not None]
