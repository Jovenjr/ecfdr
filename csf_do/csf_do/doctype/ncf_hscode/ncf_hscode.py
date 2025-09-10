# Copyright (c) 2025, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
import json
import os
from frappe.model.document import Document


class NCFHSCode(Document):
    pass
	
def insert_new_records():

    base_path = frappe.get_module_path("csf_do")
    json_file_path = os.path.join(base_path, "doctype", "ncf_hscode", "ncf_hscode_data.json")

    if not os.path.exists(json_file_path):
        frappe.log_error("NCF HSCode JSON file not found", "Migration Error")
        return

    with open(json_file_path, "r") as file:
        data = json.load(file)

    for record in data:

        existing_record = frappe.get_all("NCF HSCode", filters={"name": record["name"]}, fields=["name"])

        if not existing_record:
            
            doc = frappe.get_doc({
                "doctype": "NCF HSCode",
                "name": record["name"],
                "ncf_hscode": record["ncf_hscode"],
                "description": record["description"],
                "disabled": record["disabled"],
                "docstatus": record["docstatus"],
                "item_tax": record["item_tax"],
                "uom": record["uom"],
                "itbis_": record["itbis_"]
            })
            doc.insert(ignore_permissions=True)
            frappe.logger().info(f"Inserted: {record['name']}")

        else:

            doc = frappe.get_doc("NCF HSCode", existing_record[0]["name"])

            if doc.description != record["description"]:
                doc.description = record["description"]
                doc.save()
                frappe.logger().info(f"Updated: {record['name']}")
            else:
                frappe.logger().info(f"Skipped (No Changes): {record['name']}")
