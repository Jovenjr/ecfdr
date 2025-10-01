from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional


def _to_decimal(value: Optional[str | float | int]) -> Decimal:
    if value is None:
        raise InvalidOperation("None is not a number")
    return Decimal(str(value))


def quantize(value: str | float | int, places: int) -> Decimal:
    q = Decimal("1").scaleb(-places)  # 2 -> Decimal('0.01')
    return _to_decimal(value).quantize(q, rounding=ROUND_HALF_UP)


def round_money_2(value: str | float | int) -> Decimal:
    return quantize(value, 2)


def round_unit_price_4(value: str | float | int) -> Decimal:
    return quantize(value, 4)


def round_subquantity_3(value: str | float | int) -> Decimal:
    return quantize(value, 3)


def to_str(d: Decimal) -> str:
    # normalize to plain string without scientific notation
    return format(d, 'f')


def format_decimal(value: str | float | int, places: int) -> str:
    """Return *value* formatted with the requested number of decimal places."""
    return to_str(quantize(value, places))


def format_money(value: str | float | int, places: int = 2) -> str:
    return format_decimal(value, places)


def format_exchange_rate(value: str | float | int, places: int = 4) -> str:
    return format_decimal(value, places)


