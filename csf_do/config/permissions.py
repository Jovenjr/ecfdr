# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

from frappe import _

def get_permissions():
    """Definir permisos específicos para República Dominicana"""
    return {
        "Emisor e-CF": {
            "doctypes": ["e-CF", "Digital Certificate", "DGII Configuration"],
            "permissions": ["read", "write", "create", "delete", "submit", "cancel"]
        },
        "Aprobador Comercial": {
            "doctypes": ["Sales Invoice", "Purchase Invoice", "Sales Order", "Purchase Order"],
            "permissions": ["read", "write", "create", "submit", "cancel"]
        },
        "Administrador e-CF": {
            "doctypes": ["DGII Configuration", "e-CF", "Digital Certificate", "NCF HSCode"],
            "permissions": ["read", "write", "create", "delete", "submit", "cancel", "export"]
        }
    }

def setup_role_permissions():
    """Configurar permisos para roles específicos de RD"""
    permissions = get_permissions()
    
    for role, config in permissions.items():
        for doctype in config["doctypes"]:
            for permission in config["permissions"]:
                # Crear permisos específicos para cada doctype
                pass
