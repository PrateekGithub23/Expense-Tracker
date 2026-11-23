# Expense Tracker

A command-line expense tracker in Python. Expenses are stored in a local SQLite file (`expenses.db`, created on first run). Built with Typer for the commands and Rich for the tables.

```bash
pip install -r requirements.txt
python expense_tracker.py            # interactive menu
python expense_tracker.py --help     # or use the commands directly
```

Examples:

```bash
python expense_tracker.py add Coffee 4.50 Food 2025-09-28 --note "with team"
python expense_tracker.py list --limit 10
python expense_tracker.py between 2025-09-01 2025-09-30
python expense_tracker.py report                 # totals, daily average, by category, by month
python expense_tracker.py export expenses.csv
python expense_tracker.py importcsv expenses.csv
```

Other commands: `addp` (add with prompts), `search`, `bycat`, `update`, `delete`.

Code layout: `expense_tracker.py` (CLI and menu), `database.py` (SQLite access), `analytics.py` (summaries), `csv_io.py` (CSV import/export), `utils.py` (parsing and formatting).
