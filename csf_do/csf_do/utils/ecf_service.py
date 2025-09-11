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
from .ecf33_builder import build_and_validate_ecf33
from .ecf34_builder import build_and_validate_ecf34
from .ecf41_builder import build_and_validate_ecf41
from .ecf44_builder import build_and_validate_ecf44
from .ecf45_builder import build_and_validate_ecf45
from .ecf46_builder import build_and_validate_ecf46
from .ecf47_builder import build_and_validate_ecf47
from .signing import sign_xml, SignatureResult
from . import xml_signer
from .dgii_client import DGIIClient, DGIIEnv
from .dgii_mock import DGIIMock
from .audit_log import save_audit_event
from .signing import sha256_digest
from .cert_loader import get_active_certificate
from .dgii_config import get_active_dgii_config
from .qr_code_generator import build_qr_payload_from_xml, get_qr_code
from .rfce32_builder import build_and_validate_rfce32
from .xsd_validator import validate_xml
from xml.etree import ElementTree as ET


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
    tipo_str = str(tipo)
    if tipo_str == "43":
        xml, ok, errors = build_and_validate_ecf43(data)
    elif tipo_str == "31":
        xml, ok, errors = build_and_validate_ecf31(data)
    elif tipo_str == "32":
        xml, ok, errors = build_and_validate_ecf32(data)
    elif tipo_str == "33":
        xml, ok, errors = build_and_validate_ecf33(data)
    elif tipo_str == "34":
        xml, ok, errors = build_and_validate_ecf34(data)
    elif tipo_str == "41":
        xml, ok, errors = build_and_validate_ecf41(data)
    elif tipo_str == "44":
        xml, ok, errors = build_and_validate_ecf44(data)
    elif tipo_str == "45":
        xml, ok, errors = build_and_validate_ecf45(data)
    elif tipo_str == "46":
        xml, ok, errors = build_and_validate_ecf46(data)
    elif tipo_str == "47":
        xml, ok, errors = build_and_validate_ecf47(data)
    else:
        raise NotImplementedError(f"Tipo e-CF no soportado en ecf_service: {tipo}")
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


