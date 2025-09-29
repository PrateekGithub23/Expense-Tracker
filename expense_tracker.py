# expense_tracker.py
from __future__ import annotations
import typer
from rich.console import Console
from rich.table import Table

import database as db
from utils import parse_amount_and_date, currency
from analytics import by_category, monthly_summary, total_spent, top_expenses, average_daily

app = typer.Typer(help="Incomp - Expense Tracker")
console = Console()

def _print_rows(rows):
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", justify="right")
    table.add_column("Date")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Amount", justify="right")
    table.add_column("Note", overflow="fold")
    for r in rows:
        table.add_row(
            str(r["expense_id"]),
            r["date"],
            r["name"],
            r["category"],
            f'{r["amount"]:,.2f}',
            r.get("note") or "",
        )
    console.print(table)

@app.command()
def init():
    """Initialize the database (idempotent)."""
    db.init_db()
    console.print(":white_check_mark: Database ready.")

@app.command()
def add(
    name: str = typer.Argument(..., help="Expense name"),
    amount: float = typer.Argument(..., help="Amount"),
    category: str = typer.Argument(..., help="Category"),
    date: str = typer.Argument(..., help="YYYY-MM-DD"),
    note: str = typer.Option("", "--note", "-n", help="Optional note"),
):
    """Add a new expense."""
    amt, dt = parse_amount_and_date(amount, date)
    expense_id = db.add_expense(name, amt, category, note, dt)
    console.print(f":sparkles: Added expense [b]{expense_id}[/b].")

@app.command("list")
def list_(
    limit: int = typer.Option(0, "--limit", "-l", help="Limit rows (0 = all)")
):
    """List expenses (most recent first)."""
    rows = db.get_all_expenses()
    if limit > 0:
        rows = rows[:limit]
    if not rows:
        console.print("No expenses yet.")
        return
    _print_rows(rows)

@app.command()
def delete(
    expense_id: int = typer.Option(None, "--id"),
    name: str = typer.Option(None, "--name"),
    date: str = typer.Option(None, "--date", help="YYYY-MM-DD"),
):
    """Delete expenses by id OR name OR date."""
    deleted = db.delete_expenses_by(expense_id=expense_id, name=name, date=date)
    console.print(f":wastebasket: Deleted {deleted} row(s).")

@app.command()
def update(
    expense_id: int,
    name: str,
    amount: float,
    category: str,
    date: str,
    note: str = typer.Option("", "--note", "-n"),
):
    """Update an existing expense completely."""
    amt, dt = parse_amount_and_date(amount, date)
    count = db.update_expense(expense_id, name, amt, category, note, dt)
    console.print(f":pencil: Updated {count} row(s).")

@app.command()
def search(keyword: str):
    """Search by name substring."""
    rows = db.search_expenses(keyword)
    if not rows:
        console.print("No matches.")
        return
    _print_rows(rows)

@app.command()
def bycat(category: str):
    """List expenses in a category."""
    rows = db.get_expenses_by_category(category)
    if not rows:
        console.print("No expenses for this category.")
        return
    _print_rows(rows)

@app.command()
def between(start: str, end: str):
    """List expenses between YYYY-MM-DD dates (inclusive)."""
    rows = db.get_expenses_between_dates(start, end)
    if not rows:
        console.print("No expenses in that range.")
        return
    _print_rows(rows)
@app.command()
def report():
    """Quick analytics summary."""
    rows = db.get_all_expenses()
    total = total_spent(rows)
    avg_day = average_daily(rows)
    cat = by_category(rows)
    mon = monthly_summary(rows)
    top5 = top_expenses(rows, 5)

    console.rule("[bold]Summary")
    console.print(f"Total spent: [bold]{currency(total)}[/bold]")
    console.print(f"Average per day (observed window): [bold]{currency(avg_day)}[/bold]")

    console.rule("[bold]By Category")
    t1 = Table(show_header=True, header_style="bold")
    t1.add_column("Category")
    t1.add_column("Total", justify="right")
    for k, v in cat.items():
        t1.add_row(k, f"{v:,.2f}")
    console.print(t1)

    console.rule("[bold]By Month")
    t2 = Table(show_header=True, header_style="bold")
    t2.add_column("Month")
    t2.add_column("Total", justify="right")
    for k, v in mon.items():
        t2.add_row(k, f"{v:,.2f}")
    console.print(t2)

    console.rule("[bold]Top 5 Expenses")
    _print_rows(top5)

if __name__ == "__main__":
    app()