from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple


TOLERANCE = Decimal("0.01")


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return Decimal("0")


def validate_montos_gravados_y_exentos_vs_indicador(
    totales_in: Dict, items: List[Dict]
) -> List[str]:
    """Valida coherencia entre IndicadorFacturacion de ítems y montos en Totales.

    Reglas (cuando los campos existen en Totales):
    - MontoGravadoI1 debe ≈ suma(MontoItem de items con IndicadorFacturacion == '1').
    - MontoGravadoI2 debe ≈ suma(MontoItem de items con IndicadorFacturacion == '2').
    - MontoGravadoI3 debe ≈ suma(MontoItem de items con IndicadorFacturacion == '3').
    - MontoExento debe ≈ suma(MontoItem de items con IndicadorFacturacion == '0').

    No valida TotalITBISx al no conocer la tasa exacta por indicador aquí.
    """
    errors: List[str] = []
    sum_by_ind: Dict[str, Decimal] = {"0": Decimal("0"), "1": Decimal("0"), "2": Decimal("0"), "3": Decimal("0")}
    for it in items or []:
        ind = str(it.get("IndicadorFacturacion") or "").strip()
        monto = _to_decimal(it.get("MontoItem"))
        if ind in sum_by_ind:
            sum_by_ind[ind] += monto

    def _check(field_name: str, expected_sum: Decimal):
        val = totales_in.get(field_name)
        if val is None or str(val) == "":
            return
        decl = _to_decimal(val)
        if (decl - expected_sum).copy_abs() > TOLERANCE:
            errors.append(
                f"Inconsistencia {field_name}: total declarado={decl} vs suma items={expected_sum} (tol±{TOLERANCE})"
            )

    _check("MontoGravadoI1", sum_by_ind["1"])
    _check("MontoGravadoI2", sum_by_ind["2"])
    _check("MontoGravadoI3", sum_by_ind["3"])
    _check("MontoExento", sum_by_ind["0"])

    return errors


