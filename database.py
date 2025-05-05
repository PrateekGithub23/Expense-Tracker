import sqlite3

# Connection to the database
def connect():
    conn = sqlite3.connect('expenses.db')  # This will create the database if it doesn't exist
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            note TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()
