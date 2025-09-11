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


