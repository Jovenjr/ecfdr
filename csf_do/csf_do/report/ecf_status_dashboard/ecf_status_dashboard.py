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


