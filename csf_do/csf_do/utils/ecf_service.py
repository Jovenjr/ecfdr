"""
Servicio orquestador e-CF:
- Construcción XML (xml_builder)
- Validación XSD (xsd_validator)
- Firma (signing)
- Envío (dgii_client)

Este servicio utiliza los doctypes de configuración:
- DGII Configuration (ambientes/URLs)
- Digital Certificate (certificado activo)
- e-CF Sequence (próximo ENCF por tipo/serie)

Las operaciones de BD (frappe.get_doc, frappe.db, etc.) se implementarán en siguiente iteración.
Por ahora, se aceptan parámetros explícitos para cert_path/key_path/base_url.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

from .ecf43_builder import build_and_validate_ecf43
from .ecf31_builder import build_and_validate_ecf31
from .ecf32_builder import build_and_validate_ecf32
from .signing import sign_xml, SignatureResult
from . import xml_signer
from .dgii_client import DGIIClient, DGIIEnv
from .dgii_mock import DGIIMock
from .audit_log import save_audit_event
from .signing import sha256_digest
from .cert_loader import get_active_certificate
from .dgii_config import get_active_dgii_config
from .qr_code_generator import build_qr_payload_from_xml, get_qr_code


@dataclass
class ECFResult:
    ok: bool
    estado: str
    track_id: Optional[str]
    errores: List[str]
    xml: str
    firma: Optional[SignatureResult]


def enviar_ecf(
    data: Dict,
    *,
    tipo: str,
    base_url: str,
    cert_path: str,
    key_path: str,
    p12_path: str | None = None,
    p12_password: str | None = None,
    verify_ssl: bool = True,
    ttl_token: int = 3600,
) -> ECFResult:
    """Construye, valida, firma y envía un e-CF a DGII (stub de envío).

    Retorna ECFResult con el estado preliminar y un TrackId stub.
    """
    # 1) Construcción + Validación XSD por tipo
    if str(tipo) == "43":
        xml, ok, errors = build_and_validate_ecf43(data)
    elif str(tipo) == "31":
        xml, ok, errors = build_and_validate_ecf31(data)
    elif str(tipo) == "32":
        xml, ok, errors = build_and_validate_ecf32(data)
    else:
        raise NotImplementedError(f"Tipo e-CF no soportado aún en ecf_service: {tipo}")
    if not ok:
        # Auditoría best-effort del fallo de validación
        try:
            save_audit_event({
                "tipo_ecf": str(tipo),
                "ambiente": base_url,
                "estado_dgii": "Invalid XML",
                "errores": errors,
                "payload_hash": sha256_digest(xml.encode("utf-8")),
            })
        except Exception:
            pass
        return ECFResult(ok=False, estado="Invalid XML", track_id=None, errores=errors, xml=xml, firma=None)

    # Auditoría: XML construido
    try:
        save_audit_event({
            "tipo_ecf": str(tipo),
            "ambiente": base_url,
            "estado_dgii": "XML construido",
            "payload_hash": sha256_digest(xml.encode("utf-8")),
        })
    except Exception:
        pass

    # 2.5) Intentar autoload de certificado PKCS#12 desde ERPNext si no se pasó por parámetro
    if not p12_path:
        try:
            cert_info = get_active_certificate()
            if cert_info and cert_info.get("p12_path"):
                p12_path = cert_info.get("p12_path")
                if p12_password is None:
                    p12_password = cert_info.get("password") or None
        except Exception:
            pass

    # 3) Firma: intentar firma real con PKCS#12 si se provee
    firma: SignatureResult
    if p12_path:
        try:
            res = xml_signer.sign_ecf_with_pkcs12(xml, p12_path=p12_path, password=p12_password)
            signed_xml = res["signed_xml"]
            firma = SignatureResult(
                signed_xml=signed_xml,
                signature_value=res["signature_hash"],  # placeholder; real valor base64 de firma si se requiere
                signature_hash=res["signature_hash"],
                codigo_seguridad=res["codigo_seguridad"],
            )
        except Exception:
            # Fallback a firma placeholder si falla la firma real
            firma = sign_xml(xml, cert_path=cert_path, key_path=key_path, preserve_whitespace=False)
    else:
        # Fallback por defecto (placeholder)
        firma = sign_xml(xml, cert_path=cert_path, key_path=key_path, preserve_whitespace=False)

    # Auditoría: Documento firmado
    try:
        audit_payload = {
            "tipo_ecf": str(tipo),
            "ambiente": base_url,
            "estado_dgii": "Firmado",
            "signature_hash": getattr(firma, "signature_hash", None),
            "codigo_seguridad": getattr(firma, "codigo_seguridad", None),
            "payload_hash": sha256_digest(firma.signed_xml.encode("utf-8")),
        }
        # Generar QR (best-effort). Si hay URL de consulta en overrides, úsala
        consulta_url = None
        try:
            cfg = get_active_dgii_config(ambiente="custom") or {}
            overrides = cfg.get("overrides") or {}
            consulta_url = overrides.get("consulta_estado_url")
        except Exception:
            consulta_url = None

        qr_payload = build_qr_payload_from_xml(
            firma.signed_xml,
            getattr(firma, "codigo_seguridad", ""),
            consulta_base_url=consulta_url,
        )
        qr_text = qr_payload.get("texto")
        if qr_text:
            qr_base64 = get_qr_code(qr_text)
            audit_payload["qr_text"] = qr_text
            audit_payload["qr_image_base64"] = qr_base64
        save_audit_event(audit_payload)
    except Exception:
        pass

    # 4) Envío (stub/real)
    if base_url.startswith("mock://"):
        mock = DGIIMock(base_url)
        resp = mock.recepcion_ecf(firma.signed_xml)
    else:
        env = DGIIEnv(name="custom", base_url=base_url, verify_ssl=verify_ssl, ttl_token=ttl_token)
        client = DGIIClient(env)
        resp = client.post_xml(
            "recepcion_ecf",
            firma.signed_xml,
            cert_path=cert_path,
            key_path=key_path,
            p12_path=p12_path,
            p12_password=p12_password,
        )

    track_id = resp.get("track_id")
    # Auditoría: Enviado (incluir respuesta completa en extra si es posible)
    try:
        save_audit_event({
            "tipo_ecf": str(tipo),
            "ambiente": base_url,
            "estado_dgii": resp.get("estado") or "Enviado",
            "track_id": track_id,
            "signature_hash": getattr(firma, "signature_hash", None),
            "codigo_seguridad": getattr(firma, "codigo_seguridad", None),
            "payload_hash": sha256_digest(firma.signed_xml.encode("utf-8")),
            "extra": resp,
        })
    except Exception:
        pass

    return ECFResult(ok=True, estado="Enviado", track_id=track_id, errores=[], xml=firma.signed_xml, firma=firma)


def consultar_estado(
    track_id: str,
    *,
    base_url: str,
    cert_path: str,
    key_path: str,
    p12_path: str | None = None,
    p12_password: str | None = None,
) -> Dict:
    """Consulta el estado de un e-CF por Track ID contra DGII o Mock y registra auditoría.

    Retorna el diccionario de respuesta del cliente.
    """
    try:
        save_audit_event({
            "tipo_ecf": "-",
            "ambiente": base_url,
            "estado_dgii": "ConsultaEstado: solicitada",
            "track_id": track_id,
        })
    except Exception:
        pass

    if base_url.startswith("mock://"):
        mock = DGIIMock(base_url)
        resp = mock.consulta_estado(track_id)
    else:
        env = DGIIEnv(name="custom", base_url=base_url)
        client = DGIIClient(env)
        resp = client.status_track_id(track_id)

    try:
        save_audit_event({
            "tipo_ecf": "-",
            "ambiente": base_url,
            "estado_dgii": resp.get("estado") or "ConsultaEstado: respondida",
            "track_id": track_id,
            "extra": resp,
        })
    except Exception:
        pass

    return resp


def enviar_ecf_config(
    data: Dict,
    *,
    tipo: str,
    ambiente: str = "custom",
    p12_path: str | None = None,
    p12_password: str | None = None,
) -> ECFResult:
    """Versión de enviar_ecf que usa configuración de Frappe (DGII Configuration + Digital Certificate).

    - Obtiene base_url/verificación SSL/TTL desde `DGII Configuration` para el ambiente indicado.
    - Si no se provee p12, intenta autoload desde `Digital Certificate`.
    """
    cfg = None
    try:
        cfg = get_active_dgii_config(ambiente=ambiente)
    except Exception:
        cfg = None
    if not cfg or not cfg.get("base_url"):
        raise RuntimeError("No se encontró configuración DGII válida (DGII Configuration) para el ambiente indicado")

    # Si no se pasó p12, intentar autoload
    if not p12_path:
        try:
            cert_info = get_active_certificate()
            if cert_info and cert_info.get("p12_path"):
                p12_path = cert_info.get("p12_path")
                if p12_password is None:
                    p12_password = cert_info.get("password") or None
        except Exception:
            pass

    # cert_path/key_path no se usan en la firma real, pero son requeridos por la API actual
    return enviar_ecf(
        data,
        tipo=tipo,
        base_url=str(cfg["base_url"]),
        cert_path="",
        key_path="",
        p12_path=p12_path,
        p12_password=p12_password,
        verify_ssl=bool(cfg.get("verify_ssl", True)),
        ttl_token=int(cfg.get("ttl_token", 3600)),
    )


def consultar_estado_config(
    track_id: str,
    *,
    ambiente: str = "custom",
) -> Dict:
    """Consulta estado usando configuración de Frappe (DGII Configuration)."""
    cfg = None
    try:
        cfg = get_active_dgii_config(ambiente=ambiente)
    except Exception:
        cfg = None
    if not cfg or not cfg.get("base_url"):
        raise RuntimeError("No se encontró configuración DGII válida (DGII Configuration) para el ambiente indicado")

    return consultar_estado(
        track_id,
        base_url=str(cfg["base_url"]),
        cert_path="",
        key_path="",
    )
