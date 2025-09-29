from __future__ import annotations

from typing import Iterable, Tuple

import frappe
from frappe import _
from frappe.model.document import Document

from csf_do.csf_do.utils.field_validators import validate_rnc


class DGIIConfiguration(Document):
    def validate(self) -> None:  # noqa: D401 - frappe hook
        self._validate_rnc()
        self._validate_certificate()
        self._validate_urls()
        self._validate_numbers()

    # --- Helpers -----------------------------------------------------------------
    def _validate_rnc(self) -> None:
        if not getattr(self, "rnc_emisor", None):
            frappe.throw(_("Debe definir el RNC del emisor en 'RNC Emisor'."))
        validate_rnc(self.rnc_emisor, field_name=_("RNC Emisor"))

    def _validate_certificate(self) -> None:
        if not getattr(self, "p12_file", None):
            frappe.throw(_("Debe adjuntar el certificado digital PKCS#12."))
        if not getattr(self, "p12_password", None):
            frappe.throw(_("Debe indicar la contraseña del certificado digital."))

    def _validate_urls(self) -> None:
        https_fields: Iterable[Tuple[str, str]] = (
            ("precert_base_url", _("Pre-Certificación Base URL")),
            ("cert_base_url", _("Certificación Base URL")),
            ("prod_base_url", _("Producción Base URL")),
            ("auth_semilla_url", _("URL Semilla (override)")),
            ("auth_token_url", _("URL Token (override)")),
            ("recepcion_ecf_url", _("URL Recepción e-CF (override)")),
            ("consulta_estado_url", _("URL Consulta Estado (override)")),
            ("directorio_servicios_url", _("URL Directorio Servicios (override)")),
            ("recepcion_endpoint", _("URL Recepción e-CF")),
            ("aprobacion_endpoint", _("URL Aprobación Comercial")),
            ("autenticacion_endpoint", _("URL Autenticación (opcional)")),
        )
        for fieldname, label in https_fields:
            value = getattr(self, fieldname, None)
            if not value:
                continue
            url = str(value).strip()
            if not url.lower().startswith("https://"):
                frappe.throw(_("{0} debe comenzar con https://").format(label))

    def _validate_numbers(self) -> None:
        def _must_be_positive(val: int, label: str) -> None:
            if val is None:
                return
            if val <= 0:
                frappe.throw(_("{0} debe ser mayor que 0.").format(label))

        _must_be_positive(int(getattr(self, "timeout_seconds", 30) or 0), _("Timeout (segundos)"))
        _must_be_positive(int(getattr(self, "retry_backoff_seconds", 5) or 0), _("Backoff reintentos (seg)"))
        max_retries = int(getattr(self, "max_retries", 3) or 0)
        if max_retries < 0:
            frappe.throw(_("Máx. Reintentos no puede ser negativo."))


