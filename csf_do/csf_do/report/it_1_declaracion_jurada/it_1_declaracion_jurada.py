# -*- coding: utf-8 -*-
# Copyright (c) 2025, AI Studio RD and contributors
# For license information, please see license.txt

"""
Reporte IT-1: Declaración Jurada de Retenciones de ITBIS

Este reporte genera la información necesaria para la Declaración Jurada IT-1
de acuerdo con las regulaciones de la DGII de República Dominicana.

La IT-1 es la declaración mensual de retenciones de ITBIS (IVA) que deben 
presentar las entidades del Estado y grandes contribuyentes.
"""

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate


def execute(filters=None):
    """
    Ejecuta el reporte IT-1
    
    Args:
        filters: Diccionario con filtros del reporte
        
    Returns:
        tuple: (columns, data)
    """
    if not filters:
        filters = {}
    
    # Validar filtros requeridos
    validate_filters(filters)
    
    # Obtener columnas y datos
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data


def validate_filters(filters):
    """
    Valida que los filtros requeridos estén presentes
    """
    if not filters.get("from_date"):
        frappe.throw(_("Fecha Desde es requerida"))
    
    if not filters.get("to_date"):
        frappe.throw(_("Fecha Hasta es requerida"))
    
    if getdate(filters.from_date) > getdate(filters.to_date):
        frappe.throw(_("Fecha Desde no puede ser mayor que Fecha Hasta"))


def get_columns():
    """
    Define las columnas del reporte
    """
    return [
        {
            "label": _("NCF"),
            "fieldname": "ncf",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Fecha"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("RNC Proveedor"),
            "fieldname": "rnc_proveedor",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": _("Nombre Proveedor"),
            "fieldname": "nombre_proveedor",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Tipo Comprobante"),
            "fieldname": "tipo_comprobante",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Factura No."),
            "fieldname": "factura",
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 130
        },
        {
            "label": _("Monto Facturado"),
            "fieldname": "monto_facturado",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("ITBIS Facturado"),
            "fieldname": "itbis_facturado",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("ITBIS Retenido"),
            "fieldname": "itbis_retenido",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("% Retención"),
            "fieldname": "porcentaje_retencion",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("Compañía"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 150
        }
    ]


def get_data(filters):
    """
    Obtiene los datos del reporte
    
    Args:
        filters: Diccionario con filtros
        
    Returns:
        list: Lista de diccionarios con los datos
    """
    conditions = get_conditions(filters)
    
    # Query principal
    data = frappe.db.sql("""
        SELECT
            pi.name as factura,
            pi.posting_date,
            pi.bill_no as ncf,
            s.tax_id as rnc_proveedor,
            s.supplier_name as nombre_proveedor,
            pi.ncf_type as tipo_comprobante,
            pi.net_total as monto_facturado,
            pi.total_taxes_and_charges as itbis_facturado,
            COALESCE(pi.custom_itbis_retenido, 0) as itbis_retenido,
            COALESCE(pi.custom_porcentaje_retencion, 0) as porcentaje_retencion,
            pi.company
        FROM
            `tabPurchase Invoice` pi
        LEFT JOIN
            `tabSupplier` s ON pi.supplier = s.name
        WHERE
            pi.docstatus = 1
            {conditions}
        ORDER BY
            pi.posting_date, pi.name
    """.format(conditions=conditions), filters, as_dict=1)
    
    # Calcular totales y ajustar datos
    total_facturado = 0
    total_itbis_facturado = 0
    total_itbis_retenido = 0
    
    for row in data:
        # Si no hay retención explícita pero es gran contribuyente, calcular 30% del ITBIS
        if not row.itbis_retenido and row.itbis_facturado:
            if is_gran_contribuyente(row.rnc_proveedor):
                row.itbis_retenido = flt(row.itbis_facturado * 0.30, 2)
                row.porcentaje_retencion = 30
        
        # Acumular totales
        total_facturado += flt(row.monto_facturado)
        total_itbis_facturado += flt(row.itbis_facturado)
        total_itbis_retenido += flt(row.itbis_retenido)
    
    # Agregar fila de totales
    if data:
        data.append({
            "factura": "<b>TOTALES</b>",
            "monto_facturado": total_facturado,
            "itbis_facturado": total_itbis_facturado,
            "itbis_retenido": total_itbis_retenido,
            "posting_date": ""
        })
    
    return data


def get_conditions(filters):
    """
    Construye las condiciones WHERE del query
    
    Args:
        filters: Diccionario con filtros
        
    Returns:
        str: Condiciones SQL
    """
    conditions = []
    
    # Filtro de fechas
    if filters.get("from_date"):
        conditions.append("pi.posting_date >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("pi.posting_date <= %(to_date)s")
    
    # Filtro de compañía
    if filters.get("company"):
        conditions.append("pi.company = %(company)s")
    
    # Filtro de proveedor
    if filters.get("supplier"):
        conditions.append("pi.supplier = %(supplier)s")
    
    # Solo facturas con ITBIS
    conditions.append("pi.total_taxes_and_charges > 0")
    
    return " AND " + " AND ".join(conditions) if conditions else ""


def is_gran_contribuyente(rnc):
    """
    Verifica si un RNC pertenece a un gran contribuyente
    
    Args:
        rnc: RNC a verificar
        
    Returns:
        bool: True si es gran contribuyente
    """
    # Buscar en Supplier si tiene marcado gran_contribuyente
    supplier = frappe.db.get_value(
        "Supplier",
        {"tax_id": rnc},
        "custom_gran_contribuyente"
    )
    
    return supplier or False


# ==================== UTILITY FUNCTIONS ====================

@frappe.whitelist()
def export_to_excel(filters):
    """
    Exporta el reporte a Excel
    
    Args:
        filters: Filtros del reporte
        
    Returns:
        str: Path del archivo Excel generado
    """
    import json
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    columns, data = execute(filters)
    
    # Usar el ExcelBuilder de Frappe
    from frappe.utils.xlsxutils import make_xlsx
    
    xlsx_data = []
    
    # Headers
    headers = [col.get("label") for col in columns]
    xlsx_data.append(headers)
    
    # Data
    for row in data:
        xlsx_row = []
        for col in columns:
            fieldname = col.get("fieldname")
            value = row.get(fieldname, "")
            xlsx_row.append(value)
        xlsx_data.append(xlsx_row)
    
    # Generar archivo
    xlsx_file = make_xlsx(xlsx_data, "IT-1 Declaracion Jurada")
    
    return xlsx_file


@frappe.whitelist()
def get_summary(filters):
    """
    Obtiene resumen del reporte para dashboard
    
    Args:
        filters: Filtros del reporte
        
    Returns:
        dict: Resumen con totales
    """
    import json
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    _, data = execute(filters)
    
    # El último elemento es la fila de totales
    if data:
        totales = data[-1]
        return {
            "total_facturas": len(data) - 1,
            "total_facturado": totales.get("monto_facturado", 0),
            "total_itbis_facturado": totales.get("itbis_facturado", 0),
            "total_itbis_retenido": totales.get("itbis_retenido", 0)
        }
    
    return {
        "total_facturas": 0,
        "total_facturado": 0,
        "total_itbis_facturado": 0,
        "total_itbis_retenido": 0
    }
