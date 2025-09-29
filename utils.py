# utils.py
from __future__ import annotations
from datetime import datetime
from typing import Tuple

ISO_FMT = "%Y-%m-%d"

def validate_date(date_str: str) -> str:
    datetime.strptime(date_str, ISO_FMT)  # raises if invalid
    return date_str

def validate_amount(value: str | float) -> float:
    try:
        amt = float(value)
    except ValueError:
        raise ValueError("Amount must be a number.")
    if amt < 0:
        raise ValueError("Amount cannot be negative.")
    return amt

def parse_amount_and_date(amount: str | float, date_str: str) -> Tuple[float, str]:
    return (validate_amount(amount), validate_date(date_str))

def currency(n: float, symbol: str = "$") -> str:
    return f"{symbol}{n:,.2f}"
