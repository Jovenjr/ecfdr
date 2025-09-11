from __future__ import annotations
import frappe


def execute(filters=None):
    columns = [
        {"label": "Fecha", "fieldname": "creation", "fieldtype": "Datetime", "width": 160},
        {"label": "Tipo", "fieldname": "tipo_ecf", "fieldtype": "Data", "width": 80},
        {"label": "Ambiente", "fieldname": "ambiente", "fieldtype": "Data", "width": 120},
        {"label": "Estado DGII", "fieldname": "estado_dgii", "fieldtype": "Data", "width": 140},
        {"label": "Track ID", "fieldname": "track_id", "fieldtype": "Data", "width": 200},
        {"label": "Signature Hash", "fieldname": "signature_hash", "fieldtype": "Data", "width": 260},
    ]

    doctype_candidates = ["ECF Audit Log", "e-CF Audit Log", "ECF AuditLog"]
    dt = None
    for name in doctype_candidates:
        try:
            if frappe.db.table_exists(name) or frappe.get_meta(name):
                dt = name
                break
        except Exception:
            continue
    if not dt:
        return columns, []

    filters = filters or {}
    conditions = []
    values = {}
    if filters.get("from_date"):
        conditions.append("creation >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("creation <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    if filters.get("tipo_ecf"):
        conditions.append("tipo_ecf = %(tipo_ecf)s")
        values["tipo_ecf"] = filters["tipo_ecf"]
    if filters.get("estado_dgii"):
        conditions.append("estado_dgii = %(estado_dgii)s")
        values["estado_dgii"] = filters["estado_dgii"]

    where = (" where " + " and ".join(conditions)) if conditions else ""
    rows = frappe.db.sql(
        f"select creation, tipo_ecf, ambiente, estado_dgii, track_id, signature_hash from `tab{dt}` {where} order by creation desc limit 200",
        values,
        as_dict=True,
    )
    return columns, rows

from __future__ import annotations
from typing import List, Tuple
import frappe


def execute(filters=None) -> Tuple[List[dict], List[List]]:
    columns = [
        {"label": "Estado", "fieldname": "estado", "fieldtype": "Data", "width": 180},
        {"label": "Cantidad", "fieldname": "cantidad", "fieldtype": "Int", "width": 120},
    ]
    estados = [
        "Pendiente",
        "En Proceso",
        "Observado",
        "Aceptado",
        "Rechazado",
        "Anulado",
    ]
    data = []
    for est in estados:
        cnt = frappe.db.count("e-CF", {"estado_dgii": est})
        data.append({"estado": est, "cantidad": cnt})
    return columns, data


