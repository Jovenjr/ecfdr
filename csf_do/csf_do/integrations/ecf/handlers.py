"""Sales Invoice and Purchase Invoice event handlers for DGII e-CF integration."""
from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime

from csf_do.csf_do.doctype.e_cf_sequence.e_cf_sequence import ECFSequence, ExhaustedSequenceError
from csf_do.csf_do.overrides.validate_rnc import validate_rnc
from csf_do.csf_do.utils.field_validators import validate_rnc as validate_rnc_format


def before_sales_invoice_submit(doc: Document, method: str) -> None:
    """Validaciones previas al submit de Sales Invoice.
    
    - Valida RNC del cliente
    - Valida tipo e-CF
    - Asigna secuencia e-NCF si no existe
    - Calcula totales ITBIS por tasa
    """
    # Validar RNC del cliente
    if not doc.customer:
        return
    
    customer = frappe.get_doc("Customer", doc.customer)
    validate_rnc(doc, customer)
    
    # Validar tipo e-CF
    if not doc.get("dgii_tipo_ecf"):
        frappe.throw(_("Debe seleccionar un Tipo e-CF para emitir comprobante fiscal electrónico."))
    
    # Asignar e-NCF si no existe
    if not doc.get("dgii_encf"):
        _assign_encf_to_invoice(doc)
    
    # Calcular totales ITBIS
    _calculate_dgii_totals(doc)


def on_sales_invoice_submit(doc: Document, method: str) -> None:
    """Después de submit: crear/actualizar documento e-CF y encolar envío a DGII."""
    if not doc.get("dgii_encf"):
        return
    
    # Crear o actualizar documento e-CF
    ecf_doc = _create_or_update_ecf_document(doc)
    
    # Encolar envío a DGII en background
    _queue_dgii_submission(doc, ecf_doc)


def on_sales_invoice_cancel(doc: Document, method: str) -> None:
    """Al cancelar: generar Nota de Crédito electrónica (34) o anular e-NCF."""
    if not doc.get("dgii_encf"):
        return
    
    estado = doc.get("dgii_estado_dgii")
    
    # Si ya fue enviado y aceptado, requiere Nota de Crédito
    if estado in ("Aceptado", "Aceptado Condicional"):
        frappe.msgprint(
            _("Para anular una factura Aceptada por DGII debe crear una Nota de Crédito Electrónica (Tipo 34)."),
            indicator="orange",
            alert=True,
        )
    else:
        # Si aún no fue aceptado, intentar anulación directa
        _queue_dgii_cancellation(doc)


def on_sales_invoice_update_after_submit(doc: Document, method: str) -> None:
    """Permite actualizar estado DGII y track_id después de submit."""
    # Este hook permite que el scheduler actualice dgii_estado_dgii y dgii_track_id
    pass


def on_purchase_invoice_cancel(doc: Document, method: str) -> None:
    """Al cancelar Purchase Invoice: manejar anulación de e-CF de compras si aplica."""
    # Similar a Sales Invoice pero para tipo 41
    pass


# ============================================================================
# Helpers internos
# ============================================================================

def _assign_encf_to_invoice(doc: Document) -> None:
    """Asigna el próximo e-NCF de la secuencia configurada."""
    tipo_ecf = doc.get("dgii_tipo_ecf")
    if not tipo_ecf:
        frappe.throw(_("No se puede asignar e-NCF sin Tipo e-CF."))
    
    # Buscar secuencia activa para este tipo
    contingency_mode = frappe.db.get_single_value("DGII Configuration", "contingency_mode")
    serie = "B" if contingency_mode else "E"
    
    filters = {
        "sequence_type": ["like", f"{tipo_ecf}%"],
        "serie": serie,
        "status": "Activo",
    }
    
    sequences = frappe.get_all(
        "e-CF Sequence",
        filters=filters,
        fields=["name"],
        order_by="valid_until desc, next_number asc",
        limit=1,
    )
    
    if not sequences:
        frappe.throw(
            _("No hay secuencias activas para tipo e-CF {0} serie {1}. Configure una secuencia antes de emitir.").format(
                tipo_ecf, serie
            )
        )
    
    seq_doc = frappe.get_doc("e-CF Sequence", sequences[0].name)
    
    try:
        encf = seq_doc.allocate_next_encf(commit=True)
        doc.dgii_encf = encf
        doc.dgii_ecf_sequence = seq_doc.name
    except ExhaustedSequenceError:
        frappe.throw(_("La secuencia seleccionada está agotada. Configure una nueva secuencia."))


