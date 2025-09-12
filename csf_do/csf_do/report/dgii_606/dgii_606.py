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


@frappe.whitelist()
def export_csv(filters=None) -> Dict[str, Any]:
    """Genera un CSV del 606 con layout extendido y validaciones básicas."""
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

    # Layout extendido propuesto DGII: incluir NCF modificado, tipo de pago e indicador de anulación
    headers = [
        "TipoId",
        "RncCedula",
        "NCF",
        "NCFModificado",
        "FechaComprobante",
        "MontoFacturado",
        "ITBISFacturado",
        "FormaPago",
        "IndicadorAnulacion",
    ]

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(headers)

    # Pre-cargar info complementaria de PI
    pi_names = [r.get("pi_name") for r in rows if r.get("pi_name")]
    extra_by_pi: Dict[str, Dict[str, Any]] = {}
    if pi_names:
        pi_extras = frappe.get_all(
            "Purchase Invoice",
            filters={"name": ["in", pi_names]},
            fields=["name", "is_return", "return_against", "docstatus"],
        )
        extra_by_pi = {x["name"]: x for x in pi_extras}

    def _get_encf_for_pi(pi_name: str) -> str:
        row = frappe.get_all("e-CF", filters={"purchase_invoice": pi_name}, fields=["encf"], limit=1)
        return (row[0]["encf"] if row and row[0].get("encf") else "")

    for r in rows:
        rnc = r.get("rnc") or ""
        ncf = r.get("ncf") or ""
        fecha = r.get("fecha")
        monto = r.get("monto")
        itbis = r.get("itbis")
        pi_name = r.get("pi_name")

        # Validaciones
        validate_rnc(rnc, field_name="RNC/Cédula")
        if ncf and len(str(ncf)) == 13:
            validate_encf(ncf)

        ex = extra_by_pi.get(pi_name, {})
        is_return = bool(ex.get("is_return"))
        return_against = ex.get("return_against")
        indicador_anulacion = "1" if int(ex.get("docstatus") or 1) == 2 else "0"

        ncf_mod = ""
        if is_return and return_against:
            ncf_mod = _get_encf_for_pi(str(return_against)) or str(return_against)

        # Forma de pago en 606 se reporta a veces por convenio; aquí dejamos "1" por defecto
        forma_pago = "1"

        writer.writerow([
            _infer_id_type(rnc),
            rnc,
            ncf,
            ncf_mod,
            _to_yyyymmdd(fecha),
            _num(monto),
            _num(itbis),
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
    filename = f"DGII_606_{company_abbr}_{period}.csv"

    filedoc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "content": content,
        "is_private": 0,
    }).insert(ignore_permissions=True)

    return {"file_url": filedoc.file_url, "file_name": filename}
