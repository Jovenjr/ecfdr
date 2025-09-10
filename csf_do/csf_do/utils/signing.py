"""
Digital signing utilities for DGII e-CF integration.
- Interface for SHA-256 XML signatures
- Canonicalization note: no whitespace preservation (preserveWhitespace = False)

This module provides a pluggable interface. The actual cryptographic implementation
can be wired later using xmlsec or platform-specific providers (e.g., Viafirma SDK),
without changing call sites.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import hashlib


@dataclass
class SignatureResult:
    signed_xml: str
    signature_value: str
    signature_hash: str
    codigo_seguridad: str  # first 6 characters of the signature hash (per QR spec)


def sha256_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_codigo_seguridad(signature_hash_hex: str) -> str:
    return signature_hash_hex[:6]


def sign_xml(xml: str, *, cert_path: str, key_path: str, preserve_whitespace: bool = False) -> SignatureResult:
    """Sign an XML string and return the signed payload and metadata.

    Notes:
    - DGII expects signing with SHA-256.
    - Canonicalization must be performed without preserving whitespace.
    - This is a placeholder implementation that simulates a signature using SHA-256 of the input.
      Replace with a proper XMLDSig (XAdES/ETSI profile if required) implementation.
    """
    # In the placeholder, we ignore cert_path/key_path and whitespace setting.
    # Real implementation should:
    # 1) Canonicalize XML (exclusive c14n) with preserveWhitespace = False
    # 2) Build SignedInfo, Reference, DigestValue using SHA-256
    # 3) Sign with the private key associated to the certificate
    # 4) Embed Signature node into the XML

    # Placeholder: derive a deterministic signature hash for wiring downstream logic
    signature_hash = sha256_digest(xml.encode("utf-8"))
    signature_value = signature_hash  # stand-in; real impl would be base64 signature value
    codigo_seguridad = compute_codigo_seguridad(signature_hash)

    # For now, return original XML unchanged to respect immutability post-sign
    # The real implementation must inject the <Signature> element and return the modified XML.
    return SignatureResult(
        signed_xml=xml,
        signature_value=signature_value,
        signature_hash=signature_hash,
        codigo_seguridad=codigo_seguridad,
    )
