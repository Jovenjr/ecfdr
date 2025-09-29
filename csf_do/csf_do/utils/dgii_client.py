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

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from csf_do.csf_do.utils.dgii_config import get_active_dgii_config

# requests es opcional para no romper entornos sin conectividad/dep
try:  # pragma: no cover
    import requests  # type: ignore

    _HAS_REQUESTS = True
except Exception:  # pragma: no cover
    requests = None  # type: ignore
    _HAS_REQUESTS = False

try:  # pragma: no cover
    from .xml_signer import sign_with_pkcs12

    _HAS_SIGNER = True
except Exception:  # pragma: no cover
    sign_with_pkcs12 = None  # type: ignore
    _HAS_SIGNER = False


LOGGER = logging.getLogger(__name__)


@dataclass
class DGIIEnv:
    name: str
    base_url: str
    verify_ssl: bool
    timeout: int
    max_retries: int
    retry_backoff: int
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token_ttl: int = 3600
    estatus_api_key: Optional[str] = None


@dataclass
class Token:
    access_token: str
    expires_at: float

    def is_expired(self) -> bool:
        return time.time() >= self.expires_at


class DGIIClient:
    def __init__(self, env: DGIIEnv):
        self.env = env
        self._token: Optional[Token] = None
        self._circuit_open_until: Optional[float] = None
        self._last_status_check: float = 0

    # ---- Auth flow (stubs) ----
    def get_seed(self) -> str:
        """Request seed from DGII (stub)."""
        if not _HAS_REQUESTS:
            return "<Semilla>placeholder</Semilla>"

        url = self.endpoints().get("semilla") or f"{self.env.base_url.rstrip('/')}/semilla"
        try:
            resp = self._request("get", url)
            return resp.text
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("DGII seed request failed: %s", exc)
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
        if not _HAS_REQUESTS:
            return Token(access_token="stub-token", expires_at=time.time() + self.env.token_ttl)

        url = self.endpoints().get("token") or f"{self.env.base_url.rstrip('/')}/token"
        headers = {"Content-Type": "text/xml"}
        try:
            resp = self._request(
                "post",
                url,
                data=signed_seed_xml.encode("utf-8"),
                headers=headers,
            )
            resp.raise_for_status()
            data: Dict[str, Any] = {}
            if "application/json" in resp.headers.get("Content-Type", ""):
                data = resp.json()
            token_value = data.get("access_token") or resp.text.strip() or "stub-token"
            ttl_secs = int(data.get("expires_in") or self.env.token_ttl)
            return Token(access_token=token_value, expires_at=time.time() + ttl_secs)
        except Exception as exc:  # noqa: BLE001
            LOGGER.error("DGII token exchange failed: %s", exc)
            return Token(access_token="stub-token", expires_at=time.time() + self.env.token_ttl)

    def ensure_token(
        self,
        *,
        cert_path: str,
        key_path: str,
        p12_path: Optional[str] = None,
        p12_password: Optional[str] = None,
    ) -> str:
        if self._token is None or self._token.is_expired():
            seed = self.get_seed()
            signed = self.sign_seed(
                seed,
                cert_path=cert_path,
                key_path=key_path,
                p12_path=p12_path,
                p12_password=p12_password,
            )
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
            "recepcion_aprobacion": f"{base}/recepcion/aprobacion",
            "recepcion_rfce": f"{base}/recepcion/rfce",
            "consulta_resultado": f"{base}/consulta/resultado",
            "consulta_estado": f"{base}/consulta/estado",
            "consulta_resumen_rfce": f"{base}/consulta/rfce",
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
                resp = self._request("post", url, data=xml_payload.encode("utf-8"), headers=headers)
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
                resp = self._request("get", f"{url}/{track_id}", headers=headers)
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
                resp = self._request("get", f"{url}/{rnc}", headers=headers)
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
            timeout=int(cfg.get("timeout_seconds", 30)),
            max_retries=int(cfg.get("max_retries", 3)),
            retry_backoff=int(cfg.get("retry_backoff_seconds", 5)),
            token_ttl=int(cfg.get("ttl_token", 3600)),
            estatus_api_key=cfg.get("estatus_api_key"),
        )
        return DGIIClient(env)

    # ---- Internals -----------------------------------------------------------------
    def _request(self, method: str, url: str, **kwargs: Any):
        if not _HAS_REQUESTS:
            raise RuntimeError("Requests no disponible")

        now = time.time()
        if self._circuit_open_until and now < self._circuit_open_until:
            raise RuntimeError("Circuito DGII abierto temporalmente")

        headers = kwargs.pop("headers", {}) or {}
        kwargs["headers"] = headers
        kwargs.setdefault("timeout", self.env.timeout)
        kwargs.setdefault("verify", self.env.verify_ssl)

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.env.max_retries + 2):
            try:
                resp = requests.request(method.upper(), url, **kwargs)
                if resp.status_code >= 500:
                    raise RuntimeError(f"DGII 5xx: {resp.status_code}")
                return resp
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                LOGGER.warning("DGII request error (attempt %s/%s): %s", attempt, self.env.max_retries + 1, exc)
                if attempt > self.env.max_retries:
                    self._open_circuit()
                    self._maybe_check_service_status()
                    raise
                time.sleep(self.env.retry_backoff)
        if last_exc:
            raise last_exc

    def _open_circuit(self) -> None:
        self._circuit_open_until = time.time() + (self.env.retry_backoff * max(1, self.env.max_retries))

    def _maybe_check_service_status(self) -> None:
        if not self.env.estatus_api_key or not _HAS_REQUESTS:
            return
        now = time.time()
        if now - self._last_status_check < 60:
            return
        self._last_status_check = now
        url = f"{self.env.base_url.rstrip('/')}/api/estatusservicios/obtenerestatus"
        try:
            headers = {"Apikey": self.env.estatus_api_key}
            resp = requests.get(url, headers=headers, timeout=self.env.timeout, verify=self.env.verify_ssl)
            resp.raise_for_status()
            LOGGER.info("Estatus DGII: %s", resp.text)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("No se pudo verificar estatus DGII: %s", exc)