def anular_encf(
    *,
    rnc_emisor: str,
    anulaciones: List[Dict],
    base_url: str,
    p12_path: str | None = None,
    p12_password: str | None = None,
    verify_ssl: bool = True,
    ttl_token: int = 3600,
) -> Dict:
    """Genera XML ANECF, firma e intenta enviar la anulación a DGII.

    anulaciones: lista de items con llaves: NoLinea, TipoeCF, rangos (Desde/Hasta)
    """
    from xml.etree import ElementTree as ET
    from datetime import datetime
    # Construcción ANECF mínima
    root = ET.Element("ANECF")
    encabezado = ET.SubElement(root, "Encabezado")
    ET.SubElement(encabezado, "Version").text = "1.0"
    ET.SubElement(encabezado, "RncEmisor").text = str(rnc_emisor)
    ET.SubElement(encabezado, "CantidadeNCFAnulados").text = str(sum(int(a.get("Cantidad", 0)) for a in anulaciones) or len(anulaciones))
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    ET.SubElement(encabezado, "FechaHoraAnulacioneNCF").text = now

    detalle = ET.SubElement(root, "DetalleAnulacion")
    for a in anulaciones:
        ann = ET.SubElement(detalle, "Anulacion")
        ET.SubElement(ann, "NoLinea").text = str(a.get("NoLinea") or 1)
        ET.SubElement(ann, "TipoeCF").text = str(a.get("TipoeCF"))
        tabla = ET.SubElement(ann, "TablaRangoSecuenciasAnuladaseNCF")
        secs = ET.SubElement(tabla, "Secuencias")
        ET.SubElement(secs, "SecuenciaeNCFDesde").text = str(a.get("Desde"))
        ET.SubElement(secs, "SecuenciaeNCFHasta").text = str(a.get("Hasta"))
        ET.SubElement(ann, "CantidadeNCFAnulados").text = str(a.get("Cantidad") or 1)

    # xs:any
    ET.SubElement(root, "Signature").text = "-"
    xml = ET.tostring(root, encoding="utf-8").decode("utf-8")

    # Validar contra XSD si es posible
    try:
        validate_xml(xml, xsd_name="ANECF v.1.0.xsd")
    except Exception:
        pass

    # Firma ANECF
    if not p12_path:
        try:
            cert_info = get_active_certificate()
            if cert_info and cert_info.get("p12_path"):
                p12_path = cert_info.get("p12_path")
                if p12_password is None:
                    p12_password = cert_info.get("password") or None
        except Exception:
            pass

    try:
        if p12_path:
            res = xml_signer.sign_with_pkcs12(xml, p12_path=p12_path, password=p12_password, target_tag="ANECF")
            signed_xml = res["signed_xml"]
        else:
            signed_xml = xml
    except Exception:
        signed_xml = xml

    # Enviar
    if base_url.startswith("mock://"):
        mock = DGIIMock(base_url)
        resp = mock.recepcion_ecf(signed_xml)
    else:
        env = DGIIEnv(name="custom", base_url=base_url, verify_ssl=verify_ssl, ttl_token=ttl_token)
        client = DGIIClient(env)
        resp = client.post_xml(
            "anulacion_encf",
            signed_xml,
            cert_path="",
            key_path="",
            p12_path=p12_path,
            p12_password=p12_password,
        )

    try:
        save_audit_event({
            "tipo_ecf": "ANECF",
            "ambiente": base_url,
            "estado_dgii": resp.get("estado") or "Enviado",
            "track_id": resp.get("track_id"),
            "payload_hash": sha256_digest(signed_xml.encode("utf-8")),
            "extra": resp,
        })
    except Exception:
        pass

    return resp


def enviar_rfce32_config(
    data: Dict,
    *,
    ambiente: str = "custom",
    p12_path: str | None = None,
    p12_password: str | None = None,
) -> Dict:
    """Wrapper que usa `DGII Configuration` y `Digital Certificate` para enviar RFCE."""
    cfg = get_active_dgii_config(ambiente=ambiente)
    if not cfg or not cfg.get("base_url"):
        raise RuntimeError("No se encontró configuración DGII válida para RFCE")
    if not p12_path:
        try:
            cert_info = get_active_certificate()
            if cert_info and cert_info.get("p12_path"):
                p12_path = cert_info.get("p12_path")
                if p12_password is None:
                    p12_password = cert_info.get("password") or None
        except Exception:
            pass
    return enviar_rfce32(
        data,
        base_url=str(cfg["base_url"]),
        cert_path="",
        key_path="",
        p12_path=p12_path,
        p12_password=p12_password,
        verify_ssl=bool(cfg.get("verify_ssl", True)),
        ttl_token=int(cfg.get("ttl_token", 3600)),
    )


def consultar_resumen_rfce32_config(
    *,
    ambiente: str = "custom",
) -> Dict:
    cfg = get_active_dgii_config(ambiente=ambiente)
    if not cfg or not cfg.get("base_url"):
        raise RuntimeError("No se encontró configuración DGII válida para consulta RFCE")
    return consultar_resumen_rfce32(
        base_url=str(cfg["base_url"]),
        verify_ssl=bool(cfg.get("verify_ssl", True)),
        ttl_token=int(cfg.get("ttl_token", 3600)),
    )


