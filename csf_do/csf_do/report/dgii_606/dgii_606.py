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
            (PI.name).as_("pi_name"),
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

    if not data:
        return columns, []

    # Mapear NCF desde doctype e-CF vinculado a la Purchase Invoice (si existiera para recepción e-CF)
    pi_names = [r.get("pi_name") for r in data if r.get("pi_name")]
    encf_by_pi: Dict[str, str] = {}
    if pi_names:
        ecf_rows = frappe.get_all(
            "e-CF",
            filters={"purchase_invoice": ["in", pi_names]},
            fields=["purchase_invoice", "encf", "modified"],
            order_by="modified desc",
        )
        for ecf in ecf_rows:
            pi = ecf.get("purchase_invoice")
            if pi and pi not in encf_by_pi and ecf.get("encf"):
                encf_by_pi[pi] = ecf.get("encf")

    # Cargar impuestos ITBIS por factura de compra
    itbis_by_pi: Dict[str, float] = {}
    if pi_names:
        tax_rows = frappe.get_all(
            "Purchase Taxes and Charges",
            filters={"parenttype": "Purchase Invoice", "parent": ["in", pi_names]},
            fields=["parent", "description", "account_head", "base_tax_amount"],
        )
        for tr in tax_rows:
            parent = tr.get("parent")
            desc = (tr.get("description") or "").upper()
            acc = (tr.get("account_head") or "").upper()
            if "ITBIS" in desc or "ITBIS" in acc:
                itbis_by_pi[parent] = itbis_by_pi.get(parent, 0.0) + float(tr.get("base_tax_amount") or 0.0)

    # Completar filas: preferir e-NCF si existe, de lo contrario usar nombre PI como NCF; ITBIS por suma o diferencia
    for row in data:
        pi_name = row.get("pi_name")
        # Si hubo recepción e-CF, usamos el e-NCF como referencia
        row["ncf"] = encf_by_pi.get(pi_name) or pi_name
        base_total = float(row.get("monto") or 0)
        net = float(frappe.db.get_value("Purchase Invoice", pi_name, "base_net_total") or 0)
        diff_itbis = max(base_total - net, 0.0)
        calc_itbis = itbis_by_pi.get(pi_name, 0.0)
        row["itbis"] = calc_itbis if calc_itbis > 0 else diff_itbis

    return columns, data
