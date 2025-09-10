"""
Cargador de certificado digital (PKCS#12) desde ERPNext si está disponible.

- Intenta leer el Doctype "Digital Certificate" activo (campos esperados):
  - p12_path (ruta del .p12/.pfx)
  - password (si está accesible; en Frappe es Password field)
- Si Frappe no está disponible o no hay contexto de sitio, este módulo
  expone una API que retorna None y el llamador debe usar otros medios.
"""
from __future__ import annotations
from typing import Optional, Dict


def _load_from_frappe() -> Optional[Dict[str, str]]:
    try:
        import frappe  # type: ignore
    except Exception:
        return None

    try:
        # Asumimos Doctype Single o un registro marcado como Activo=1
        # Si es tabla normal, filtrar por activo
        if frappe.db.table_exists("Digital Certificate"):
            # Intento como Single
            try:
                doc = frappe.get_single("Digital Certificate")
                p12_path = getattr(doc, "p12_path", None) or getattr(doc, "file_path", None)
                password = getattr(doc, "password", None)
                activo = getattr(doc, "active", 1)
                if activo and p12_path:
                    return {"p12_path": p12_path, "password": password or ""}
            except Exception:
                # Intento como listado con campo activo
                try:
                    row = frappe.get_all(
                        "Digital Certificate",
                        filters={"active": 1},
                        fields=["name", "p12_path as p12_path", "file_path as file_path", "password"],
                        limit=1,
                    )
                    if row:
                        p12_path = row[0].get("p12_path") or row[0].get("file_path")
                        password = row[0].get("password")
                        if p12_path:
                            return {"p12_path": p12_path, "password": password or ""}
                except Exception:
                    return None
    except Exception:
        return None
    return None


def get_active_certificate() -> Optional[Dict[str, str]]:
    """Retorna {"p12_path": str, "password": str} si logró cargarlo desde Frappe; de lo contrario None."""
    return _load_from_frappe()
