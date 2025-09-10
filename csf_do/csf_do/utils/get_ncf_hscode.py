import frappe
from frappe import _

def validate_mandatory_hscode(doc, method):
    """
    Validate that the NCF HSCode field is filled if an Item Tax Template is linked.
    """
    for tax in doc.taxes:
        if tax.item_tax_template:
            hscodes = frappe.get_all("NCF HSCode", 
                                     filters={"item_tax": tax.item_tax_template}, 
                                     fields=["name", "ncf_hscode"])

            if hscodes and not tax.ncf_hscode:
                fieldname = "ncf_hscode"
                message = _(
                    "NCF HSCode is mandatory for Item Tax Template {0}.").format(frappe.bold(tax.item_tax_template), fieldname)

                frappe.throw(message, title=_("Missing NCF HSCode"))
