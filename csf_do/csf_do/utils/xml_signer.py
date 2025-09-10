"""
Firma XML real para e-CF usando signxml (fallback) y soporte de certificados PKCS#12 (p12/pfx).

Requisitos recomendados:
- lxml (ya añadido)
- signxml (pip install signxml)
- cryptography (pip install cryptography)

Uso básico:
    from csf_do.csf_do.utils.xml_signer import sign_ecf_with_pkcs12
    result = sign_ecf_with_pkcs12(xml, p12_path="/ruta/cert.p12", password="secreto")
    signed_xml = result["signed_xml"]
    firma_hash = result["signature_hash"]
    codigo_seguridad = result["codigo_seguridad"]

Notas DGII:
- SHA-256
- Canonicalización exclusiva sin comentarios
- Firma enveloped en el nodo raíz <ECF>
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from hashlib import sha256

# Dependencias opcionales (no forzamos instalación para no romper entorno)
try:
    from signxml import XMLSigner, methods
    from lxml import etree
    _HAS_SIGNXML = True
except Exception:  # pragma: no cover
    XMLSigner = None  # type: ignore
    methods = None  # type: ignore
    algorithms = None  # type: ignore
    etree = None  # type: ignore
    _HAS_SIGNXML = False

try:
    from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
    from cryptography.hazmat.backends import default_backend
    _HAS_CRYPTO = True
except Exception:  # pragma: no cover
    load_key_and_certificates = None  # type: ignore
    default_backend = None  # type: ignore
    _HAS_CRYPTO = False


class XMLSigningUnavailable(Exception):
    pass


def _load_pkcs12(p12_path: str, password: Optional[str]):
    if not _HAS_CRYPTO:
        raise XMLSigningUnavailable("cryptography no está disponible. Instala 'cryptography'.")
    with open(p12_path, "rb") as f:
        data = f.read()
    pwd_bytes = password.encode("utf-8") if password is not None else None
    key, cert, extra = load_key_and_certificates(data, pwd_bytes, default_backend())
    if key is None or cert is None:
        raise ValueError("No se pudo extraer clave o certificado del PKCS#12.")
    # Convertir a PEM
    from cryptography.hazmat.primitives import serialization
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    return key_pem, cert_pem


def _compute_codigo_seguridad(signed_xml_bytes: bytes) -> Dict[str, str]:
    h = sha256(signed_xml_bytes).hexdigest()
    return {"signature_hash": h, "codigo_seguridad": h[:6]}


def sign_ecf_with_pkcs12(xml: str, *, p12_path: str, password: Optional[str]) -> Dict[str, Any]:
    """Firma el nodo raíz del XML (e.g., ECF) con un certificado PKCS#12 usando signxml.

    Retorna dict con: signed_xml, signature_hash, codigo_seguridad
    """
    if not _HAS_SIGNXML:
        raise XMLSigningUnavailable("signxml no está disponible. Instala 'signxml'.")

    key_pem, cert_pem = _load_pkcs12(p12_path, password)

    # Preparar documento
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(xml.encode("utf-8"), parser)

    # Configurar signer: Enveloped, SHA256, Exclusive C14N (sin comentarios)
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        # Exclusive Canonicalization (without comments)
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
    )

    # Firmar sobre el nodo raíz
    signed_root = signer.sign(root, key=key_pem, cert=cert_pem)

    # Serializar
    signed_xml_bytes = etree.tostring(signed_root, encoding="utf-8")
    meta = _compute_codigo_seguridad(signed_xml_bytes)

    return {
        "signed_xml": signed_xml_bytes.decode("utf-8"),
        **meta,
    }


def sign_with_pkcs12(xml: str, *, p12_path: str, password: Optional[str], target_tag: str) -> Dict[str, Any]:
    """Firma un tag específico (por nombre) dentro del XML usando signxml (enveloped).

    - target_tag: nombre del elemento a firmar, p. ej. 'ECF', 'SemillaModel', 'RFCE'.
    - Inserta <Signature> como hijo del elemento objetivo.

    Retorna dict con: signed_xml, signature_hash, codigo_seguridad.
    """
    if not _HAS_SIGNXML:
        raise XMLSigningUnavailable("signxml no está disponible. Instala 'signxml'.")

    key_pem, cert_pem = _load_pkcs12(p12_path, password)

    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(xml.encode("utf-8"), parser)

    # Localizar objetivo
    target = root if root.tag == target_tag else root.find(f'.//{target_tag}')
    if target is None:
        raise ValueError(f"No se encontró el tag objetivo '{target_tag}' para firmar")

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
    )

    signed_target = signer.sign(target, key=key_pem, cert=cert_pem)

    # Si el objetivo es la raíz, reemplazar root completo
    if target is root:
        signed_root = signed_target
    else:
        # Reemplazar el subelemento objetivo por su versión firmada
        parent = target.getparent() if hasattr(target, 'getparent') else None
        if parent is None:
            # lxml elementtree de signxml provee getparent; si no, regeneramos árbol
            # Para simplicidad, si no hay getparent, firmamos el documento completo
            signed_root = signer.sign(root, key=key_pem, cert=cert_pem)
        else:
            parent.replace(target, signed_target)
            signed_root = root

    signed_xml_bytes = etree.tostring(signed_root, encoding="utf-8")
    meta = _compute_codigo_seguridad(signed_xml_bytes)
    return {
        "signed_xml": signed_xml_bytes.decode("utf-8"),
        **meta,
    }
