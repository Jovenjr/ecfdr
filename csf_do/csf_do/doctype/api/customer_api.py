from __future__ import annotations
from typing import Optional, Dict, Any

import frappe
from frappe.rate_limiter import rate_limit


@frappe.whitelist()
@rate_limit(key="ip", limit=60, seconds=60)
def create_or_update_customer(
    name: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_group: Optional[str] = None,
    tax_id: Optional[str] = None,
    territory: Optional[str] = None,
    customer_type: str = "Company",
    allow_missing_rnc: int = 0,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Crea o actualiza un Customer con RNC opcional.

    - Si el Customer Group exige RNC y allow_missing_rnc=0, valida formato (9 u 11 dígitos).
    - Si allow_missing_rnc=1, permite crear sin RNC aunque el grupo lo exija.
    """
    if not customer_name and not name:
        frappe.throw("customer_name or name requerido")

    # Normalizar grupo
    if not customer_group:
        customer_group = frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups"

    # Validación RNC si corresponde y no se permite faltar
    if tax_id and not allow_missing_rnc:
        import re
        if not re.match(r"^\d{9}$|^\d{11}$", str(tax_id)):
            frappe.throw("Formato de RNC inválido (9 u 11 dígitos)")

    doc = None
    if name and frappe.db.exists("Customer", name):
        doc = frappe.get_doc("Customer", name)
    else:
        # Buscar por nombre si no se pasó name
        if customer_name and frappe.db.exists("Customer", customer_name):
            doc = frappe.get_doc("Customer", customer_name)
        else:
            doc = frappe.new_doc("Customer")

    # Asignación de campos básicos
    if customer_name:
        doc.customer_name = customer_name
    if customer_group:
        doc.customer_group = customer_group
    if customer_type:
        doc.customer_type = customer_type
    if territory:
        doc.territory = territory
    if tax_id is not None:
        doc.tax_id = tax_id

    # Flag para omitir validación de RNC obligatoria si se permite faltar
    if allow_missing_rnc:
        # Desactivar hook de validación en esta transacción
        try:
            frappe.flags.ignore_customer_rnc_validation = True
        except Exception:
            pass

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"name": doc.name, "customer_name": doc.customer_name, "tax_id": doc.tax_id}
