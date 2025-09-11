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
                # Soportar distintos esquemas de campos según el Doctype
                is_active = getattr(doc, "is_active", None)
                active = getattr(doc, "active", None)
                activo = is_active if is_active is not None else (active if active is not None else 1)
                # Priorizar ruta PKCS#12 si existe en cert_path o p12_path
                p12_path = (
                    getattr(doc, "p12_path", None)
                    or getattr(doc, "cert_path", None)
                    or getattr(doc, "file_path", None)
                )
                password = getattr(doc, "password", None)
                if activo and p12_path:
                    return {"p12_path": p12_path, "password": password or ""}
            except Exception:
                # Intento como listado con campo activo
                try:
                    # Intento flexible: campos is_active/active y cert_path/p12_path/file_path
                    row = frappe.get_all(
                        "Digital Certificate",
                        filters={"is_active": 1},
                        fields=["name", "p12_path", "cert_path", "file_path", "password"],
                        limit=1,
                    ) or frappe.get_all(
                        "Digital Certificate",
                        filters={"active": 1},
                        fields=["name", "p12_path", "cert_path", "file_path", "password"],
                        limit=1,
                    )
                    if row:
                        p12_path = row[0].get("p12_path") or row[0].get("cert_path") or row[0].get("file_path")
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
