from __future__ import annotations
from typing import List, Tuple, Dict, Any
import frappe
from frappe import _


def execute(filters=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    f = frappe._dict(filters or {})

    columns = [
        {"label": _("RNC Cliente"), "fieldname": "rnc", "fieldtype": "Data", "width": 140},
        {"label": _("Nombre Cliente"), "fieldname": "nombre", "fieldtype": "Data", "width": 220},
        {"label": _("Fecha Factura"), "fieldname": "fecha", "fieldtype": "Date", "width": 110},
        {"label": _("e-NCF"), "fieldname": "encf", "fieldtype": "Data", "width": 160},
        {"label": _("Monto Factura"), "fieldname": "monto", "fieldtype": "Currency", "width": 130},
        {"label": _("ITBIS"), "fieldname": "itbis", "fieldtype": "Currency", "width": 110},
    ]

    q = frappe.qb
    SI = q.DocType("Sales Invoice")
    CUS = q.DocType("Customer")

    query = (
        q.from_(SI)
        .inner_join(CUS)
        .on(SI.customer == CUS.name)
        .select(
            (CUS.tax_id).as_("rnc"),
            (SI.customer_name).as_("nombre"),
            (SI.posting_date).as_("fecha"),
            (SI.name).as_("encf"),
            (SI.base_grand_total).as_("monto"),
        )
        .where(SI.docstatus == 1)
    )

    if f.company:
        query = query.where(SI.company == f.company)
    if f.from_date:
        query = query.where(SI.posting_date >= f.from_date)
    if f.to_date:
        query = query.where(SI.posting_date <= f.to_date)

    data = query.run(as_dict=True)

    for row in data:
        base_total = row.get("monto") or 0
        net = frappe.db.get_value("Sales Invoice", row["encf"], "base_net_total") or 0
        row["itbis"] = max(base_total - net, 0)

    return columns, data
