# -*- coding: utf-8 -*-
# Copyright (c) 2025, AI Studio RD and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_dashboard_data(company=None):
    """
    Obtiene datos para el dashboard DGII
    
    Returns:
        dict con métricas y estadísticas
    """
    filters = {}
    if company:
        filters["company"] = company
    
    # Métricas de eCF
    ecf_emitidos = frappe.db.count("e-CF", {"docstatus": 1, **filters})
    ecf_pendientes = frappe.db.count("e-CF", {"docstatus": 0, **filters})
    ecf_cancelados = frappe.db.count("e-CF", {"docstatus": 2, **filters})
    
    # Métricas de NCF Series
    from csf_do.csf_do.doctype.ncf_series.ncf_series import get_series_dashboard_data
    ncf_data = get_series_dashboard_data(company)
    
    # eCF Recibidos
    ecf_recibidos = frappe.db.count("eCF Recibido", filters)
    
    # Validaciones RNC del mes
    validaciones_rnc = frappe.db.sql("""
        SELECT COUNT(*) as total
        FROM `tabCustomer`
        WHERE MONTH(modified) = MONTH(CURDATE())
        AND YEAR(modified) = YEAR(CURDATE())
        AND tax_id IS NOT NULL
    """)[0][0]
    
    return {
        "ecf": {
            "emitidos": ecf_emitidos,
            "pendientes": ecf_pendientes,
            "cancelados": ecf_cancelados,
            "total": ecf_emitidos + ecf_pendientes + ecf_cancelados
        },
        "ncf": ncf_data,
        "ecf_recibidos": ecf_recibidos,
        "validaciones_rnc": validaciones_rnc
    }


@frappe.whitelist()
def get_ncf_series_list(company=None, estado=None):
    """
    Obtiene listado de series NCF con filtros
    
    Args:
        company: Compañía (opcional)
        estado: Estado de la serie (opcional)
        
    Returns:
        list de series NCF
    """
    filters = {}
    if company:
        filters["company"] = company
    if estado:
        filters["estado"] = estado
    
    series = frappe.get_all(
        "NCF Series",
        filters=filters,
        fields=[
            "name",
            "tipo_ncf",
            "tipo_ncf_name",
            "serie",
            "desde",
            "hasta",
            "actual",
            "disponibles",
            "fecha_vencimiento",
            "dias_restantes",
            "estado",
            "total_emitidos",
            "porcentaje_uso",
            "alerta_vencimiento"
        ],
        order_by="fecha_vencimiento asc"
    )
    
    return series


@frappe.whitelist()
def get_recent_ecf(company=None, limit=10):
    """
    Obtiene los eCF más recientes
    
    Args:
        company: Compañía (opcional)
        limit: Cantidad de registros
        
    Returns:
        list de eCF
    """
    filters = {"docstatus": 1}
    if company:
        filters["company"] = company
    
    ecf_list = frappe.get_all(
        "e-CF",
        filters=filters,
        fields=[
            "name",
            "ncf",
            "customer",
            "posting_date",
            "grand_total",
            "status"
        ],
        order_by="posting_date desc",
        limit=limit
    )
    
    return ecf_list
