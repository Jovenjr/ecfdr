import frappe
from frappe.model.document import Document

from .validate_rnc import validate_rnc


def validate_customer_rnc(doc: Document, method: str) -> None:
    if not doc.customer:
        return

    customer = frappe.get_doc("Customer", doc.customer)

    validate_rnc(doc, customer)
