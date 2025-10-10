# -*- coding: utf-8 -*-
# Copyright (c) 2025, AI Studio RD and contributors
# For license information, please see license.txt

"""
Custom Fields para validación de ITBIS en facturas
"""

from __future__ import unicode_literals
import frappe


def create_itbis_validation_fields():
    """
    Crea campos personalizados para tracking de validación ITBIS
    en Sales Invoice y Purchase Invoice
    """
    
    custom_fields = {
        "Sales Invoice": [
            {
                "fieldname": "custom_itbis_section",
                "label": "Validación ITBIS",
                "fieldtype": "Section Break",
                "insert_after": "taxes",
                "collapsible": 1
            },
            {
                "fieldname": "custom_itbis_validado",
                "label": "ITBIS Validado",
                "fieldtype": "Check",
                "insert_after": "custom_itbis_section",
                "read_only": 1,
                "default": 0
            },
            {
                "fieldname": "custom_itbis_rate",
                "label": "Tasa ITBIS (%)",
                "fieldtype": "Percent",
                "insert_after": "custom_itbis_validado",
                "read_only": 1,
                "default": 18
            },
            {
                "fieldname": "custom_itbis_amount",
                "label": "Monto ITBIS",
                "fieldtype": "Currency",
                "insert_after": "custom_itbis_rate",
                "read_only": 1,
                "options": "currency"
            },
            {
                "fieldname": "custom_column_break_itbis",
                "fieldtype": "Column Break",
                "insert_after": "custom_itbis_amount"
            }
        ],
        "Purchase Invoice": [
            {
                "fieldname": "custom_itbis_section",
                "label": "Validación ITBIS",
                "fieldtype": "Section Break",
                "insert_after": "taxes",
                "collapsible": 1
            },
            {
                "fieldname": "custom_itbis_validado",
                "label": "ITBIS Validado",
                "fieldtype": "Check",
                "insert_after": "custom_itbis_section",
                "read_only": 1,
                "default": 0
            },
            {
                "fieldname": "custom_itbis_rate",
                "label": "Tasa ITBIS (%)",
                "fieldtype": "Percent",
                "insert_after": "custom_itbis_validado",
                "read_only": 1,
                "default": 18
            },
            {
                "fieldname": "custom_itbis_amount",
                "label": "Monto ITBIS",
                "fieldtype": "Currency",
                "insert_after": "custom_itbis_rate",
                "read_only": 1,
                "options": "currency"
            },
            {
                "fieldname": "custom_column_break_itbis",
                "fieldtype": "Column Break",
                "insert_after": "custom_itbis_amount"
            }
        ]
    }
    
    for doctype, fields in custom_fields.items():
        for field in fields:
            # Verificar si el campo ya existe
            if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}):
                custom_field = frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": doctype,
                    "module": "Csf Do",
                    **field
                })
                custom_field.insert(ignore_permissions=True)
                print(f"✅ Created custom field {field['fieldname']} in {doctype}")
            else:
                print(f"⏭️ Custom field {field['fieldname']} already exists in {doctype}")
    
    frappe.db.commit()
    print("✅ ITBIS validation fields created successfully")


if __name__ == "__main__":
    create_itbis_validation_fields()
