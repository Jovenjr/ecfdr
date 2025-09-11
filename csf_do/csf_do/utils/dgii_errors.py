from __future__ import annotations
from typing import Any, Dict, Optional


_CODE_TO_MESSAGE = {
    # Nota: estos códigos son ilustrativos y deben ajustarse a la tabla oficial DGII
    "0": "En Proceso",
    "1": "Aceptado",
    "2": "Observado",
    "3": "Rechazado",
    "400": "Solicitud inválida",
    "401": "No autorizado (token inválido/expirado)",
    "403": "Prohibido (credenciales insuficientes)",
    "404": "No encontrado",
    "408": "Tiempo de espera excedido",
    "422": "Validación fallida (estructura o reglas)",
    "429": "Demasiadas solicitudes (rate limit)",
    "500": "Error interno del servicio DGII",
}


def build_friendly_error_message(data: Any) -> Optional[str]:
    """Intenta producir un mensaje claro basado en respuesta DGII o excepción.

    Acepta dicts con campos comunes como 'codigo', 'mensaje', 'detalle', 'errors', o una Exception.
    Retorna None si no se puede construir algo significativo.
    """
    if data is None:
        return None
    # Si es excepción, usa su string
    if isinstance(data, Exception):
        msg = str(data).strip()
        return msg or None
    # Si es dict, prioriza campos
    if isinstance(data, dict):
        codigo = str(data.get("codigo") or data.get("code") or "").strip()
        estado = str(data.get("estado") or "").strip()
        mensaje = (
            data.get("mensaje")
            or data.get("message")
            or data.get("detalle")
            or data.get("detail")
            or None
        )
        if codigo and not mensaje:
            base = _CODE_TO_MESSAGE.get(codigo)
            if base:
                return f"{base} (código {codigo})"
        if mensaje:
            if codigo:
                return f"{mensaje} (código {codigo})"
            return str(mensaje)
        # Fallback a estado si es Observado/Rechazado/En Proceso
        if estado:
            return estado
        raw = data.get("raw")
        if raw:
            return str(raw)[:400]
    # Fallback a str genérico
    try:
        s = str(data)
        return s if s else None
    except Exception:
        return None