def recepcion_aprobacion_comercial(
    data_xml: str,
    *,
    base_url: str,
    verify_ssl: bool = True,
    ttl_token: int = 3600,
) -> Dict:
    """Envía un XML de Aprobación/Rechazo Comercial (ACECF/ARECF) a DGII."""
    # Validar que raíz sea ACECF o ARECF para nocaut temprano
    try:
        root = ET.fromstring(data_xml)
        if root.tag not in ("ACECF", "ARECF"):
            raise ValueError("XML no corresponde a ACECF/ARECF")
    except Exception:
        return {"ok": False, "error": "XML inválido ACECF/ARECF"}

    if base_url.startswith("mock://"):
        mock = DGIIMock(base_url)
        resp = mock.recepcion_ecf(data_xml)
    else:
        env = DGIIEnv(name="custom", base_url=base_url, verify_ssl=verify_ssl, ttl_token=ttl_token)
        client = DGIIClient(env)
        resp = client.post_xml("recepcion_aprobacion", data_xml, cert_path="", key_path="")

    try:
        save_audit_event({
            "tipo_ecf": root.tag,
            "ambiente": base_url,
            "estado_dgii": resp.get("estado") or "Enviado",
            "track_id": resp.get("track_id"),
            "payload_hash": sha256_digest(data_xml.encode("utf-8")),
            "extra": resp,
        })
    except Exception:
        pass
    return resp


def enviar_rfce32(
    data: Dict,
    *,
    base_url: str,
    cert_path: str,
    key_path: str,
    p12_path: str | None = None,
    p12_password: str | None = None,
    verify_ssl: bool = True,
    ttl_token: int = 3600,
) -> Dict:
    """Construye, firma y envía un RFCE 32 a DGII."""
    xml, ok, errors = build_and_validate_rfce32(data)
    if not ok:
        return {"ok": False, "estado": "Invalid XML", "errores": errors, "track_id": None}

    # Firma RFCE: firmar el tag RFCE con PKCS#12 si disponible
    if not p12_path:
        try:
            cert_info = get_active_certificate()
            if cert_info and cert_info.get("p12_path"):
                p12_path = cert_info.get("p12_path")
                if p12_password is None:
                    p12_password = cert_info.get("password") or None
        except Exception:
            pass

    try:
        if p12_path:
            res = xml_signer.sign_with_pkcs12(xml, p12_path=p12_path, password=p12_password, target_tag="RFCE")
            signed_xml = res["signed_xml"]
        else:
            # placeholder: usar firma simple que no altera el XML
            signed_xml = xml
    except Exception:
        signed_xml = xml

    if base_url.startswith("mock://"):
        mock = DGIIMock(base_url)
        resp = mock.recepcion_ecf(signed_xml)
    else:
        env = DGIIEnv(name="custom", base_url=base_url, verify_ssl=verify_ssl, ttl_token=ttl_token)
        client = DGIIClient(env)
        resp = client.post_xml(
            "recepcion_rfce",
            signed_xml,
            cert_path=cert_path,
            key_path=key_path,
            p12_path=p12_path,
            p12_password=p12_password,
        )

    try:
        save_audit_event({
            "tipo_ecf": "RFCE32",
            "ambiente": base_url,
            "estado_dgii": resp.get("estado") or "Enviado",
            "track_id": resp.get("track_id"),
            "payload_hash": sha256_digest(signed_xml.encode("utf-8")),
            "extra": resp,
        })
    except Exception:
        pass

    return resp


def consultar_resumen_rfce32(
    *,
    base_url: str,
    verify_ssl: bool = True,
    ttl_token: int = 3600,
) -> Dict:
    """Consulta el resumen RFCE 32 (endpoint dedicado)."""
    if base_url.startswith("mock://"):
        return {"status": "stub", "resumen": []}
    env = DGIIEnv(name="custom", base_url=base_url, verify_ssl=verify_ssl, ttl_token=ttl_token)
    client = DGIIClient(env)
    url = client.endpoints().get("consulta_resumen_rfce")
    try:
        import requests  # type: ignore
        token = client.ensure_token(cert_path="", key_path="")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers, timeout=20, verify=verify_ssl)
        resp.raise_for_status()
        return resp.json() if "application/json" in resp.headers.get("Content-Type", "") else {"raw": resp.text}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


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
