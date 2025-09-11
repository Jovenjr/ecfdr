from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, List
from frappe.rate_limiter import rate_limit

import frappe


@frappe.whitelist()
@rate_limit(key="user", limit=30, seconds=60)
def enviar_ecf(name: str, tipo: str, data: Dict | None = None, ambiente: str = "custom") -> Dict[str, Any]:
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.enviar",
        name=name,
        tipo=tipo,
        data=data,
        ambiente=ambiente,
    )


@frappe.whitelist()
@rate_limit(key="user", limit=60, seconds=60)
def consultar_estado(name: str, ambiente: str = "custom") -> Dict[str, Any]:
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.consultar_estado",
        name=name,
        ambiente=ambiente,
    )


@frappe.whitelist()
@rate_limit(key="user", limit=10, seconds=60)
def anular_encf(name: str, motivo: str | None = None) -> Dict[str, Any]:
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.anular",
        name=name,
        motivo=motivo,
    )


 

# ---- NUEVOS ENDPOINTS: Sales Invoice -> e-CF ----

def _get_next_encf_for_tipo(tipo: str) -> Tuple[str, Optional[str]]:
    """Genera el siguiente eNCF usando `e-CF Sequence` para el tipo indicado.

    Retorna (encf, sequence_name). Lanza si no hay secuencia disponible.
    Formato: Serie (E/B) + Tipo (2 dígitos) + correlativo 10 dígitos => 13 chars
    """
    sequences: List[Dict[str, Any]] = frappe.get_all(
        "e-CF Sequence",
        filters={"sequence_type": ["like", f"{str(tipo)}%"], "serie": ["in", ["E", "B"]]},
        fields=["name", "sequence_type", "serie", "range_from", "range_to", "current"],
        order_by="serie asc, modified asc",
    )
    if not sequences:
        raise frappe.ValidationError("No hay secuencias configuradas para el tipo e-CF indicado")
    for seq in sequences:
        current = int(seq.get("current") or 0)
        range_to = int(seq.get("range_to") or 0)
        next_num = current + 1
        if next_num <= range_to:
            # actualizar current de forma optimista
            frappe.db.set_value("e-CF Sequence", seq["name"], "current", next_num)
            encf = f"{seq['serie']}{str(tipo).zfill(2)}{next_num:010d}"
            return encf, seq["name"]
    raise frappe.ValidationError("Secuencias agotadas para el tipo e-CF indicado")


def _build_ecf32_from_sales_invoice(si: Dict[str, Any], encf: str) -> Dict[str, Any]:
    """Construye payload mínimo válido para e-CF 32 a partir de Sales Invoice.

    Aplica defaults razonables donde no haya datos en ERPNext.
    """
    company = si.get("company")
    customer = si.get("customer")
    posting_date = si.get("posting_date")
    items = si.get("items") or []

    # Emisor
    rnc_emisor = frappe.get_cached_value("Company", company, "tax_id")
    razon_emisor = frappe.get_cached_value("Company", company, "company_name")
    direccion_emisor = frappe.get_cached_value("Company", company, "address") if frappe.db.has_column("Company", "address") else "-"

    # Comprador (si no tiene RNC, se asumirá CONSUMIDOR FINAL en builder)
    rnc_comprador = frappe.get_cached_value("Customer", customer, "tax_id") if customer else None
    razon_comprador = si.get("customer_name") or customer

    # Totales e ítems
    detalle_items: List[Dict[str, Any]] = []
    sum_items = 0.0
    for idx, it in enumerate(items, start=1):
        qty = float(it.get("qty") or 0)
        rate = float(it.get("rate") or 0)
        amount = float(it.get("amount") or qty * rate)
        sum_items += amount
        detalle_items.append(
            {
                "NumeroLinea": str(idx),
                "IndicadorFacturacion": "1",  # por defecto gravado
                "NombreItem": it.get("item_name") or it.get("item_code") or "ITEM",
                "IndicadorBienoServicio": "1",  # 1 = Bien
                "CantidadItem": f"{qty:.2f}",
                "PrecioUnitarioItem": f"{rate:.4f}",
                "MontoItem": f"{amount:.2f}",
                "DescripcionItem": (it.get("description") or "")[:120],
            }
        )

    # TipoPago: contado si no hay saldo pendiente
    outstanding = float(si.get("outstanding_amount") or 0)
    tipo_pago = "1" if abs(outstanding) < 0.01 else "2"

    data = {
        "encabezado": {
            "Version": "1.0",
            "IdDoc": {
                "TipoeCF": "32",
                "eNCF": encf,
                "TipoIngresos": "1",
                "TipoPago": tipo_pago,
            },
            "Emisor": {
                "RNCEmisor": rnc_emisor,
                "RazonSocialEmisor": razon_emisor,
                "DireccionEmisor": direccion_emisor or "-",
                "FechaEmision": str(posting_date),
            },
            "Comprador": {
                "RNCComprador": rnc_comprador,
                "RazonSocialComprador": razon_comprador,
            },
            "Totales": {
                "MontoTotal": f"{sum_items:.2f}",
            },
        },
        "detalles": {"items": detalle_items},
        "fecha_hora_firma": frappe.utils.now(),
    }
    return data


