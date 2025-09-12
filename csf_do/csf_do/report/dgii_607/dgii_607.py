from __future__ import annotations
from typing import List, Tuple, Dict, Any
import io
import csv
import frappe
from frappe import _
from csf_do.csf_do.utils.field_validators import validate_rnc, validate_encf


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


@frappe.whitelist()
def export_csv(filters=None) -> Dict[str, Any]:
    """Genera un CSV del 607 con layout consistente DGII y validaciones básicas."""
    cols, rows = execute(filters)

    def _to_yyyymmdd(d: Any) -> str:
        if not d:
            return ""
        try:
            return frappe.utils.formatdate(d, "yyyyMMdd")
        except Exception:
            return ""

    def _infer_id_type(rnc: str) -> str:
        # 1=RNC (9), 2=Cédula (11), 3=Pasaporte/Extranjero (otro)
        s = (rnc or "").strip()
        if s.isdigit() and len(s) == 9:
            return "1"
        if s.isdigit() and len(s) == 11:
            return "2"
        return "3"

    def _num(v: Any) -> str:
        try:
            return f"{float(v or 0):.2f}"
        except Exception:
            return "0.00"

    # Layout propuesto: [TipoId, RNC/Cedula, eNCF, Fecha, Monto, ITBIS]
    headers = [
        "TipoId",
        "RncCedula",
        "eNCF",
        "Fecha",
        "Monto",
        "ITBIS",
    ]

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(headers)

    for r in rows:
        rnc = r.get("rnc") or ""
        encf = r.get("encf") or ""
        fecha = r.get("fecha")
        monto = r.get("monto")
        itbis = r.get("itbis")

        # Validaciones
        validate_rnc(rnc, field_name="RNC/Cédula")
        if encf:
            validate_encf(encf)

        writer.writerow([
            _infer_id_type(rnc),
            rnc,
            encf,
            _to_yyyymmdd(fecha),
            _num(monto),
            _num(itbis),
        ])

    content = out.getvalue()

    f = frappe._dict(filters or {})
    # Periodo YYYYMM si hay from_date; fallback a hoy
    try:
        period = frappe.utils.formatdate(f.get("from_date") or f.get("to_date") or frappe.utils.nowdate(), "yyyyMM")
    except Exception:
        period = frappe.utils.formatdate(frappe.utils.nowdate(), "yyyyMM")

    company_abbr = (f.company or "").replace(" ", "_") or "COMPANY"
    filename = f"DGII_607_{company_abbr}_{period}.csv"

    filedoc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "content": content,
        "is_private": 0,
    }).insert(ignore_permissions=True)

    return {"file_url": filedoc.file_url, "file_name": filename}
