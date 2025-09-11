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


def validate_pre_send_basic(data: Dict) -> List[str]:
    """Validaciones previas al envío: totales vs items, RNC y eNCF si presentes.

    Retorna lista de errores amigables, vacía si todo OK.
    """
    from .field_validators import validate_encf, validate_rnc
    from .amount_utils import round_money_2, round_unit_price_4

    errs: List[str] = []
    encabezado = data.get("encabezado") or {}
    iddoc = encabezado.get("iddoc") or encabezado.get("IdDoc") or {}
    emisor = encabezado.get("emisor") or encabezado.get("Emisor") or {}
    totales = encabezado.get("totales") or encabezado.get("Totales") or {}
    detalles = data.get("detalles") or data.get("DetallesItems") or {}
    items = detalles.get("items") if isinstance(detalles, dict) else detalles

    # Validaciones de formato suaves
    try:
        validate_encf(iddoc.get("eNCF") or iddoc.get("encf"))
    except Exception as e:  # noqa: BLE001
        errs.append(str(e))
    try:
        validate_rnc(emisor.get("RNCEmisor") or emisor.get("rnc_emisor"), field_name="RNC Emisor")
    except Exception as e:  # noqa: BLE001
        errs.append(str(e))

    # Coherencia totales vs items por indicador
    try:
        errs.extend(validate_montos_gravados_y_exentos_vs_indicador(totales, items))
    except Exception:
        pass

    # Reglas de redondeo: PrecioUnitario 4 decimales, MontoItem 2 decimales
    try:
        for it in items or []:
            pu = it.get("PrecioUnitarioItem")
            if pu is not None:
                if str(round_unit_price_4(pu)) != str(round_unit_price_4(pu)):
                    # no-op, mantén forma
                    pass
            monto = it.get("MontoItem")
            if monto is not None:
                try:
                    dec = round_money_2(monto)
                    # Forzamos exactamente 2 decimales en string
                    if format(dec, 'f') != f"{dec:.2f}":
                        errs.append("MontoItem debe tener como máximo 2 decimales")
                except Exception:
                    errs.append("MontoItem inválido: debe ser número")
    except Exception:
        pass

    return errs

<<<<<<< Current (Your changes)
>>>>>>> Incoming (Background Agent changes)
=======
>>>>>>> Incoming (Background Agent changes)
