from __future__ import annotations

from typing import Optional

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, now_datetime


class ExhaustedSequenceError(frappe.ValidationError):
    """Raised when attempting to consumir e-CF en un rango agotado."""


class ECFSequence(Document):
    E_PREFIX = "E"
    B_PREFIX = "B"

    def validate(self) -> None:  # noqa: D401 (frappe hook)
        self._normalize_fields()
        self._validate_range_values()
        self._validate_dates()
        self._validate_contingency_deadline()
        self._ensure_status_alignment()

    # ------------------------------------------------------------------
    # Helpers de normalización / validación
    # ------------------------------------------------------------------
    def _normalize_fields(self) -> None:
        # Si el siguiente número no está establecido, comenzar desde "range_from"
        if not self.next_number or int(self.next_number) < int(self.range_from):
            self.next_number = int(self.range_from)

        # Si el campo allow_reuse_rejected no aplica (Serie E), forzar 0
        if self.serie == self.E_PREFIX:
            self.allow_reuse_rejected = 0

    def _validate_range_values(self) -> None:
        rng_from = int(self.range_from)
        rng_to = int(self.range_to)
        nxt = int(self.next_number)

        if rng_from <= 0 or rng_to <= 0:
            frappe.throw(_("Los rangos de e-CF deben ser mayores a cero."))
        if rng_from > rng_to:
            frappe.throw(_("El valor 'Desde' no puede ser mayor que 'Hasta'."))
        if nxt < rng_from:
            frappe.throw(_("El Próximo Número debe ser mayor o igual al rango inicial."))
        if nxt > rng_to:
            # si está fuera de rango, marcar como exhausto y validar
            self.status = "Exhausto"
            frappe.throw(_("El Próximo Número ya superó el rango autorizado."))

    def _validate_dates(self) -> None:
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            frappe.throw(_("La fecha 'Vigente Desde' debe ser anterior a 'Vigente Hasta'."))

        if self.resolution_date and self.valid_from and self.resolution_date > self.valid_from:
            frappe.throw(_("La fecha de resolución debe ser anterior o igual a la fecha de vigencia."))

    def _validate_contingency_deadline(self) -> None:
        if self.is_contingency:
            if not self.replacement_deadline:
                frappe.throw(
                    _("Las secuencias de contingencia (Serie B) requieren una fecha límite de reemplazo."),
                )
        else:
            self.replacement_deadline = None

    def _ensure_status_alignment(self) -> None:
        """Actualiza el estado según el rango, fechas y serie."""
        now = now_datetime().date()

        if self.valid_until and self.valid_until < now:
            self.status = "Expirado"
            return

        if int(self.next_number) > int(self.range_to):
            self.status = "Exhausto"
            return

        if self.status not in {"Activo", "Suspendido", "Exhausto", "Expirado"}:
            self.status = "Activo"

    # ------------------------------------------------------------------
    # API para obtención y consumo de secuencias e-CF
    # ------------------------------------------------------------------
    def peek_next_encf(self) -> str:
        """Retorna el próximo e-NCF sin avanzar la secuencia."""
        numero = int(self.next_number)
        if numero > int(self.range_to):
            raise ExhaustedSequenceError(_("La secuencia está agotada."))
        serie = self._serie_prefix()
        tipo = self._tipo_codigo()
        return f"{serie}{tipo}{numero:010d}"

    def allocate_next_encf(self, commit: bool = True) -> str:
        """Asigna y avanza la secuencia, devolviendo el e-NCF generado."""
        encf = self.peek_next_encf()

        numero = int(self.next_number)
        self.last_allocated_on = now_datetime()
        self.next_number = numero + 1

        if int(self.next_number) > int(self.range_to):
            self.status = "Exhausto"

        if commit:
            self.save(ignore_permissions=True)

        return encf

    def reset_to(self, value: int) -> None:
        """Permite reajustar manualmente la secuencia (administradores)."""
        if value < int(self.range_from) or value > int(self.range_to):
            frappe.throw(_("El valor indicado está fuera del rango autorizado."))
        self.next_number = value
        self.status = "Activo"
        self.last_allocated_on = None

    # ------------------------------------------------------------------
    # utilidades privadas
    # ------------------------------------------------------------------
    def _serie_prefix(self) -> str:
        serie = (self.serie or "").strip().upper()
        return serie if serie in {self.E_PREFIX, self.B_PREFIX} else self.E_PREFIX

    def _tipo_codigo(self) -> str:
        raw = str(self.sequence_type or "").strip()
        return raw.split(" ")[0] if raw else "31"

    @property
    def is_expired(self) -> bool:
        if not self.valid_until:
            return False
        return self.valid_until < now_datetime().date()

    def schedule_contingency_deadline(self) -> Optional[str]:
        """Calcula fecha de reemplazo sugerida (15 días + plazo de reemplazo)."""
        if not self.is_contingency:
            return None
        base_date = self.last_allocated_on.date() if self.last_allocated_on else now_datetime().date()
        return add_days(base_date, 30)
