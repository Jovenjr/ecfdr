# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute():
    """Migración para configurar datos iniciales de CSF DO"""
    frappe.logger().info("Ejecutando migración de datos iniciales...")
    
    try:
        # Importar y ejecutar configuración inicial
        from csf_do.install.setup_initial_data import setup_dominican_data
        setup_dominican_data()
        
        frappe.logger().info("Migración de datos iniciales completada")
        
    except Exception as e:
        frappe.logger().error(f"Error en migración: {str(e)}")
        raise
