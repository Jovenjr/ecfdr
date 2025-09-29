"""Utilities to download DGII catalogs and persist them for ERPNext usage.

This module fetches catalog JSON/CSV files from the DGII services, storing
normalized JSON copies under the site's private folder so that builders and
validators can reference up-to-date values.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, Optional

import frappe

from csf_do.csf_do.utils.dgii_client import DGIIClient
from csf_do.csf_do.utils.dgii_config import get_active_dgii_config

try:  # pragma: no cover - requests may be absent in some environments
    import requests  # type: ignore

    _HAS_REQUESTS = True
except Exception:  # pragma: no cover
    requests = None  # type: ignore
    _HAS_REQUESTS = False

LOGGER = logging.getLogger(__name__)

CATALOG_SPECS: Dict[str, Dict[str, str]] = {
    "monedas": {"path": "/catalogos/monedas", "filename": "monedas.json"},
    "unidades_medida": {"path": "/catalogos/unidadesmedida", "filename": "unidades_medida.json"},
    "provincias_municipios": {"path": "/catalogos/provinciasmunicipios", "filename": "provincias_municipios.json"},
    "tipos_ingresos": {"path": "/catalogos/tiposingresos", "filename": "tipos_ingresos.json"},
    "tipos_comprobante": {"path": "/catalogos/tiposcomprobante", "filename": "tipos_comprobante.json"},
    "formas_pago": {"path": "/catalogos/formaspago", "filename": "formas_pago.json"},
    "impuestos_adicionales": {"path": "/catalogos/impuestos", "filename": "impuestos_adicionales.json"},
}


def sync_catalogs(*, ambiente: str = "precert", names: Optional[Iterable[str]] = None) -> Dict[str, Path]:
    """Download catalog data from DGII and persist as JSON files.

    Parameters
    ----------
    ambiente: str
        Which DGII environment to query (``precert``, ``cert`` or ``prod``).
    names: Iterable[str] | None
        Catalog identifiers to refresh. When ``None`` all known catalogs are fetched.

    Returns
    -------
    Dict[str, Path]
        Mapping catalog name -> local file path written.
    """
    if not _HAS_REQUESTS:
        raise RuntimeError("La librería requests es requerida para sincronizar catálogos.")

    cfg = get_active_dgii_config(ambiente=ambiente)
    if not cfg:
        raise RuntimeError("No se encontró configuración DGII activa para sincronizar catálogos.")

    client = DGIIClient.from_configuration(ambiente=ambiente)
    if not client:
        raise RuntimeError("No fue posible instanciar el cliente DGII para sincronizar catálogos.")

    results: Dict[str, Path] = {}
    catalog_names = list(names or CATALOG_SPECS.keys())
    base_url = cfg["base_url"].rstrip("/")
    cache_dir = Path(frappe.get_site_path("private", "dgii_catalogs"))
    cache_dir.mkdir(parents=True, exist_ok=True)

    for name in catalog_names:
        spec = CATALOG_SPECS.get(name)
        if not spec:
            LOGGER.warning("Catálogo desconocido: %s", name)
            continue

        url = f"{base_url}{spec['path']}"
        try:
            resp = requests.get(url, timeout=int(cfg.get("timeout_seconds", 30) or 30), verify=bool(cfg.get("verify_ssl", True)))
            resp.raise_for_status()
            payload = _normalize_catalog_payload(resp)
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("No se pudo descargar catálogo %s: %s", name, exc)
            continue

        target = cache_dir / spec["filename"]
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        LOGGER.info("Catálogo DGII sincronizado: %s -> %s", name, target)
        results[name] = target

    return results


def _normalize_catalog_payload(response: "requests.Response") -> Dict[str, object]:
    """Return payload in JSON form whatever the DGII response content type is."""
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type.lower():
        return response.json()
    # Simple CSV-like formats can be converted to arrays of values.
    text = response.text.strip()
    if text.startswith("<"):
        # XML -> leave raw so that consumers can parse later
        return {"raw": text}
    rows = [row.split(";") for row in text.splitlines() if row]
    return {"values": rows}
*** End Patch
