# analytics.py
from __future__ import annotations
from collections import defaultdict
from typing import Dict, List
from datetime import datetime


# Helper Fuctions for Analytics


def total_spent(rows: List[dict]) -> float:
    return sum(r["amount"] for r in rows)

def by_category(rows: List[dict]) -> Dict[str, float]:
    agg = defaultdict(float)
    for r in rows:
        agg[r["category"]] += r["amount"]
    return dict(sorted(agg.items(), key=lambda kv: kv[1], reverse=True))

def monthly_summary(rows: List[dict]) -> Dict[str, float]:
    agg = defaultdict(float)  # YYYY-MM -> total
    for r in rows:
        ym = r["date"][:7]
        agg[ym] += r["amount"]
    return dict(sorted(agg.items()))

def top_expenses(rows: List[dict], n: int = 5) -> List[dict]:
    return sorted(rows, key=lambda r: (r["amount"], r["date"]), reverse=True)[:n]

def average_daily(rows: List[dict]) -> float:
    if not rows:
        return 0.0
    dates = sorted(set(r["date"] for r in rows))
    first = datetime.fromisoformat(dates[0])
    last = datetime.fromisoformat(dates[-1])
    days = (last - first).days + 1
    total = total_spent(rows)
    return total / max(days, 1)
