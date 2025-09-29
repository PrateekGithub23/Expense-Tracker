# formatting currency and validating inputs
from __future__ import annotations
from datetime import datetime
from typing import Tuple

ISO_FMT = "%Y-%m-%d"

def validate_date(date_str: str) -> str:

    # convert to datetime object to validate format
    datetime.strptime(date_str, ISO_FMT) 
    return date_str

# accept the amount as string or float
def validate_amount(value: str | float) -> float:
    try:
        amt = float(value)
    except ValueError:
        raise ValueError("Amount must be a number.")
    if amt < 0:
        raise ValueError("Amount cannot be negative.")
    return amt

# utility to parse and validate amount and date
def parse_amount_and_date(amount: str | float, date_str: str) -> Tuple[float, str]:
    return (validate_amount(amount), validate_date(date_str))

# format number as currency string
def currency(n: float, symbol: str = "$") -> str:

    # format to 2 decimal places
    return f"{symbol}{n:,.2f}"
