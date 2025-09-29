# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now

def get_backup_config():
    """Configuración de backup para CSF DO"""
    return {
        "include_doctypes": [
            "DGII Configuration",
            "Digital Certificate", 
            "e-CF",
            "NCF HSCode",
            "ITBIS Withholding"
        ],
        "exclude_doctypes": [
            "e-CF Audit Log"
        ],
        "backup_frequency": "daily",
        "retention_days": 30
    }

def create_critical_data_backup():
    """Crear backup de datos críticos de CSF DO"""
    backup_config = get_backup_config()
    
    # Crear backup de configuraciones críticas
    critical_data = {}
    
    for doctype in backup_config["include_doctypes"]:
        if frappe.db.exists("DocType", doctype):
            data = frappe.get_all(doctype, fields=["*"])
            critical_data[doctype] = data
    
    return critical_data
