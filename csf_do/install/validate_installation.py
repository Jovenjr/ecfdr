# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from importlib import import_module


def _get_app_version(app_name: str) -> str | None:
    try:
        module = import_module(app_name)
    except ModuleNotFoundError:
        return None

    return getattr(module, "__version__", None)


def validate_erpnext_version():
    """Validar que la versión de ERPNext sea compatible"""
    installed_apps = set(frappe.get_installed_apps())

    if "erpnext" not in installed_apps:
        frappe.throw(_("ERPNext no está instalado. CSF DO requiere ERPNext v13 o superior."))

    erpnext_version = _get_app_version("erpnext")

    if not erpnext_version:
        frappe.throw(_("No se pudo determinar la versión instalada de ERPNext."))

    major_version = int(erpnext_version.split('.')[0])
    if major_version < 13:
        frappe.throw(_("CSF DO requiere ERPNext v13 o superior. Versión actual: {0}").format(erpnext_version))


def validate_dependencies():
    """Validar dependencias requeridas"""
    required_apps = ["erpnext", "hrms"]

    installed_apps = set(frappe.get_installed_apps())

    for app in required_apps:
        if app not in installed_apps:
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
