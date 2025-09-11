from __future__ import annotations
from typing import Any, Dict, Optional


_CODE_TO_MESSAGE = {
    # Placeholders; ajustar cuando se conozcan códigos reales DGII
    "0": "En Proceso",
    "1": "Aceptado",
    "2": "Observado por DGII",
    "3": "Rechazado por DGII",
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


