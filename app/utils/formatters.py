from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.constants import CONTRACT_STATUS_LABELS, DATE_FORMAT, ORDER_STATUS_LABELS, ROLE_LABELS


def format_date(value: date | datetime | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime(DATE_FORMAT)


def format_decimal(value: Decimal | float | int | None) -> str:
    if value is None:
        return ""
    decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    return f"{decimal_value:.2f}"


def format_bool(value: bool) -> str:
    return "Да" if value else "Нет"


def contract_status_label(code: str) -> str:
    return CONTRACT_STATUS_LABELS.get(code, code)


def order_status_label(code: str) -> str:
    return ORDER_STATUS_LABELS.get(code, code)


def role_label(role: str) -> str:
    return ROLE_LABELS.get(role, role)
