# -*- coding: utf-8 -*-
# Copyright (c) 2025, AI Studio RD and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, nowdate, now
from datetime import datetime, timedelta


class NCFSeries(Document):
    """
    Gestión de Series de Comprobantes Fiscales (NCF)
    para cumplimiento con normativa DGII de República Dominicana
    """
    
    # Mapeo de tipos de NCF
    TIPOS_NCF = {
        "B01": "Facturas de Crédito Fiscal",
        "B02": "Facturas de Consumo",
        "B03": "Notas de Débito",
        "B04": "Notas de Crédito",
        "B11": "Proveedores Informales",
        "B12": "Registro Único de Ingresos",
        "B13": "Gastos Menores",
        "B14": "Régimen Especial de Tributación",
        "B15": "Gubernamental",
        "B16": "Exportaciones",
        "B17": "Pagos al Exterior"
    }
    
    def before_insert(self):
        """Validaciones antes de insertar"""
        self.validate_serie()
        self.validate_range()
        self.set_tipo_ncf_name()
        self.calculate_disponibles()
        
    def before_save(self):
        """Validaciones antes de guardar"""
        self.validate_range()
        self.set_tipo_ncf_name()
        self.calculate_disponibles()
        self.calculate_dias_restantes()
        self.check_alerta_vencimiento()
        self.calculate_porcentaje_uso()
        self.update_estado()
        
    def validate_serie(self):
        """Valida que la serie sea A o B"""
        if self.serie not in ["A", "B"]:
            frappe.throw("La serie debe ser A (producción) o B (contingencia)")
            
    def validate_range(self):
        """Valida el rango de numeración"""
        if self.desde >= self.hasta:
            frappe.throw("El número 'Desde' debe ser menor que 'Hasta'")
            
        # Validar que el rango sea de 8 dígitos
        if len(str(self.desde)) > 8 or len(str(self.hasta)) > 8:
            frappe.throw("Los números deben tener máximo 8 dígitos")
            
    def set_tipo_ncf_name(self):
        """Establece el nombre del tipo de NCF"""
        self.tipo_ncf_name = self.TIPOS_NCF.get(self.tipo_ncf, "")
        
    def calculate_disponibles(self):
        """Calcula números disponibles"""
        actual = self.actual or self.desde
        self.disponibles = self.hasta - actual + 1
        
    def calculate_dias_restantes(self):
        """Calcula días restantes hasta el vencimiento"""
        if self.fecha_vencimiento:
            today = getdate(nowdate())
            vencimiento = getdate(self.fecha_vencimiento)
            self.dias_restantes = date_diff(vencimiento, today)
        else:
            self.dias_restantes = 0
            
    def check_alerta_vencimiento(self):
        """Activa alerta si faltan menos de 30 días"""
        self.alerta_vencimiento = 1 if self.dias_restantes <= 30 else 0
        
    def calculate_porcentaje_uso(self):
        """Calcula el porcentaje de uso de la serie"""
        total_numeros = self.hasta - self.desde + 1
        if total_numeros > 0:
            self.porcentaje_uso = (self.total_emitidos / total_numeros) * 100
        else:
            self.porcentaje_uso = 0
            
    def update_estado(self):
        """Actualiza el estado de la serie"""
        # Vencido
        if self.dias_restantes < 0:
            self.estado = "Vencido"
        # Agotado
        elif self.disponibles <= 0:
            self.estado = "Agotado"
        # Activo
        else:
            self.estado = "Activo"
            
    def get_next_ncf(self):
        """
        Obtiene el próximo NCF disponible de la serie
        Returns: NCF completo en formato BXXYYYYYYYY
        """
        # Validar que la serie esté activa
        if self.estado != "Activo":
            frappe.throw(f"La serie {self.name} no está activa. Estado: {self.estado}")
            
        # Inicializar actual si es la primera vez
        if not self.actual:
            self.actual = self.desde
            
        # Validar que no se haya agotado
        if self.actual > self.hasta:
            self.estado = "Agotado"
            self.save()
            frappe.throw(f"La serie {self.name} se ha agotado")
            
        # Generar NCF
        ncf_numero = str(self.actual).zfill(8)
        ncf_completo = f"{self.serie}{self.tipo_ncf}{ncf_numero}"
        
        # Incrementar contador
        self.actual += 1
        self.total_emitidos += 1
        self.ultimo_ncf_emitido = ncf_completo
        self.fecha_ultimo_uso = now()
        
        # Guardar cambios
        self.save()
        frappe.db.commit()
        
        return ncf_completo
        
    @staticmethod
    def get_active_series(tipo_ncf, company=None):
        """
        Obtiene la serie activa para un tipo de NCF
        Args:
            tipo_ncf: Tipo de NCF (B01, B02, etc.)
            company: Compañía (opcional)
        Returns:
            NCFSeries document o None
        """
        filters = {
            "tipo_ncf": tipo_ncf,
            "estado": "Activo"
        }
        
        if company:
            filters["company"] = company
            
        series = frappe.get_all(
            "NCF Series",
            filters=filters,
            order_by="fecha_vencimiento desc",
            limit=1
        )
        
        if series:
            return frappe.get_doc("NCF Series", series[0].name)
        return None


@frappe.whitelist()
def get_ncf_for_invoice(tipo_ncf, company):
    """
    Obtiene un NCF para una factura
    Args:
        tipo_ncf: Tipo de NCF requerido
        company: Compañía
    Returns:
        NCF generado
    """
    serie = NCFSeries.get_active_series(tipo_ncf, company)
    
    if not serie:
        frappe.throw(f"No hay series activas para el tipo {tipo_ncf}")
        
    return serie.get_next_ncf()


@frappe.whitelist()
def get_series_dashboard_data(company=None):
    """
    Obtiene datos para el dashboard de series NCF
    Returns:
        Dict con métricas
    """
    filters = {}
    if company:
        filters["company"] = company
        
    # Series activas
    activas = frappe.db.count("NCF Series", {"estado": "Activo", **filters})
    
    # Próximas a vencer (menos de 30 días)
    proximas_vencer = frappe.db.count("NCF Series", {
        "estado": "Activo",
        "alerta_vencimiento": 1,
        **filters
    })
    
    # Total de NCF utilizados
    total_utilizados = frappe.db.sql("""
        SELECT SUM(total_emitidos)
        FROM `tabNCF Series`
        WHERE estado != 'Inactivo'
        {company_filter}
    """.format(
        company_filter=f"AND company = '{company}'" if company else ""
    ))[0][0] or 0
    
    return {
        "series_activas": activas,
        "proximas_vencer": proximas_vencer,
        "total_utilizados": int(total_utilizados)
    }


@frappe.whitelist()
def check_series_alerts():
    """
    Verifica y envía alertas para series próximas a vencer o agotarse
    """
    # Series próximas a vencer
    series_vencer = frappe.get_all(
        "NCF Series",
        filters={
            "estado": "Activo",
            "alerta_vencimiento": 1
        },
        fields=["name", "tipo_ncf", "tipo_ncf_name", "dias_restantes", "fecha_vencimiento"]
    )
    
    # Series próximas a agotarse (menos del 10% disponible)
    series_agotar = frappe.db.sql("""
        SELECT name, tipo_ncf, tipo_ncf_name, disponibles, porcentaje_uso
        FROM `tabNCF Series`
        WHERE estado = 'Activo'
        AND porcentaje_uso > 90
    """, as_dict=True)
    
    alerts = {
        "series_por_vencer": series_vencer,
        "series_por_agotar": series_agotar
    }
    
    return alerts
