# expense_tracker.py
from __future__ import annotations
import typer
from rich.console import Console
from rich.table import Table
from datetime import date  # NEW: for defaulting date prompts to today

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
    date_str: str = typer.Argument(..., help="YYYY-MM-DD"),
    note: str = typer.Option("", "--note", "-n", help="Optional note"),
):
    """Add a new expense (CLI args)."""
    amt, dt = parse_amount_and_date(amount, date_str)
    expense_id = db.add_expense(name, amt, category, note, dt)
    console.print(f":sparkles: Added expense [b]{expense_id}[/b].")

# ----------------------- NEW: Prompt-based Add -----------------------
@app.command()
def addp(
    name: str = typer.Option(..., prompt="Name"),
    amount: float = typer.Option(..., prompt="Amount"),
    category: str = typer.Option(..., prompt="Category"),
    date_str: str = typer.Option(
        date.today().isoformat(), "--date", "-d", prompt="Date (YYYY-MM-DD)", show_default=True
    ),
    note: str = typer.Option("", "--note", "-n", prompt="Note (optional)", prompt_required=False),
):
    """Add a new expense via interactive prompts."""
    amt, dt = parse_amount_and_date(amount, date_str)
    expense_id = db.add_expense(name, amt, category, note, dt)
    console.print(f":sparkles: Added expense [b]{expense_id}[/b].")
# --------------------------------------------------------------------

@app.command("list")
def list_(limit: int = typer.Option(0, "--limit", "-l", help="Limit rows (0 = all)")):
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
    date_str: str = typer.Option(None, "--date", help="YYYY-MM-DD"),
):
    """Delete expenses by id OR name OR date."""
    deleted = db.delete_expenses_by(expense_id=expense_id, name=name, date=date_str)
    console.print(f":wastebasket: Deleted {deleted} row(s).")

@app.command()
def update(
    expense_id: int,
    name: str,
    amount: float,
    category: str,
    date_str: str,
    note: str = typer.Option("", "--note", "-n"),
):
    """Update an existing expense completely."""
    amt, dt = parse_amount_and_date(amount, date_str)
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

# ----------------------- NEW: Interactive Menu -----------------------
def _prompt_expense_fields():
    """Prompt for fields and return validated values."""
    name = typer.prompt("Name")
    amount = typer.prompt("Amount", type=float)
    category = typer.prompt("Category")
    dt_default = date.today().isoformat()
    date_str = typer.prompt("Date (YYYY-MM-DD)", default=dt_default)
    note = typer.prompt("Note (optional)", default="")
    amt, dt = parse_amount_and_date(amount, date_str)
    return name, amt, category, note, dt

@app.command()
def menu():
    """Interactive menu loop (no CLI args needed)."""
    while True:
        console.rule("[bold]Expense Tracker Menu")
        console.print(
            "[b]1[/b] Add expense\n"
            "[b]2[/b] List expenses\n"
            "[b]3[/b] Search by name\n"
            "[b]4[/b] By category\n"
            "[b]5[/b] Between dates\n"
            "[b]6[/b] Report\n"
            "[b]7[/b] Delete by ID\n"
            "[b]0[/b] Quit"
        )
        choice = typer.prompt("Choose an option", type=int)

        if choice == 1:
            name, amt, cat, note, dt = _prompt_expense_fields()
            eid = db.add_expense(name, amt, cat, note, dt)
            console.print(f":sparkles: Added expense [b]{eid}[/b].")

        elif choice == 2:
            rows = db.get_all_expenses()
            _print_rows(rows) if rows else console.print("No expenses yet.")

        elif choice == 3:
            kw = typer.prompt("Keyword")
            rows = db.search_expenses(kw)
            _print_rows(rows) if rows else console.print("No matches.")

        elif choice == 4:
            cat = typer.prompt("Category")
            rows = db.get_expenses_by_category(cat)
            _print_rows(rows) if rows else console.print("No expenses for this category.")

        elif choice == 5:
            start = typer.prompt("Start date (YYYY-MM-DD)")
            end = typer.prompt("End date (YYYY-MM-DD)")
            rows = db.get_expenses_between_dates(start, end)
            _print_rows(rows) if rows else console.print("No expenses in that range.")

        elif choice == 6:
            rows = db.get_all_expenses()
            if not rows:
                console.print("No data yet.")
                continue
            total_v = total_spent(rows)
            avg_day_v = average_daily(rows)
            cat_v = by_category(rows)
            mon_v = monthly_summary(rows)
            top5_v = top_expenses(rows, 5)

            console.rule("[bold]Summary")
            console.print(f"Total spent: [bold]{currency(total_v)}[/bold]")
            console.print(f"Average per day (observed window): [bold]{currency(avg_day_v)}[/bold]")

            console.rule("[bold]By Category")
            t1 = Table(show_header=True, header_style="bold")
            t1.add_column("Category"); t1.add_column("Total", justify="right")
            for k, v in cat_v.items():
                t1.add_row(k, f"{v:,.2f}")
            console.print(t1)

            console.rule("[bold]By Month")
            t2 = Table(show_header=True, header_style="bold")
            t2.add_column("Month"); t2.add_column("Total", justify="right")
            for k, v in mon_v.items():
                t2.add_row(k, f"{v:,.2f}")
            console.print(t2)

            console.rule("[bold]Top 5 Expenses")
            _print_rows(top5_v)

        elif choice == 7:
            eid = typer.prompt("Expense ID", type=int)
            deleted = db.delete_expenses_by(expense_id=eid)
            console.print(f":wastebasket: Deleted {deleted} row(s).")

        elif choice == 0:
            console.print("Goodbye! 👋")
            break

        else:
            console.print("Invalid choice. Try again.")
# --------------------------------------------------------------------

if __name__ == "__main__":
    app()