def _calculate_dgii_totals(doc: Document) -> None:
    """Calcula totales ITBIS por tasa, retenciones, ISC y propina legal."""

    company_currency = doc.get("company_currency") or frappe.db.get_value("Company", doc.company, "default_currency")
    doc_currency = doc.get("currency") or company_currency
    conversion_rate = flt(doc.get("conversion_rate") or 1.0)
    is_foreign_currency = bool(company_currency and doc_currency and doc_currency != company_currency)

    total_itbis_18 = 0.0
    total_itbis_16 = 0.0
    total_itbis_0 = 0.0
    total_itbis_exento = 0.0
    total_itbis_retenido = 0.0
    total_isr_retenido = 0.0
    total_isc = 0.0
    total_propina = 0.0
    total_itbis_foreign = 0.0

    for item in doc.get("items", []):
        indicator = item.get("dgii_indicator", "")
        base_amount = flt(item.get("base_amount"))
        if not base_amount and conversion_rate:
            base_amount = flt(item.get("amount") or 0.0) * conversion_rate
        foreign_amount = flt(item.get("amount") or 0.0)

        itbis_percentage = None
        if "18%" in indicator or indicator.startswith("1"):
            itbis_percentage = flt(item.get("dgii_itbis_percentage", 18.0))
            total_itbis_18 += base_amount * itbis_percentage / 100.0
        elif "16%" in indicator or indicator.startswith("2"):
            itbis_percentage = flt(item.get("dgii_itbis_percentage", 16.0))
            total_itbis_16 += base_amount * itbis_percentage / 100.0
        elif "0%" in indicator or indicator.startswith("3"):
            total_itbis_0 += 0.0  # Gravado pero tasa 0
        elif "exento" in indicator.lower() or indicator.startswith("0"):
            total_itbis_exento += base_amount

        if is_foreign_currency and itbis_percentage:
            total_itbis_foreign += foreign_amount * itbis_percentage / 100.0

        if item.get("dgii_isr_retencion"):
            isr_pct = flt(item.get("dgii_isr_retencion"))
            total_isr_retenido += base_amount * isr_pct / 100.0

        if item.get("dgii_propina_flag"):
            total_propina += base_amount * 0.10  # 10% propina legal

    doc.dgii_total_itbis_tasa1 = total_itbis_18
    doc.dgii_total_itbis_tasa2 = total_itbis_16
    doc.dgii_total_itbis_tasa3 = total_itbis_0
    doc.dgii_total_itbis_exento = total_itbis_exento
    doc.dgii_total_itbis_retenido = total_itbis_retenido
    doc.dgii_total_isr_retenido = total_isr_retenido
    doc.dgii_total_isc = total_isc
    doc.dgii_total_propina_legal = total_propina

    if is_foreign_currency:
        doc.dgii_tipo_moneda = doc_currency
        doc.dgii_tipo_cambio = conversion_rate
        doc.dgii_total_itbis_moneda_alterna = total_itbis_foreign
    else:
        doc.dgii_tipo_moneda = ""
        doc.dgii_tipo_cambio = 1.0
        doc.dgii_total_itbis_moneda_alterna = 0.0


def _create_or_update_ecf_document(doc: Document) -> Document:
    """Crea o actualiza el documento e-CF vinculado a la factura."""
    # Buscar si ya existe
    existing = frappe.get_all(
        "e-CF",
        filters={"sales_invoice": doc.name},
        fields=["name"],
        limit=1,
    )
    
    if existing:
        ecf_doc = frappe.get_doc("e-CF", existing[0].name)
    else:
        ecf_doc = frappe.new_doc("e-CF")
        ecf_doc.sales_invoice = doc.name
    
    # Actualizar campos
    ecf_doc.tipo_ecf = doc.get("dgii_tipo_ecf")
    ecf_doc.encf = doc.get("dgii_encf")
    ecf_doc.rnc_emisor = frappe.db.get_single_value("DGII Configuration", "rnc_emisor")
    
    customer = frappe.get_doc("Customer", doc.customer)
    ecf_doc.rnc_comprador = customer.tax_id or customer.customer_name
    
    ecf_doc.estado_dgii = doc.get("dgii_estado_dgii", "Pendiente")
    ecf_doc.sequence = doc.get("dgii_ecf_sequence")
    
    ecf_doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return ecf_doc


