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
    """Genera un CSV del 607 con layout extendido y validaciones básicas."""
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

    # Layout extendido propuesto DGII: incluir NCF modificado, propina, forma de pago e indicador de anulación
    headers = [
        "TipoId",
        "RncCedula",
        "NCF",
        "NCFModificado",
        "FechaComprobante",
        "MontoFacturado",
        "ITBISFacturado",
        "PropinaLegal",
        "FormaPago",
        "IndicadorAnulacion",
    ]

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(headers)

    # Pre-cargar mapa SI -> datos necesarios (outstanding, is_return, return_against)
    si_names = [r.get("si_name") for r in rows if r.get("si_name")]
    extra_by_si: Dict[str, Dict[str, Any]] = {}
    if si_names:
        si_extras = frappe.get_all(
            "Sales Invoice",
            filters={"name": ["in", si_names]},
            fields=["name", "outstanding_amount", "is_return", "return_against", "docstatus"],
        )
        extra_by_si = {x["name"]: x for x in si_extras}

    # Para NCF modificado, buscar e-CF del documento original si aplica
    def _get_encf_for_si(si_name: str) -> str:
        row = frappe.get_all("e-CF", filters={"sales_invoice": si_name}, fields=["encf"], limit=1)
        return (row[0]["encf"] if row and row[0].get("encf") else "")

    for r in rows:
        rnc = r.get("rnc") or ""
        encf = r.get("encf") or ""
        fecha = r.get("fecha")
        monto = r.get("monto")
        itbis = r.get("itbis")
        si_name = r.get("si_name")

        # Validaciones base
        validate_rnc(rnc, field_name="RNC/Cédula")
        if encf:
            validate_encf(encf)

        ex = extra_by_si.get(si_name, {})
        is_return = bool(ex.get("is_return"))
        return_against = ex.get("return_against")
        indicador_anulacion = "1" if int(ex.get("docstatus") or 1) == 2 else "0"

        ncf_mod = ""
        if is_return and return_against:
            ncf_mod = _get_encf_for_si(str(return_against)) or str(return_against)

        forma_pago = "1"
        try:
            forma_pago = "1" if abs(float(ex.get("outstanding_amount") or 0)) < 0.01 else "2"
        except Exception:
            forma_pago = "1"

        propina = "0.00"  # no distinguimos propina legal aquí

        writer.writerow([
            _infer_id_type(rnc),
            rnc,
            encf,
            ncf_mod,
            _to_yyyymmdd(fecha),
            _num(monto),
            _num(itbis),
            propina,
            forma_pago,
            indicador_anulacion,
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

<<<<<<< Current (Your changes)
    return columns, data
=======
    return {"file_url": filedoc.file_url, "file_name": filename}
>>>>>>> Incoming (Background Agent changes)
