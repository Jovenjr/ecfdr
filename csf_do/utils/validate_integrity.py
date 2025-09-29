# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def validate_system_integrity():
    """Validar integridad del sistema CSF DO"""
    results = {
        "passed": [],
        "warnings": [],
        "errors": []
    }
    
    # Validar configuración básica
    validate_basic_config(results)
    
    # Validar certificados digitales
    validate_digital_certificates(results)
    
    # Validar configuración DGII
    validate_dgii_config(results)
    
    # Validar datos maestros
    validate_master_data(results)
    
    return results

def validate_basic_config(results):
    """Validar configuración básica"""
    # Verificar país
    if frappe.db.exists("Country", "Dominican Republic"):
        results["passed"].append("País República Dominicana configurado")
    else:
        results["errors"].append("País República Dominicana no configurado")
    
    # Verificar moneda
    if frappe.db.exists("Currency", "DOP"):
        results["passed"].append("Moneda DOP configurada")
    else:
        results["errors"].append("Moneda DOP no configurada")

def validate_digital_certificates(results):
    """Validar certificados digitales"""
    certificates = frappe.get_all("Digital Certificate", filters={"enabled": 1})
    
    if certificates:
        results["passed"].append(f"{len(certificates)} certificado(s) digital(es) configurado(s)")
    else:
        results["warnings"].append("No hay certificados digitales configurados")

def validate_dgii_config(results):
    """Validar configuración DGII"""
    dgii_configs = frappe.get_all("DGII Configuration", filters={"enabled": 1})
    
    if dgii_configs:
        results["passed"].append("Configuración DGII activa")
    else:
        results["warnings"].append("No hay configuración DGII activa")

def validate_master_data(results):
    """Validar datos maestros"""
    # Verificar roles
    roles = ["Emisor e-CF", "Aprobador Comercial", "Administrador e-CF"]
    for role in roles:
        if frappe.db.exists("Role", role):
            results["passed"].append(f"Rol {role} creado")
        else:
            results["errors"].append(f"Rol {role} no encontrado")
    
    # Verificar almacenes
    if frappe.db.exists("Warehouse", "Almacén Principal - RD"):
        results["passed"].append("Almacén principal configurado")
    else:
        results["warnings"].append("Almacén principal no configurado")

def get_validation_report():
    """Obtener reporte de validación"""
    return validate_system_integrity()
