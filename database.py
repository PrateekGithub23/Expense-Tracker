# database.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("expenses.db")

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db() -> None:
    conn = _connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                amount     REAL NOT NULL CHECK (amount >= 0),
                category   TEXT NOT NULL,
                note       TEXT,
                date       TEXT NOT NULL  -- ISO (YYYY-MM-DD)
            );

            CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
            CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
            CREATE INDEX IF NOT EXISTS idx_expenses_name ON expenses(name);
            """
        )
        conn.commit()
    finally:
        conn.close()

def add_expense(name: str, amount: float, category: str, note: str, date: str) -> int:
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO expenses (name, amount, category, note, date) VALUES (?, ?, ?, ?, ?)",
            (name, amount, category, note, date),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def update_expense(expense_id: int, name: str, amount: float,
                   category: str, note: str, date: str) -> int:
    conn = _connect()
    try:
        cur = conn.execute(
            """
            UPDATE expenses
               SET name = ?, amount = ?, category = ?, note = ?, date = ?
             WHERE expense_id = ?
            """,
            (name, amount, category, note, date, expense_id),
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def delete_expenses_by(
    *, expense_id: Optional[int] = None, name: Optional[str] = None, date: Optional[str] = None
) -> int:
    conn = _connect()
    try:
        if expense_id is not None:
            cur = conn.execute("DELETE FROM expenses WHERE expense_id = ?", (expense_id,))
        elif name is not None:
            cur = conn.execute("DELETE FROM expenses WHERE name = ?", (name,))
        elif date is not None:
            cur = conn.execute("DELETE FROM expenses WHERE date = ?", (date,))
        else:
            raise ValueError("Provide expense_id OR name OR date")
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def get_all_expenses() -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM expenses ORDER BY date DESC, expense_id DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_expense_by_id(expense_id: int) -> Optional[Dict[str, Any]]:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM expenses WHERE expense_id = ?", (expense_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_expenses_by_date(date: str) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM expenses WHERE date = ? ORDER BY expense_id DESC", (date,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_expenses_by_category(category: str) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM expenses WHERE category = ? ORDER BY date DESC", (category,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_expenses_between_dates(start: str, end: str) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date ASC",
            (start, end),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def search_expenses(keyword: str) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE name LIKE ? ORDER BY date DESC",
            (f"%{keyword}%",),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_expenses_by_amount_range(min_amt: float, max_amt: float) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE amount BETWEEN ? AND ? ORDER BY amount ASC",
            (min_amt, max_amt),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_latest_expenses(n: int = 10) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM expenses ORDER BY date DESC, expense_id DESC LIMIT ?",
            (n,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_distinct_categories() -> List[str]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT DISTINCT category FROM expenses ORDER BY category ASC").fetchall()
        return [r["category"] for r in rows]
    finally:
        conn.close()

def get_total_count() -> int:
    conn = _connect()
    try:
        return conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    finally:
        conn.close()
