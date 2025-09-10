"""
Utilidad para registrar eventos del e-CF en el Doctype de auditoría (si está disponible).

- Intenta usar el Doctype "ECF Audit Log" (basado en la carpeta doctype `ecf_audit_log/`).
- Si Frappe no está disponible o el Doctype/campos no existen, hace fallback a `frappe.log_error` o no hace nada.

Campos sugeridos a registrar (cuando existan):
- tipo_ecf: str (por ejemplo, "31", "32", "43")
- ambiente: str (base_url del servicio DGII)
- estado_dgii: str (por ejemplo, "Construido", "Firmado", "Enviado", "Recibido", etc.)
- track_id: str | None
- signature_hash: str | None
- codigo_seguridad: str | None
- payload_hash: str | None (hash del XML firmado)
- errores: list[str] | None
- extra: JSON con datos adicionales opcionales
"""
from __future__ import annotations
from typing import Any, Dict, Optional


_DOCTYPE_CANDIDATES = [
    "ECF Audit Log",  # más probable por el nombre de la carpeta `ecf_audit_log`
    "e-CF Audit Log",
    "ECF AuditLog",
]


def save_audit_event(event: Dict[str, Any]) -> None:
    """Persiste un evento de auditoría si Frappe y el Doctype están disponibles.

    Este método es best-effort: nunca debe lanzar excepción hacia el llamador.
    """
    try:
        import frappe  # type: ignore
    except Exception:
        return  # fuera de contexto Frappe

    try:
        doctype_name: Optional[str] = None
        for name in _DOCTYPE_CANDIDATES:
            try:
                if frappe.db.table_exists(name):
                    doctype_name = name
                    break
                # `table_exists` puede no funcionar para Singles, probar get_meta
                frappe.get_meta(name)  # puede lanzar si no existe
                doctype_name = name
                break
            except Exception:
                continue
        if not doctype_name:
            # No existe el doctype esperado: registrar como log de error para trazabilidad mínima
            try:
                frappe.log_error(title="ECF Audit (doctype missing)", message=str(event))
            except Exception:
                pass
            return

        # Intentar mapear sólo campos existentes en el DocType
        try:
            meta = frappe.get_meta(doctype_name)
            fieldnames = {f.fieldname for f in getattr(meta, "fields", [])}
        except Exception:
            fieldnames = set()

        doc = frappe.new_doc(doctype_name)

        # Mapeo directo de campos comunes si existen
        mappings = {
            "tipo_ecf": "tipo_ecf",
            "ambiente": "ambiente",
            "estado_dgii": "estado_dgii",
            "track_id": "track_id",
            "signature_hash": "signature_hash",
            "codigo_seguridad": "codigo_seguridad",
            "payload_hash": "payload_hash",
            "errores": "errores",  # en Frappe puede ser Text o JSON; si es tabla, este set no aplicará
        }
        for src, target in mappings.items():
            if src in event and (not fieldnames or target in fieldnames):
                try:
                    doc.set(target, event[src])
                except Exception:
                    pass

        # Guardar el evento completo como JSON en un campo generico si existe
        for generic_field in ("raw", "payload", "data", "extra"):
            if (not fieldnames or generic_field in fieldnames):
                try:
                    doc.set(generic_field, event)
                    break
                except Exception:
                    continue

        # Insertar ignorando permisos, commit best-effort
        try:
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            try:
                frappe.log_error(title="ECF Audit (insert failed)", message=str(event))
            except Exception:
                pass
    except Exception:
        # Nunca propagamos errores de auditoría
        try:
            frappe.log_error(title="ECF Audit (unexpected)", message=str(event))
        except Exception:
            pass
