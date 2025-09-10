"""
Validadores de formato previos al XSD para e-CF.

Incluye validaciones más amigables para:
- eNCF: 13 caracteres alfanuméricos
- RNC/Cédula: 9 o 11 dígitos
- Teléfono: ddd-ddd-dddd
- Email: patrón básico (máx 80)

Estas validaciones no sustituyen la validación XSD, pero entregan
mensajes más claros antes de construir/validar contra el esquema.
"""
from __future__ import annotations
import re
from typing import Optional


_RE_ENCF = re.compile(r"^[A-Za-z0-9]{13}$")
_RE_RNC = re.compile(r"^(\d{9}|\d{11})$")
_RE_PHONE = re.compile(r"^\d{3}-\d{3}-\d{4}$")
_RE_EMAIL = re.compile(r"^\w+([-+. ]\w+)*@\w+([-. ]\w+)*\.\w+([-. ]\w+)*$")


def validate_encf(value: Optional[str]) -> None:
    if value is None or value == "":
        return
    if not _RE_ENCF.match(str(value)):
        raise ValueError(f"eNCF inválido: '{value}'. Debe tener 13 caracteres alfanuméricos.")


def validate_rnc(value: Optional[str], *, field_name: str = "RNC") -> None:
    if value is None or value == "":
        return
    if not _RE_RNC.match(str(value)):
        raise ValueError(f"{field_name} inválido: '{value}'. Debe ser 9 o 11 dígitos.")


def validate_phone(value: Optional[str], *, field_name: str = "Telefono") -> None:
    if value is None or value == "":
        return
    if not _RE_PHONE.match(str(value)):
        raise ValueError(f"{field_name} inválido: '{value}'. Formato esperado ddd-ddd-dddd.")


def validate_email(value: Optional[str], *, field_name: str = "Correo") -> None:
    if value is None or value == "":
        return
    s = str(value)
    if len(s) > 80:
        raise ValueError(f"{field_name} demasiado largo (>{80} caracteres)")
    if not _RE_EMAIL.match(s):
        raise ValueError(f"{field_name} inválido: '{value}'.")
