from __future__ import annotations

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


ECF_TYPES = "\n".join([
    "31",
    "32",
    "33",
    "34",
    "41",
    "43",
    "44",
    "45",
    "46",
    "47",
])

DGII_STATES = "\n".join([
    "Pendiente",
    "En Proceso",
    "Aceptado",
    "Aceptado Condicional",
    "Rechazado",
    "Observado",
    "Anulado",
])

FORMAS_PAGO = "\n".join([
    "1 - Efectivo",
    "2 - Cheque / Transferencia",
    "3 - Tarjeta",
    "4 - Crédito",
])

INDICADORES_FACTURACION = "\n".join([
    "0 - Exento",
    "1 - Gravado ITBIS 18%",
    "2 - Gravado ITBIS 16%",
    "3 - Gravado ITBIS 0%",
    "4 - Gastos Menores",
])


def execute() -> None:
    custom_fields = {
        "Sales Invoice": [
            {
                "fieldname": "dgii_ecf_section",
                "label": "DGII e-CF",
                "fieldtype": "Section Break",
                "insert_after": "posting_date",
            },
            {
                "fieldname": "dgii_tipo_ecf",
                "label": "Tipo e-CF",
                "fieldtype": "Select",
                "options": ECF_TYPES,
                "default": "31",
                "reqd": 1,
                "insert_after": "dgii_ecf_section",
            },
            {
                "fieldname": "dgii_ecf_sequence",
                "label": "Secuencia e-CF",
                "fieldtype": "Link",
                "options": "e-CF Sequence",
                "insert_after": "dgii_tipo_ecf",
            },
            {
                "fieldname": "dgii_encf",
                "label": "e-NCF",
                "fieldtype": "Data",
                "insert_after": "dgii_ecf_sequence",
                "allow_on_submit": 1,
                "read_only": 1,
                "search_index": 1,
            },
            {
                "fieldname": "dgii_estado_dgii",
                "label": "Estado DGII",
                "fieldtype": "Select",
                "options": DGII_STATES,
                "default": "Pendiente",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_encf",
            },
            {
                "fieldname": "dgii_track_id",
                "label": "Track ID DGII",
                "fieldtype": "Data",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_estado_dgii",
            },
            {
                "fieldname": "dgii_codigo_seguridad",
                "label": "Código de Seguridad",
                "fieldtype": "Data",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_track_id",
            },
            {
                "fieldname": "dgii_forma_pago",
                "label": "Forma de Pago DGII",
                "fieldtype": "Select",
                "options": FORMAS_PAGO,
                "insert_after": "dgii_codigo_seguridad",
            },
            {
                "fieldname": "dgii_totals_column_break",
                "fieldtype": "Column Break",
                "insert_after": "dgii_forma_pago",
            },
            {
                "fieldname": "dgii_total_itbis_tasa1",
                "label": "Total ITBIS Tasa 18%",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_totals_column_break",
            },
            {
                "fieldname": "dgii_total_itbis_tasa2",
                "label": "Total ITBIS Tasa 16%",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_total_itbis_tasa1",
            },
            {
                "fieldname": "dgii_total_itbis_tasa3",
                "label": "Total ITBIS Tasa 0%",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_total_itbis_tasa2",
            },
            {
                "fieldname": "dgii_total_itbis_exento",
                "label": "Total ITBIS Exento",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_total_itbis_tasa3",
            },
            {
                "fieldname": "dgii_total_itbis_retenido",
                "label": "Total ITBIS Retenido",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_total_itbis_exento",
            },
            {
                "fieldname": "dgii_total_isr_retenido",
                "label": "Total ISR Retenido",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_total_itbis_retenido",
            },
            {
                "fieldname": "dgii_total_isc",
                "label": "Total ISC",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_total_isr_retenido",
            },
            {
                "fieldname": "dgii_total_propina_legal",
                "label": "Propina Legal",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_total_isc",
            },
            {
                "fieldname": "dgii_other_currency_section",
                "fieldtype": "Section Break",
                "label": "Otra Moneda",
                "insert_after": "dgii_total_propina_legal",
            },
            {
                "fieldname": "dgii_tipo_moneda",
                "label": "Tipo de Moneda",
                "fieldtype": "Data",
                "insert_after": "dgii_other_currency_section",
            },
            {
                "fieldname": "dgii_tipo_cambio",
                "label": "Tipo de Cambio",
                "fieldtype": "Float",
                "precision": "6",
                "insert_after": "dgii_tipo_moneda",
            },
            {
                "fieldname": "dgii_total_itbis_moneda_alterna",
                "label": "Total ITBIS (Otra Moneda)",
                "fieldtype": "Currency",
                "allow_on_submit": 1,
                "read_only": 1,
                "insert_after": "dgii_tipo_cambio",
            },
        ],
        "Sales Invoice Item": [
            {
                "fieldname": "dgii_indicator",
                "label": "Indicador Facturación",
                "fieldtype": "Select",
                "options": INDICADORES_FACTURACION,
                "default": "1 - Gravado ITBIS 18%",
                "reqd": 1,
                "insert_after": "uom",
            },
            {
                "fieldname": "dgii_itbis_percentage",
                "label": "% ITBIS",
                "fieldtype": "Percent",
                "precision": "2",
                "insert_after": "dgii_indicator",
            },
            {
                "fieldname": "dgii_isr_retencion",
                "label": "RET ISR %",
                "fieldtype": "Percent",
                "precision": "2",
                "insert_after": "dgii_itbis_percentage",
            },
            {
                "fieldname": "dgii_isc_codigo",
                "label": "Código ISC",
                "fieldtype": "Data",
                "insert_after": "dgii_isr_retencion",
            },
            {
                "fieldname": "dgii_propina_flag",
                "label": "Incluye Propina Legal",
                "fieldtype": "Check",
                "insert_after": "dgii_isc_codigo",
            },
        ],
    }

    create_custom_fields(custom_fields, update=True)
