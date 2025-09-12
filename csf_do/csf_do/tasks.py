from __future__ import annotations
from typing import List, Dict

import frappe


def poll_ecf_statuses() -> None:
    """Encola consultas de estado para e-CF con estado Pendiente/En Proceso.

    Corre vía scheduler cada 10 minutos.
    """
    try:
        rows: List[Dict] = frappe.get_all(
            "e-CF",
            filters={"estado_dgii": ["in", ["Pendiente", "En Proceso"]]},
            fields=["name", "track_id"],
            limit=100,
            order_by="modified asc",
        )
        for r in rows:
            # evitar duplicar si no hay track_id, pero igual podemos intentar por si lo obtiene
            frappe.enqueue(
                "csf_do.csf_do.doctype.e_cf.e_cf._status_job",
                queue="short",
                timeout=300,
                is_async=True,
                job_name=f"scheduler-estado-ecf-{r['name']}",
                kwargs={"name": r["name"], "ambiente": "custom"},
            )
    except Exception:
        # no romper scheduler
        pass
