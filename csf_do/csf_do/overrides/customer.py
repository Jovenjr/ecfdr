import frappe
from frappe.model.document import Document

from .validate_rnc import validate_rnc


@frappe.whitelist()
def validate_customer_rnc(doc: Document, method: str) -> None:
    validate_rnc(doc, doc)
