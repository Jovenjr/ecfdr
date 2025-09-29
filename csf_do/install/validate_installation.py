# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def validate_erpnext_version():
    """Validar que la versión de ERPNext sea compatible"""
    erpnext_version = frappe.get_installed_version("erpnext")
    
    if not erpnext_version:
        frappe.throw(_("ERPNext no está instalado. CSF DO requiere ERPNext v13 o superior."))
    
    major_version = int(erpnext_version.split('.')[0])
    if major_version < 13:
        frappe.throw(_("CSF DO requiere ERPNext v13 o superior. Versión actual: {0}").format(erpnext_version))

def validate_dependencies():
    """Validar dependencias requeridas"""
    required_apps = ["erpnext", "hrms"]
    
    for app in required_apps:
        if not frappe.get_installed_version(app):
            frappe.throw(_("Aplicación requerida {0} no está instalada").format(app))

def validate_certificate_config():
    """Validar configuración de certificados digitales"""
    if not frappe.db.exists("Digital Certificate", {"enabled": 1}):
        frappe.logger().warning("No hay certificados digitales configurados")

def validate_dgii_config():
    """Validar configuración de DGII"""
    if not frappe.db.exists("DGII Configuration", {"enabled": 1}):
        frappe.logger().warning("No hay configuración de DGII activa")

def validate_installation():
    """Validar instalación completa"""
    checks = [
        ("Country", "Dominican Republic"),
        ("Currency", "DOP"),
        ("Role", "Emisor e-CF")
    ]
    
    for doctype, name in checks:
        if not frappe.db.exists(doctype, name):
            frappe.logger().warning(f"Validación fallida: {doctype} - {name}")
    
    return True
