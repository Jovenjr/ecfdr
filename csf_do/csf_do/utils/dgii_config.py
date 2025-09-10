"""
Cargador de configuración DGII desde el Doctype Single "DGII Configuration" si está disponible.
Devuelve un diccionario con las claves más utilizadas por el cliente DGII.

Campos esperados (flexible a nombres alternos):
- base_url_{ambiente}: str (precert, cert, prod) o base_url (genérico)
- verify_ssl: int/bool
- token_ttl_minutes: int (minutos) o ttl_token: int (segundos)
- client_id, client_secret (opcional)
- overrides opcionales de endpoints: auth_semilla_url, auth_token_url, recepcion_ecf_url, consulta_estado_url, directorio_servicios_url

Si Frappe no está disponible o el Doctype no existe, retorna None.
"""
from __future__ import annotations
from typing import Optional, Dict, Any


def get_active_dgii_config(ambiente: str = "custom") -> Optional[Dict[str, Any]]:
    try:
        import frappe  # type: ignore
    except Exception:
        return None

    # Buscar Doctype Single por nombre
    dt_name = "DGII Configuration"
    try:
        # get_single lanza si no existe
        doc = frappe.get_single(dt_name)
    except Exception:
        return None

    # Intentar mapear campos flexiblemente
    ambiente = (ambiente or "").lower()
    base_url = None
    if ambiente in ("precert", "pre", "precertificacion", "pre-cert", "pre_cert"):
        base_url = getattr(doc, "base_url_precert", None) or getattr(doc, "precert_base_url", None)
    elif ambiente in ("cert", "certificacion", "stg", "stage"):
        base_url = getattr(doc, "base_url_cert", None) or getattr(doc, "cert_base_url", None)
    elif ambiente in ("prod", "production", "produccion"):
        base_url = getattr(doc, "base_url_prod", None) or getattr(doc, "prod_base_url", None)
    # Generico
    base_url = base_url or getattr(doc, "base_url", None)

    verify_ssl = getattr(doc, "verify_ssl", 1)
    # Soportar token_ttl_minutes (preferido) o ttl_token (segundos)
    token_ttl_minutes = getattr(doc, "token_ttl_minutes", None)
    ttl_token = None
    if token_ttl_minutes is not None:
        try:
            ttl_token = int(token_ttl_minutes) * 60
        except Exception:
            ttl_token = None
    if ttl_token is None:
        ttl_token = getattr(doc, "ttl_token", 3600)

    try:
        verify_ssl_bool = bool(int(verify_ssl))
    except Exception:
        verify_ssl_bool = bool(verify_ssl)

    if not base_url:
        return None

    # Normalizar esquema mock: permitir "mock" o "mock://" y completar con el ambiente
    try:
        base_url_str = str(base_url).strip()
        if base_url_str.lower().startswith("mock"):
            if "://" not in base_url_str or base_url_str.lower() in ("mock://", "mock:///"):
                base_url_str = f"mock://{ambiente or 'custom'}"
            base_url = base_url_str
    except Exception:
        pass

    # Credenciales (opcionales)
    client_id = getattr(doc, "client_id", None)
    client_secret = getattr(doc, "client_secret", None)

    # Overrides de endpoints (opcionales)
    overrides = {
        "auth_semilla_url": getattr(doc, "auth_semilla_url", None),
        "auth_token_url": getattr(doc, "auth_token_url", None),
        "recepcion_ecf_url": getattr(doc, "recepcion_ecf_url", None),
        "consulta_estado_url": getattr(doc, "consulta_estado_url", None),
        "directorio_servicios_url": getattr(doc, "directorio_servicios_url", None),
    }

    return {
        "base_url": str(base_url),
        "verify_ssl": verify_ssl_bool,
        "ttl_token": int(ttl_token) if ttl_token else 3600,
        "client_id": client_id,
        "client_secret": client_secret,
        "overrides": {k: v for k, v in overrides.items() if v},
    }
