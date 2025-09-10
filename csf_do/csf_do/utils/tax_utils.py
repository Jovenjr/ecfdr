from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple

from .amount_utils import round_money_2, to_str


ALLOWED_ADDITIONAL_TAX_CODES = {
    "001",  # Propina Legal
    "002",  # CDT
    "003",  # ISC Servicios Seguros (ejemplo)
    "004",  # ISC Servicios Telecomunicaciones
    "005",  # ISC Expedición primera placa
    # Códigos de ISC específicos de alcoholes/cigarrillos en distintas tablas pueden variar por XSD
}


def compute_item_additional_taxes(monto_item: str | float | int, tabla_impuesto: List[Dict]) -> List[Tuple[str, Decimal, Decimal | None]]:
    """Calcula impuestos adicionales por ítem.

    Retorna lista de tuplas: (codigo, monto_calculado, tasa_aplicada_opcional)
    Regla simplificada: si viene 'TasaImpuestoAdicional' usar porcentaje sobre MontoItem; si viene 'MontoImpuestoSelectivoConsumoEspecifico' usar monto fijo; si viene 'MontoImpuestoSelectivoConsumoAdvalorem' úsese como monto.
    """
    results: List[Tuple[str, Decimal, Decimal | None]] = []
    try:
        base = Decimal(str(monto_item))
    except InvalidOperation:
        base = Decimal("0")
    for imp in tabla_impuesto or []:
        codigo = str(imp.get("TipoImpuesto") or "").zfill(3)
        if not codigo:
            continue
        tasa = imp.get("TasaImpuestoAdicional")
        monto_esp = imp.get("MontoImpuestoSelectivoConsumoEspecifico")
        monto_adv = imp.get("MontoImpuestoSelectivoConsumoAdvalorem")
        monto_calc = Decimal("0")
        tasa_dec: Decimal | None = None
        if tasa is not None and str(tasa) != "":
            tasa_dec = Decimal(str(tasa))
            monto_calc = (base * tasa_dec / Decimal("100"))
        elif monto_adv is not None and str(monto_adv) != "":
            monto_calc = Decimal(str(monto_adv))
        elif monto_esp is not None and str(monto_esp) != "":
            monto_calc = Decimal(str(monto_esp))
        results.append((codigo, round_money_2(monto_calc), tasa_dec))
    return results


def aggregate_additional_taxes(items_taxes: List[List[Tuple[str, Decimal, Decimal | None]]]) -> Dict[str, Dict[str, str]]:
    """Agrega impuestos adicionales de todos los ítems en un dict por código.

    Retorna: { codigo: { 'monto': 'X.XX', 'tasa': 'Y.YY' (si aplica) } }
    """
    acc: Dict[str, Tuple[Decimal, Decimal | None]] = {}
    for item_list in items_taxes:
        for codigo, monto, tasa in item_list:
            total, last_tasa = acc.get(codigo, (Decimal("0"), None))
            acc[codigo] = (total + monto, tasa or last_tasa)
    out: Dict[str, Dict[str, str]] = {}
    for codigo, (monto, tasa) in acc.items():
        out[codigo] = {"monto": to_str(round_money_2(monto))}
        if tasa is not None:
            out[codigo]["tasa"] = to_str(tasa)
    return out


