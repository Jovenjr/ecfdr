# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def setup_dominican_data():
    """Configurar datos iniciales específicos de República Dominicana"""
    setup_country()
    setup_currency()
    setup_warehouses()
    setup_roles()

def setup_country():
    """Configurar República Dominicana"""
    if not frappe.db.exists("Country", "Dominican Republic"):
        country = frappe.get_doc({
            "doctype": "Country",
            "country_name": "Dominican Republic",
            "code": "DO",
            "date_format": "dd-mm-yyyy",
            "timezone": "America/Santo_Domingo"
        })
        country.insert(ignore_permissions=True)

def setup_currency():
    """Configurar Peso Dominicano"""
    if not frappe.db.exists("Currency", "DOP"):
        currency = frappe.get_doc({
            "doctype": "Currency",
            "currency_name": "Peso Dominicano",
            "symbol": "RD$",
            "fraction": "Centavo",
            "fraction_units": 100,
            "enabled": 1
        })
        currency.insert(ignore_permissions=True)

def setup_warehouses():
    """Crear almacenes por defecto"""
    warehouses = [
        {"warehouse_name": "Almacén Principal - RD", "is_group": 0},
        {"warehouse_name": "All Warehouses - RD", "is_group": 1}
    ]
    
    for wh_data in warehouses:
        if not frappe.db.exists("Warehouse", wh_data["warehouse_name"]):
            warehouse = frappe.get_doc({
                "doctype": "Warehouse",
                **wh_data,
                "company": frappe.defaults.get_user_default("Company")
            })
            warehouse.insert(ignore_permissions=True)

def setup_roles():
    """Crear roles específicos de RD"""
    roles = ["Emisor e-CF", "Aprobador Comercial", "Administrador e-CF"]
    
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1,
                "is_custom": 1
            })
            role.insert(ignore_permissions=True)
