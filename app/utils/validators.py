from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

from app.constants import DATE_FORMAT


class ValidationError(ValueError):
    """Validation error with user-friendly message."""


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_text(value: str | None, field_name: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValidationError(f"Поле «{field_name}» обязательно для заполнения.")
    return cleaned


def optional_text(value: str | None) -> str | None:
    cleaned = (value or "").strip()
    return cleaned or None


def parse_decimal(value: str | None, field_name: str) -> Decimal:
    try:
        cleaned = require_text(value, field_name).replace(",", ".")
        return Decimal(cleaned)
    except (ValidationError, InvalidOperation) as error:
        if isinstance(error, ValidationError):
            raise
        raise ValidationError(f"Поле «{field_name}» должно быть числом.")


def parse_positive_decimal(value: str | None, field_name: str) -> Decimal:
    number = parse_decimal(value, field_name)
    if number <= 0:
        raise ValidationError(f"Поле «{field_name}» должно быть больше нуля.")
    return number


def parse_positive_int(value: str | None, field_name: str) -> int:
    text = require_text(value, field_name)
    if not text.isdigit():
        raise ValidationError(f"Поле «{field_name}» должно быть целым числом.")
    number = int(text)
    if number <= 0:
        raise ValidationError(f"Поле «{field_name}» должно быть больше нуля.")
    return number


def parse_date(value: str | None, field_name: str, required: bool = False):
    cleaned = (value or "").strip()
    if not cleaned:
        if required:
            raise ValidationError(f"Поле «{field_name}» обязательно для заполнения.")
        return None
    try:
        return datetime.strptime(cleaned, DATE_FORMAT).date()
    except ValueError as error:
        raise ValidationError(
            f"Поле «{field_name}» должно быть в формате {DATE_FORMAT}."
        ) from error


def validate_email(value: str | None, field_name: str) -> str | None:
    cleaned = optional_text(value)
    if cleaned and not EMAIL_RE.match(cleaned):
        raise ValidationError(f"Поле «{field_name}» содержит некорректный email.")
    return cleaned


def validate_date_range(start_date, end_date, start_label: str, end_label: str) -> None:
    if start_date and end_date and end_date < start_date:
        raise ValidationError(f"Поле «{end_label}» не может быть раньше поля «{start_label}».")
