from __future__ import annotations
from typing import Dict, Any
from frappe.rate_limiter import rate_limit

import frappe


@frappe.whitelist()
@rate_limit(key="user", limit=30, seconds=60)
def enviar_ecf(name: str, tipo: str, data: Dict | None = None, ambiente: str = "custom") -> Dict[str, Any]:
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.enviar",
        name=name,
        tipo=tipo,
        data=data,
        ambiente=ambiente,
    )


@frappe.whitelist()
@rate_limit(key="user", limit=60, seconds=60)
def consultar_estado(name: str, ambiente: str = "custom") -> Dict[str, Any]:
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.consultar_estado",
        name=name,
        ambiente=ambiente,
    )


@frappe.whitelist()
@rate_limit(key="user", limit=10, seconds=60)
def anular_encf(name: str, motivo: str | None = None) -> Dict[str, Any]:
    return frappe.call(
        "csf_do.csf_do.doctype.e_cf.e_cf.anular",
        name=name,
        motivo=motivo,
    )

