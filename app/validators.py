from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Iterable

CSV_DELIMITER = ";"
EXPECTED_HEADERS = ("Дата", "Номер группы", "ФИО", "Оценка")


@dataclass(frozen=True, slots=True)
class ParsedRow:
    grade_date: date
    group_no: str
    full_name: str
    grade: int


def _strip(s: Any) -> str:
    return ("" if s is None else str(s)).strip()


def parse_date(value: Any) -> date:
    v = _strip(value)
    try:
        return datetime.strptime(v, "%d.%m.%Y").date()
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date: {v}")


def parse_group(value: Any) -> str:
    v = _strip(value)
    if not v:
        raise ValueError("Group is empty")
    if len(v) > 32:
        raise ValueError("Group is too long")
    return v


def parse_name(value: Any) -> str:
    v = _strip(value)
    if not v:
        raise ValueError("Full name is empty")
    if len(v) < 3:
        raise ValueError("Full name is too short")
    if len(v) > 256:
        raise ValueError("Full name is too long")
    return v


def parse_grade(value: Any) -> int:
    v = _strip(value)
    if not v:
        raise ValueError("Grade is empty")
    try:
        g = int(v)
    except ValueError:
        raise ValueError(f"Grade is not an integer: {v}")
    if not (2 <= g <= 5):
        raise ValueError(f"Grade out of range [2..5]: {g}")
    return g


def validate_headers(headers: Iterable[str]) -> None:
    got = tuple(h.strip() for h in headers)
    if got != EXPECTED_HEADERS:
        raise ValueError(f"Invalid CSV headers: expected {EXPECTED_HEADERS}, got {got}")
