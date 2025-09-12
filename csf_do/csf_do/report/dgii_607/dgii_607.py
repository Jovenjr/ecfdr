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
            (SI.name).as_("si_name"),
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

    if not data:
        return columns, []

    # Mapear e-NCF desde doctype e-CF vinculado a la Sales Invoice (si existe)
    si_names = [r.get("si_name") for r in data if r.get("si_name")]
    encf_by_si: Dict[str, str] = {}
    if si_names:
        ecf_rows = frappe.get_all(
            "e-CF",
            filters={"sales_invoice": ["in", si_names]},
            fields=["sales_invoice", "encf", "modified"],
            order_by="modified desc",
        )
        for ecf in ecf_rows:
            si = ecf.get("sales_invoice")
            if si and si not in encf_by_si and ecf.get("encf"):
                encf_by_si[si] = ecf.get("encf")

    # Cargar impuestos de ITBIS por factura
    itbis_by_si: Dict[str, float] = {}
    if si_names:
        tax_rows = frappe.get_all(
            "Sales Taxes and Charges",
            filters={"parenttype": "Sales Invoice", "parent": ["in", si_names]},
            fields=["parent", "description", "account_head", "base_tax_amount"],
        )
        for tr in tax_rows:
            parent = tr.get("parent")
            desc = (tr.get("description") or "").upper()
            acc = (tr.get("account_head") or "").upper()
            if "ITBIS" in desc or "ITBIS" in acc:
                itbis_by_si[parent] = itbis_by_si.get(parent, 0.0) + float(tr.get("base_tax_amount") or 0.0)

    # Completar filas: e-NCF + ITBIS (con respaldo por diferencia)
    for row in data:
        si_name = row.get("si_name")
        row["encf"] = encf_by_si.get(si_name)
        base_total = float(row.get("monto") or 0)
        net = float(frappe.db.get_value("Sales Invoice", si_name, "base_net_total") or 0)
        diff_itbis = max(base_total - net, 0.0)
        calc_itbis = itbis_by_si.get(si_name, 0.0)
        row["itbis"] = calc_itbis if calc_itbis > 0 else diff_itbis

    return columns, data
