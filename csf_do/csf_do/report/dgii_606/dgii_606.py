from __future__ import annotations
from typing import List, Tuple, Dict, Any
import frappe
from frappe import _


def execute(filters=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    f = frappe._dict(filters or {})

    columns = [
        {"label": _("RNC Proveedor"), "fieldname": "rnc", "fieldtype": "Data", "width": 140},
        {"label": _("Nombre Proveedor"), "fieldname": "nombre", "fieldtype": "Data", "width": 220},
        {"label": _("Fecha Factura"), "fieldname": "fecha", "fieldtype": "Date", "width": 110},
        {"label": _("NCF"), "fieldname": "ncf", "fieldtype": "Data", "width": 160},
        {"label": _("Monto Factura"), "fieldname": "monto", "fieldtype": "Currency", "width": 130},
        {"label": _("ITBIS"), "fieldname": "itbis", "fieldtype": "Currency", "width": 110},
    ]

    q = frappe.qb
    PI = q.DocType("Purchase Invoice")
    SUP = q.DocType("Supplier")

    query = (
        q.from_(PI)
        .inner_join(SUP)
        .on(PI.supplier == SUP.name)
        .select(
            (SUP.tax_id).as_("rnc"),
            (PI.supplier_name).as_("nombre"),
            (PI.posting_date).as_("fecha"),
            (PI.name).as_("ncf"),
            (PI.base_grand_total).as_("monto"),
        )
        .where(PI.docstatus == 1)
    )

    if f.company:
        query = query.where(PI.company == f.company)
    if f.from_date:
        query = query.where(PI.posting_date >= f.from_date)
    if f.to_date:
        query = query.where(PI.posting_date <= f.to_date)

    data = query.run(as_dict=True)

    # ITBIS básico: diferencia entre total y neto si está disponible
    for row in data:
        base_total = row.get("monto") or 0
        net = frappe.db.get_value("Purchase Invoice", row["ncf"], "base_net_total") or 0
        row["itbis"] = max(base_total - net, 0)

    return columns, data