def _queue_dgii_submission(invoice_doc: Document, ecf_doc: Document) -> None:
    """Encola el envío del e-CF a DGII en background."""
    # Construir payload para el builder
    data = _build_ecf_payload_from_invoice(invoice_doc)
    
    frappe.enqueue(
        "csf_do.csf_do.integrations.ecf.handlers._send_ecf_job",
        queue="long",
        timeout=600,
        is_async=True,
        job_name=f"dgii-send-ecf-{ecf_doc.name}",
        kwargs={
            "ecf_name": ecf_doc.name,
            "invoice_name": invoice_doc.name,
            "tipo": invoice_doc.get("dgii_tipo_ecf"),
            "data": data,
        },
    )
    
    frappe.msgprint(
        _("El comprobante electrónico será enviado a DGII en segundo plano."),
        indicator="blue",
        alert=True,
    )


def _send_ecf_job(ecf_name: str, invoice_name: str, tipo: str, data: dict) -> None:
    """Job para enviar e-CF a DGII (ejecutado en background)."""
    from csf_do.csf_do.doctype.e_cf.e_cf import _send_job
    
    # Delegar al handler existente de e-CF
    _send_job(name=ecf_name, tipo=tipo, data=data, ambiente="custom")
    
    # Actualizar Sales Invoice con resultado
    ecf_doc = frappe.get_doc("e-CF", ecf_name)
    invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)
    
    invoice_doc.dgii_estado_dgii = ecf_doc.estado_dgii
    invoice_doc.dgii_track_id = ecf_doc.track_id
    invoice_doc.dgii_codigo_seguridad = ecf_doc.codigo_seguridad
    
    invoice_doc.save(ignore_permissions=True)
    frappe.db.commit()


def _queue_dgii_cancellation(doc: Document) -> None:
    """Encola anulación de e-NCF en DGII."""
    ecf_docs = frappe.get_all(
        "e-CF",
        filters={"sales_invoice": doc.name},
        fields=["name"],
        limit=1,
    )
    
    if not ecf_docs:
        return
    
    frappe.enqueue(
        "csf_do.csf_do.doctype.e_cf.e_cf.anular",
        queue="short",
        timeout=300,
        is_async=True,
        job_name=f"dgii-cancel-ecf-{doc.name}",
        kwargs={
            "name": ecf_docs[0].name,
            "motivo": f"Cancelación de factura {doc.name}",
        },
    )


