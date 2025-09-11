from __future__ import annotations
import frappe


def run() -> None:
    """Consulta periódicamente estados en DGII para e-CF en proceso o pendiente.

    - Busca documentos `e-CF` con `estado_dgii` en (Pendiente, En Proceso)
      y con `track_id` definido, actualiza su estado consultando a DGII.
    - Si no hay `track_id`, lo omite (podría estar recién encolado).
    """
    estados = ["Pendiente", "En Proceso"]
    rows = frappe.get_all(
        "e-CF",
        filters={"estado_dgii": ["in", estados]},
        fields=["name", "track_id"],
        limit=100,
        order_by="modified asc",
    )
    for row in rows:
        if not row.get("track_id"):
            continue
        try:
            frappe.call(
                "csf_do.csf_do.doctype.e_cf.e_cf.consultar_estado",
                name=row["name"],
                ambiente="custom",
            )
        except Exception as e:  # noqa: BLE001
            frappe.logger().warning(f"Auto-consulta DGII fallo para {row['name']}: {e}")

    # Monitoreo básico: expiración de certificados digitales (si el Doctype existe)
    try:
        if frappe.db.table_exists("Digital Certificate"):
            certs = frappe.get_all(
                "Digital Certificate",
                filters={"is_active": 1},
                fields=["name", "valid_to"],
            ) or []
            from datetime import datetime, timedelta
            now = datetime.now().date()
            for c in certs:
                vt = c.get("valid_to")
                if vt:
                    try:
                        days = (vt - now).days  # type: ignore[operator]
                        if days <= 30:
                            frappe.log_error(
                                title="Alerta: Certificado por expirar",
                                message=f"Certificado {c['name']} expira en {days} días",
                            )
                    except Exception:
                        pass
    except Exception:
        pass


