"""
DGII client stubs for e-CF integration.
Implements the authentication/token flow placeholders and service endpoints registry.

Flow (high level):
1) Obtain "semilla" (seed) from DGII.
2) Sign the seed XML with the contributor's digital certificate (SHA-256, no whitespace preservation).
3) Exchange the signed seed for a bearer token (valid ~1 hour).
4) Use the token in Authorization headers for subsequent calls.

This module provides a typed interface and environment configuration. Replace the HTTP stubs
with real requests once endpoints and credentials are configured.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time
import re

# requests es opcional para no romper entornos sin conectividad/dep
try:  # pragma: no cover
    import requests  # type: ignore
    _HAS_REQUESTS = True
except Exception:  # pragma: no cover
    requests = None  # type: ignore
    _HAS_REQUESTS = False

# Firma opcional
try:  # pragma: no cover
    from .xml_signer import sign_with_pkcs12
    _HAS_SIGNER = True
except Exception:  # pragma: no cover
    sign_with_pkcs12 = None  # type: ignore
    _HAS_SIGNER = False


@dataclass
class DGIIEnv:
    name: str  # e.g., precert, cert, prod
    base_url: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    verify_ssl: bool = True
    ttl_token: int = 3600  # segundos


@dataclass
class Token:
    access_token: str
    expires_at: float  # epoch seconds

    def is_expired(self) -> bool:
        return time.time() >= self.expires_at


class DGIIClient:
    def __init__(self, env: DGIIEnv):
        self.env = env
        self._token: Optional[Token] = None

    # ---- Auth flow (stubs) ----
    def get_seed(self) -> str:
        """Request seed from DGII (stub)."""
        # Intento real si requests está disponible y el endpoint está definido
        if _HAS_REQUESTS:
            try:
                url = self.endpoints().get("semilla") or f"{self.env.base_url.rstrip('/')}/semilla"
                resp = requests.get(url, timeout=20, verify=self.env.verify_ssl)
                resp.raise_for_status()
                return resp.text
            except Exception:
                pass
        # Fallback stub
        return "<Semilla>placeholder</Semilla>"

    def sign_seed(self, seed_xml: str, *, cert_path: str, key_path: str, p12_path: Optional[str] = None, p12_password: Optional[str] = None) -> str:
        """Sign the seed using the configured certificate (stub)."""
        # Si tenemos un PKCS#12 y xml_signer disponible, firmar la semilla con target_tag 'SemillaModel'
        # Nota: cert_path/key_path aún no se usan; en el futuro podemos soportar PEM.
        if _HAS_SIGNER and p12_path:
            try:
                res = sign_with_pkcs12(seed_xml, p12_path=p12_path, password=p12_password, target_tag='SemillaModel')
                return res["signed_xml"]
            except Exception:
                # fallback al contenido original si la firma falla
                return seed_xml
        return seed_xml  # placeholder

    def exchange_token(self, signed_seed_xml: str) -> Token:
        """Exchange signed seed for a bearer token (stub)."""
        # Intento real si requests está disponible
        if _HAS_REQUESTS:
            try:
                url = self.endpoints().get("token") or f"{self.env.base_url.rstrip('/')}/token"
                headers = {"Content-Type": "text/xml"}
                resp = requests.post(url, data=signed_seed_xml.encode("utf-8"), headers=headers, timeout=20, verify=self.env.verify_ssl)
                resp.raise_for_status()
                data = resp.json() if "application/json" in resp.headers.get("Content-Type", "") else None
                access = (data or {}).get("access_token") if data else None
                ttl = (data or {}).get("expires_in") if data else None
                if not access:
                    # como fallback, use el cuerpo como token
                    access = resp.text.strip() or "stub-token"
                ttl_secs = int(ttl) if ttl else int(self.env.ttl_token or 3600)
                return Token(access_token=access, expires_at=time.time() + ttl_secs)
            except Exception:
                pass
        # Fallback stub
        return Token(access_token="stub-token", expires_at=time.time() + int(self.env.ttl_token or 3600))

    def ensure_token(self, *, cert_path: str, key_path: str, p12_path: Optional[str] = None, p12_password: Optional[str] = None) -> str:
        if self._token is None or self._token.is_expired():
            seed = self.get_seed()
            signed = self.sign_seed(seed, cert_path=cert_path, key_path=key_path, p12_path=p12_path, p12_password=p12_password)
            self._token = self.exchange_token(signed)
        return self._token.access_token

    # ---- Endpoints registry (expand as needed) ----
    def endpoints(self) -> Dict[str, str]:
        base = self.env.base_url.rstrip("/")
        # Intentar leer overrides desde configuración si está disponible
        overrides: Dict[str, str] = {}
        try:
            from .dgii_config import get_active_dgii_config  # type: ignore
            cfg = get_active_dgii_config(ambiente=self.env.name) or {}
            overrides = (cfg.get("overrides") or {}) if isinstance(cfg, dict) else {}
        except Exception:
            overrides = {}
        defaults = {
            "semilla": f"{base}/auth/semilla",
            "token": f"{base}/auth/token",
            "recepcion_ecf": f"{base}/recepcion/ecf",
            "recepcion_rfce": f"{base}/recepcion/rfce",
            "consulta_resultado": f"{base}/consulta/resultado",
            "consulta_estado": f"{base}/consulta/estado",
            "consulta_resumen_rfce": f"{base}/consulta/rfce",
            "recepcion_aprobacion": f"{base}/recepcion/aprobacion",
            "anulacion_encf": f"{base}/anulacion/encf",
            "directorio_servicios": f"{base}/directorio/servicios",
            "consulta_timbre": f"{base}/consulta/timbre",
            "consulta_timbre_fc": f"{base}/consulta/timbre-fc",
            "estatus_servicios": f"{base}/estatus",
        }
        # Mapear nombres de override a llaves internas
        mapping = {
            "auth_semilla_url": "semilla",
            "auth_token_url": "token",
            "recepcion_ecf_url": "recepcion_ecf",
            "consulta_estado_url": "consulta_estado",
            "directorio_servicios_url": "directorio_servicios",
        }
        for o_key, d_key in mapping.items():
            val = overrides.get(o_key)
            if val:
                defaults[d_key] = str(val)
        return defaults

    # ---- Service call placeholders ----
    def post_xml(self, path_key: str, xml_payload: str, *, cert_path: str, key_path: str, p12_path: Optional[str] = None, p12_password: Optional[str] = None) -> Dict[str, Any]:
        """POST an XML payload to a DGII service (stub)."""
        token = self.ensure_token(cert_path=cert_path, key_path=key_path, p12_path=p12_path, p12_password=p12_password)
        url = self.endpoints()[path_key]
        if _HAS_REQUESTS:
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "text/xml; charset=utf-8",
                }
                resp = requests.post(url, data=xml_payload.encode("utf-8"), headers=headers, timeout=30, verify=self.env.verify_ssl)
                resp.raise_for_status()
                content_type = resp.headers.get("Content-Type", "")
                # La DGII puede responder JSON o XML; detectar y extraer track_id/estado
                data: Dict[str, Any] = {}
                if "application/json" in content_type:
                    try:
                        data = resp.json()
                    except Exception:
                        data = {"raw": resp.text}
                else:
                    body = resp.text
                    data = {"raw": body}
                    # intentar extraer track id desde XML con regex simple
                    m = re.search(r"<TrackId>(.*?)</TrackId>", body, re.IGNORECASE)
                    if m:
                        data["track_id"] = m.group(1).strip()
                    m2 = re.search(r"<Estado>(.*?)</Estado>", body, re.IGNORECASE)
                    if m2:
                        data["estado"] = m2.group(1).strip()
                # TrackId puede venir como campo dedicado o en el cuerpo
                track_id = data.get("track_id") if isinstance(data, dict) else None
                if not track_id:
                    track_id = "TRACK-STUB-HTTP"  # placeholder si no se puede extraer
                return {"url": url, "status": "http", "track_id": track_id, **data}
            except Exception:
                pass
        # Fallback stub si falla HTTP o no hay requests
        return {"url": url, "status": "stub", "track_id": "TRACK-STUB-12345"}

    # ---- Consultas ----
    def status_track_id(self, track_id: str) -> Dict[str, Any]:
        """Consulta el estado de un Track ID."""
        url = self.endpoints().get("consulta_estado")
        if _HAS_REQUESTS and url:
            try:
                token = self.ensure_token(cert_path="", key_path="")
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.get(f"{url}/{track_id}", headers=headers, timeout=20, verify=self.env.verify_ssl)
                resp.raise_for_status()
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    try:
                        data = resp.json()
                    except Exception:
                        data = {"raw": resp.text}
                else:
                    body = resp.text
                    data = {"raw": body}
                    m = re.search(r"<Estado>(.*?)</Estado>", body, re.IGNORECASE)
                    if m:
                        data["estado"] = m.group(1).strip()
                    m2 = re.search(r"<Codigo>(.*?)</Codigo>", body, re.IGNORECASE)
                    if m2:
                        data["codigo"] = m2.group(1).strip()
                return data
            except Exception:
                pass
        # Fallback stub
        return {"track_id": track_id, "estado": "En Proceso", "codigo": "0"}

    def get_customer_directory(self, rnc: str) -> Dict[str, Any]:
        """Obtiene el directorio de servicios disponibles para un RNC receptor."""
        url = self.endpoints().get("directorio_servicios")
        if _HAS_REQUESTS and url:
            try:
                token = self.ensure_token(cert_path="", key_path="")
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.get(f"{url}/{rnc}", headers=headers, timeout=20, verify=self.env.verify_ssl)
                resp.raise_for_status()
                if "application/json" in resp.headers.get("Content-Type", ""):
                    return resp.json()
                return {"raw": resp.text}
            except Exception:
                pass
        return {"rnc": rnc, "ambientes": []}

    # ---- Helpers de fábrica ----
    @staticmethod
    def from_configuration(ambiente: str = "custom") -> Optional["DGIIClient"]:
        """Crea un cliente leyendo el Doctype "DGII Configuration", si existe.
        Retorna None si la configuración no está disponible.
        """
        try:
            from .dgii_config import get_active_dgii_config
        except Exception:
            return None
        cfg = get_active_dgii_config(ambiente=ambiente)
        if not cfg:
            return None
        env = DGIIEnv(
            name=ambiente,
            base_url=cfg.get("base_url"),
            client_id=cfg.get("client_id"),
            client_secret=cfg.get("client_secret"),
            verify_ssl=bool(cfg.get("verify_ssl", True)),
            ttl_token=int(cfg.get("ttl_token", 3600)),
        )
        return DGIIClient(env)
