from __future__ import annotations
import csv
from typing import Tuple, List, Dict
import database as db
from utils import validate_date, validate_amount

CSV_HEADERS = ["expense_id","name", "amount", "category", "note", "date"]

def export_to_csv(path: str) -> int:
    rows: List[Dict] = db.get_all_expenses()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "expense_id": r["expense_id"],
                "name": r["name"],
                "amount": r["amount"],
                "category": r["category"],
                "note": r["note"],
                "date": r["date"],
            })
    return len(rows)

def import_expenses_from_csv(path: str, mode: str = "append") -> Tuple[int, int]:

    # mode: "append" or "upsert"
    inserted = 0
    updated = 0

    # open the file, read the rows
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Required fields
            name = (row.get("name") or "").strip()
            category = (row.get("category") or "").strip()
            date = (row.get("date") or "").strip()
            if not (name and category and date and row.get("amount")):
                continue  # skip incomplete rows

            amount = validate_amount(row["amount"])
            validate_date(date)
            note = (row.get("note") or "").strip()

            if mode == "upsert" and (row.get("expense_id") or "").strip().isdigit():
                eid = int(row["expense_id"])
                existing = db.get_expense_by_id(eid)
                if existing:
                    db.update_expense(eid, name, amount, category, note, date)
                    updated += 1
                    continue

            db.add_expense(name, amount, category, note, date)
            inserted += 1

    return inserted, updated