def _ensure_ecf_for_sales_invoice(si_name: str, tipo: str = "32") -> Tuple[str, Dict[str, Any]]:
    """Busca o crea un Doc e-CF vinculado a la Sales Invoice.

    Retorna (ecf_name, payload_data_minima).
    """
    # Buscar existente
    existing = frappe.get_all(
        "e-CF",
        filters={"sales_invoice": si_name, "tipo_ecf": str(tipo)},
        fields=["name", "encf"],
        limit=1,
    )
    if existing:
        ecf_name = existing[0]["name"]
        ecf_doc = frappe.get_doc("e-CF", ecf_name)
        # si no tiene encf, asignar uno ahora
        encf_val = ecf_doc.encf
        if not encf_val:
            encf_val, seq_name = _get_next_encf_for_tipo(tipo)
            ecf_doc.encf = encf_val
            if seq_name:
                ecf_doc.sequence = seq_name
            ecf_doc.save(ignore_permissions=True)
        # construir payload mínimo desde SI
        si = frappe.get_doc("Sales Invoice", si_name).as_dict()
        data = _build_ecf32_from_sales_invoice(si, encf_val)
        return ecf_name, data

    # Crear nuevo
    encf_val, seq_name = _get_next_encf_for_tipo(tipo)
    si = frappe.get_doc("Sales Invoice", si_name)
    ecf_doc = frappe.get_doc(
        {
            "doctype": "e-CF",
            "estado_dgii": "Pendiente",
            "tipo_ecf": str(tipo),
            "encf": encf_val,
            "sales_invoice": si_name,
            "rnc_emisor": frappe.get_cached_value("Company", si.company, "tax_id"),
            "rnc_comprador": frappe.get_cached_value("Customer", si.customer, "tax_id") if si.customer else None,
            "sequence": seq_name,
        }
    )
    ecf_doc.insert(ignore_permissions=True)
    data = _build_ecf32_from_sales_invoice(si.as_dict(), encf_val)
    return ecf_doc.name, data


@frappe.whitelist()
@rate_limit(key="user", limit=30, seconds=60)
def enviar_ecf_desde_sales_invoice(name: str, tipo: str = "32", ambiente: str = "custom") -> Dict[str, Any]:
    ecf_name, data = _ensure_ecf_for_sales_invoice(name, tipo)
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.enviar",
        name=ecf_name,
        tipo=tipo,
        data=data,
        ambiente=ambiente,
    )


@frappe.whitelist()
@rate_limit(key="user", limit=60, seconds=60)
def consultar_estado_desde_sales_invoice(name: str, ambiente: str = "custom") -> Dict[str, Any]:
    row = frappe.get_all("e-CF", filters={"sales_invoice": name}, fields=["name"], limit=1)
    if not row:
        frappe.throw("No existe un e-CF vinculado a esta Sales Invoice")
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.consultar_estado",
        name=row[0]["name"],
        ambiente=ambiente,
    )


@frappe.whitelist()
@rate_limit(key="user", limit=10, seconds=60)
def anular_desde_sales_invoice(name: str, motivo: str | None = None) -> Dict[str, Any]:
    row = frappe.get_all("e-CF", filters={"sales_invoice": name}, fields=["name"], limit=1)
    if not row:
        frappe.throw("No existe un e-CF vinculado a esta Sales Invoice")
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.anular",
        name=row[0]["name"],
        motivo=motivo,
    )

 
