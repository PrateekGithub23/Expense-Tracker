import sqlite3

# Connection to the database
def connect():
    try:
        # Create connection to the database
        conn = sqlite3.connect('expenses.db')  # This will create the database if it doesn't exist
        # create a cursor to run queries
        cursor = conn.cursor()

        # Create the expenses table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount REAL,
            category TEXT,
            note TEXT,
            date TEXT
    )
        ''')

        # Commit changes and return the connection
        conn.commit()
        return conn  # Return connection object to be used in other functions
    except sqlite3.Error as e:
        print(f"Error while connecting to database: {e}")
        return None  # Return None if there's an error
    
# Close the database connection
def close_connection(connection):
    if connection:
        connection.close()  # Properly close the connection