def _build_ecf_payload_from_invoice(doc: Document) -> dict:
    """Construye el payload JSON para el builder de XML e-CF desde Sales Invoice."""
    from frappe.utils import formatdate

    rnc_emisor = frappe.db.get_single_value("DGII Configuration", "rnc_emisor")
    company = frappe.get_doc("Company", doc.company)
    customer = frappe.get_doc("Customer", doc.customer)

    company_currency = company.default_currency
    doc_currency = doc.get("currency") or company_currency
    conversion_rate = flt(doc.get("conversion_rate") or 1.0)
    is_foreign_currency = bool(company_currency and doc_currency and doc_currency != company_currency)

    base_grand_total = flt(doc.get("base_grand_total") or 0.0)
    base_net_total = flt(doc.get("base_net_total") or 0.0)
    if not base_grand_total and conversion_rate:
        base_grand_total = flt(doc.get("grand_total") or 0.0) * conversion_rate
    if not base_net_total and conversion_rate:
        base_net_total = flt(doc.get("net_total") or 0.0) * conversion_rate

    base_total_itbis = flt(doc.dgii_total_itbis_tasa1 or 0.0) + flt(doc.dgii_total_itbis_tasa2 or 0.0)
    base_total_exento = flt(doc.dgii_total_itbis_exento or 0.0)

    totales = {
        "MontoTotal": base_grand_total,
        "MontoGravadoTotal": base_net_total,
        "TotalITBIS": base_total_itbis,
    }
    if base_total_exento:
        totales["MontoExento"] = base_total_exento

    payload = {
        "encabezado": {
            "Version": "1.0",
            "IdDoc": {
                "TipoeCF": doc.get("dgii_tipo_ecf"),
                "eNCF": doc.get("dgii_encf"),
                "FechaVencimientoSecuencia": formatdate(doc.posting_date, "dd-MM-yyyy"),
                "TipoIngresos": "01",
                "TipoPago": _map_payment_type(doc.get("dgii_forma_pago")),
            },
            "Emisor": {
                "RNCEmisor": rnc_emisor,
                "RazonSocialEmisor": company.company_name,
                "DireccionEmisor": company.get("address_line1", "Sin dirección"),
                "FechaEmision": formatdate(doc.posting_date, "dd-MM-yyyy"),
            },
            "Comprador": {
                "RNCComprador": customer.tax_id or "0",
                "RazonSocialComprador": customer.customer_name,
            },
            "Totales": totales,
        },
        "detalles": {"items": []},
        "fecha_hora_firma": now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
    }

    foreign_gravado = 0.0
    foreign_exento = 0.0

    for idx, item in enumerate(doc.get("items", []), start=1):
        indicator = _map_indicator_to_code(item.get("dgii_indicator"))
        qty = flt(item.qty)
        base_rate = flt(item.get("base_rate") or 0.0)
        if not base_rate and conversion_rate:
            base_rate = flt(item.get("rate") or 0.0) * conversion_rate
        base_amount = flt(item.get("base_amount") or (base_rate * qty))

        detail = {
            "NumeroLinea": idx,
            "IndicadorFacturacion": indicator,
            "NombreItem": item.item_name or item.item_code,
            "IndicadorBienoServicio": "1",
            "CantidadItem": qty,
            "PrecioUnitarioItem": flt(base_rate, 4),
            "MontoItem": flt(base_amount, 2),
        }

        if is_foreign_currency:
            doc_rate = flt(item.get("rate") or 0.0)
            doc_amount = flt(item.get("amount") or 0.0)
            otra_moneda_detalle = {
                "PrecioOtraMoneda": flt(doc_rate, 4),
                "MontoItemOtraMoneda": flt(doc_amount, 2),
            }
            discount_alt = flt(item.get("discount_amount") or 0.0)
            if discount_alt:
                otra_moneda_detalle["DescuentoOtraMoneda"] = flt(discount_alt, 2)
            detail["OtraMonedaDetalle"] = otra_moneda_detalle

            if indicator == "0":
                foreign_exento += doc_amount
            else:
                foreign_gravado += doc_amount

        payload["detalles"]["items"].append(detail)

    if is_foreign_currency:
        otra_moneda_totales = {
            "TipoMoneda": doc.dgii_tipo_moneda or doc_currency,
            "TipoCambio": flt(conversion_rate, 6),
            "MontoTotalOtraMoneda": flt(doc.get("grand_total") or 0.0, 2),
        }
        if foreign_gravado:
            otra_moneda_totales["MontoGravadoTotalOtraMoneda"] = flt(foreign_gravado, 2)
        if foreign_exento:
            otra_moneda_totales["MontoExentoOtraMoneda"] = flt(foreign_exento, 2)
        if doc.dgii_total_itbis_moneda_alterna:
            otra_moneda_totales["TotalITBISOtraMoneda"] = flt(doc.dgii_total_itbis_moneda_alterna, 2)

        payload["encabezado"]["OtraMoneda"] = otra_moneda_totales

    return payload


def _map_payment_type(forma_pago: str) -> str:
    """Mapea forma de pago ERPNext a código DGII."""
    if not forma_pago:
        return "4"  # Crédito por defecto
    
    forma = str(forma_pago).lower()
    if "efectivo" in forma or forma.startswith("1"):
        return "1"
    elif "cheque" in forma or "transferencia" in forma or forma.startswith("2"):
        return "2"
    elif "tarjeta" in forma or forma.startswith("3"):
        return "3"
    else:
        return "4"  # Crédito


def _map_indicator_to_code(indicator: str) -> str:
    """Mapea indicador de facturación a código numérico."""
    if not indicator:
        return "1"  # Gravado 18% por defecto
    
    ind = str(indicator).lower()
    if "exento" in ind or ind.startswith("0"):
        return "0"
    elif "18%" in ind or ind.startswith("1"):
        return "1"
    elif "16%" in ind or ind.startswith("2"):
        return "2"
    elif "0%" in ind or ind.startswith("3"):
        return "3"
    elif "gastos menores" in ind or ind.startswith("4"):
        return "4"
    else:
        return "1"
