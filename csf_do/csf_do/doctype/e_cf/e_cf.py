from __future__ import annotations
from typing import Any, Dict

import frappe
from frappe.model.document import Document

from csf_do.csf_do.utils.ecf_service import enviar_ecf_config, consultar_estado_config
from csf_do.csf_do.utils.qr_code_generator import build_qr_payload_from_xml, get_qr_code
from csf_do.csf_do.utils.field_validators import validate_encf, validate_rnc
from csf_do.csf_do.utils.input_validator import validate_against_spec
from csf_do.csf_do.utils.business_rules import validate_pre_send_basic
from csf_do.csf_do.utils.dgii_errors import build_friendly_error_message


class ECF(Document):
    def validate(self) -> None:
        # Validaciones básicas
        if self.encf:
            validate_encf(self.encf)
        if self.rnc_emisor:
            validate_rnc(self.rnc_emisor, field_name="RNC Emisor")
        if self.rnc_comprador:
            validate_rnc(self.rnc_comprador, field_name="RNC Comprador")

    def on_submit(self) -> None:
        pass


def _update_doc_from_result(doc: "ECF", result: Any) -> None:
    if not result:
        return
    try:
        if hasattr(result, "xml") and result.xml:
            doc.signed_xml = result.xml
        if hasattr(result, "track_id"):
            doc.track_id = result.track_id
        if hasattr(result, "estado") and result.estado:
            # map to e-CF status labels where possible
            doc.estado_dgii = result.estado
        if hasattr(result, "firma") and result.firma:
            try:
                codigo = getattr(result.firma, "codigo_seguridad", None)
                if codigo:
                    doc.codigo_seguridad = codigo
                    # best-effort QR
                    if result.xml:
                        payload = build_qr_payload_from_xml(result.xml, codigo)
                        texto = payload.get("texto")
                        if texto:
                            doc.qr_image_base64 = get_qr_code(texto)
            except Exception:
                pass
    except Exception:
        pass


@frappe.whitelist()
def enviar(name: str, *, tipo: str, data: Dict | None = None, ambiente: str = "custom") -> Dict:
    doc: ECF = frappe.get_doc("e-CF", name)  # type: ignore
    # Validación previa opcional contra spec del tipo
    if data:
        spec_name = f"ecf{str(tipo)}.json"
        errs = validate_against_spec(data, spec_name=spec_name)
        if errs:
            frappe.throw("\n".join(errs))
        # reglas de negocio previas
        br_errs = validate_pre_send_basic(data)
        if br_errs:
            frappe.throw("\n".join(br_errs))

    # Envío en background
    job = frappe.enqueue(
        "csf_do.csf_do.doctype.e_cf.e_cf._send_job",
        queue="long",
        timeout=600,
        is_async=True,
        job_name=f"enviar-ecf-{name}",
        kwargs={"name": name, "tipo": tipo, "data": data, "ambiente": ambiente},
    )
    return {"status": "queued", "job_id": job.id}


def _send_job(name: str, tipo: str, data: Dict | None, ambiente: str) -> None:
    doc: ECF = frappe.get_doc("e-CF", name)  # type: ignore
    max_attempts = 3
    backoff = 5
    attempt = 0
    last_error = None
    while attempt < max_attempts:
        attempt += 1
        try:
            res = enviar_ecf_config(data or {}, tipo=str(tipo), ambiente=ambiente)
            _update_doc_from_result(doc, res)
            doc.estado_dgii = res.estado or "En Proceso"
            doc.last_response = frappe.as_json({"track_id": res.track_id, "estado": res.estado})
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return
        except Exception as e:  # noqa: BLE001
            last_error = build_friendly_error_message(e) or str(e)
            doc.errores = (doc.errores or "") + ("\n" + last_error)
            doc.logs = (doc.logs or "") + f"\nIntento {attempt}: {last_error}"
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.sleep(backoff)
            backoff = min(backoff * 2, 60)
    # agotó reintentos
    doc.estado_dgii = "Observado"
    doc.errores = (doc.errores or "") + ("\n" + (last_error or "Error desconocido"))
    doc.save(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist()
def consultar_estado(name: str, *, ambiente: str = "custom") -> Dict:
    doc: ECF = frappe.get_doc("e-CF", name)  # type: ignore
    if not doc.track_id:
        frappe.throw("No hay Track ID para consultar.")
    job = frappe.enqueue(
        "csf_do.csf_do.doctype.e_cf.e_cf._status_job",
        queue="short",
        timeout=300,
        is_async=True,
        job_name=f"estado-ecf-{name}",
        kwargs={"name": name, "ambiente": ambiente},
    )
    return {"status": "queued", "job_id": job.id}


def _status_job(name: str, ambiente: str) -> None:
    doc: ECF = frappe.get_doc("e-CF", name)  # type: ignore
    try:
        resp = consultar_estado_config(doc.track_id, ambiente=ambiente)
        estado = (resp or {}).get("estado") or doc.estado_dgii
        doc.estado_dgii = estado
        doc.last_response = frappe.as_json(resp or {})
        # Mensaje amigable si Observado/Rechazado
        if str(estado).lower() in ("observado", "rechazado"):
            friendly = build_friendly_error_message(resp)
            if friendly:
                doc.errores = (doc.errores or "") + ("\n" + friendly)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:  # noqa: BLE001
        doc.logs = (doc.logs or "") + f"\nConsulta estado fallida: {e}"
        doc.save(ignore_permissions=True)
        frappe.db.commit()


@frappe.whitelist()
def anular(name: str, motivo: str | None = None) -> Dict:
    # Placeholder: la DGII define proceso RFCE/Anulación específico
    doc: ECF = frappe.get_doc("e-CF", name)  # type: ignore
    doc.estado_dgii = "Anulado"
    doc.logs = (doc.logs or "") + f"\nAnulado manualmente. Motivo: {motivo or '-'}"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "ok", "estado": doc.estado_dgii}


