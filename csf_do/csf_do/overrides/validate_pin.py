import frappe
import re
from frappe.model.document import Document


def validate_rnc(doctype: Document, customer: Document) -> None:
    is_rnc_mandatory = frappe.get_value(
        "Customer Group", customer.customer_group, "custom_is_rnc_mandatory_in"
    )
    if not is_rnc_mandatory:
        return

    applicable_doctypes = {
        "Customer": ["Customer", "All"],
        "Sales Order": ["Sales Order", "All", "Sales Order and Invoice"],
        "Sales Invoice": ["Sales Invoice", "All", "Sales Order and Invoice"],
    }

    doctype_name = doctype.doctype
    if (
        doctype_name not in applicable_doctypes
        or not any(option.lower() == is_rnc_mandatory.lower() for option in applicable_doctypes[doctype_name])
    ):
        return

    if not customer.tax_id:
        frappe.throw("Customer RNC is mandatory but not provided.")

    # RNC pattern for Dominican Republic: 9 digits or 11 digits
    pattern = r"^\d{9}$|^\d{11}$"
    if not re.match(pattern, customer.tax_id):
        frappe.throw(
            "Invalid Customer RNC format. Expected 9 or 11 digits."
        )

    company = frappe.defaults.get_defaults().get("company")
    if not company:
        companies = frappe.get_all("Company", {}, ["name"], limit=1)
        company = companies[0].name if companies else None

    if company:
        company_tax_id = frappe.get_value("Company", company, "tax_id")
        if company_tax_id and company_tax_id == customer.tax_id:
            frappe.throw("Customer DGII PIN cannot match Company Tax ID.")