from database import connect, close_connection

def add_expense(name, amount, category, note, date):
    # Connect to the database
    connection = connect()
    if connection:
        cursor = connection.cursor()

        # SQL insert command
        sql = '''
            INSERT INTO expenses (name, amount, category, note, date)
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(sql, (name, amount, category, note, date))

        # Commit changes and close the connection
        connection.commit()
        close_connection(connection)  # Close the connection when done
        print("Expense added successfully!")
    else:
        print("Failed to connect to the database.")


def update_existing_expense(expense_id, name, amount, category, note, date):
    connection = connect()
    if connection:
        cursor = connection.cursor()

        # SQL insert command
        sql = '''
            UPDATE expenses
            SET name = ?, amount = ?, category = ?, note = ?, date = ?
            WHERE expense_id = ?
        '''
        cursor.execute(sql, (name, amount, category, note, date, expense_id))


        # Commit changes and close the connection
        connection.commit()
        close_connection(connection)  # Close the connection when done
        print("Expense updated successfully!")
    else:
        print("Failed to connect to the database.")


# Delete expenses

def delete_expense():
    print("How do you want to delete your expense")
    print("1. Name")
    print("2. Expense ID")
    print("3. Date")

    userChoice = int(input('Enter your choice (1/2/3): '))

    # establish the connection

    connection = connect()
    
    if not connection:
        print("Failed to connect to the database.")
        return

    # cursor to run queries
    cursor = connection.cursor()

    if userChoice == 1:
        # ask the user for the name of the expense, strip any white spaces
        name = input("Enter the name of the expense: ").strip()
        cursor.execute('DELETE FROM expenses WHERE name = ?', (name,))

    elif userChoice == 2:
        expense_id = int(input("Enter the expense ID to delete: "))
        cursor.execute('DELETE FROM expenses WHERE expense_id = ?', (expense_id,))
        
    elif userChoice == 3:
        date = input("Enter the date (YYYY-MM-DD) to delete expenses from: ").strip()
        cursor.execute('DELETE FROM expenses WHERE date = ?', (date,))
    else:
        print("Invalid choice.")
        close_connection(connection)
        return
    
    # commit the changes
    connection.commit()
    print(f"{cursor.rowcount} expense(s) deleted.")
    close_connection(connection)



# Fetching Expenses

def get_all_expenses():

    # Connect to the database
    connection = connect()
    # if connection established
    if connection:

        # Call the cursor 
        cursor = connection.cursor()

        # SQL insert command
        sql = '''
            SELECT * from expenses
        '''

        # execute the sql query 
        cursor.execute(sql)

        # get the row using fetchall, returns a list of rows
        rows = cursor.fetchall()

        close_connection(connection)  # Close the connection when done

        # if rows exist 
        if rows:
            print("Expenses: ")
            for row in rows:
                print(row)
        else:
            print("No expense found!")
    else:
        print("Failed to connect to the database.")


def get_expense_by_id(expense_id):
    connection = connect()
    if connection:
        cursor = connection.cursor()

        sql = '''
            SELECT * FROM expenses WHERE expense_id = ?
        '''
        cursor.execute(sql, (expense_id,))

        row = cursor.fetchone()  # Fetch the result before closing
        close_connection(connection)  # Close the connection

        if row:
            print("Expense found:")
            print(row)
        else:
            print("No expense found with that ID.")
    else:
        print("Failed to connect to the database.")

def get_expenses_by_date(date):
    connection = connect()
    if connection:
        cursor = connection.cursor()

        sql = '''
            SELECT * FROM expenses WHERE date = ?
        '''
        cursor.execute(sql, (date,))

        row = cursor.fetchone()  # Fetch the result before closing
        close_connection(connection)  # Close the connection

        if row:
            print("Expense found:")
            print(row)
        else:
            print("No expense found for the date.")
    else:
        print("Failed to connect to the database.")


def get_expense_by_category(category):
    connection = connect()
    if connection:
        cursor = connection.cursor()

        sql = '''
            SELECT * FROM expenses WHERE category = ?
        '''
        cursor.execute(sql, (category,))
        row = cursor.fetchone()  # Fetch the result before closing
        close_connection(connection)  # Close the connection
        return row  # Return the result
    else:
        print("Failed to connect to the database.")


def get_expenses_between_dates(start, end):
    connection = connect()
    if connection:
        cursor = connection.cursor()
        sql = '''
            SELECT * FROM expenses WHERE date BETWEEN ? AND ?
        '''
        cursor.execute(sql, (start, end))
        rows = cursor.fetchall()
        close_connection(connection)
        return rows  # Return the result
    else:
        print("Failed to connect to the database.")
        return None
    
def search_expenses(keyword):
    connection = connect()
    if connection:
        cursor = connection.cursor()


        sql = '''
            SELECT * FROM expenses
            WHERE name LIKE ?
        '''
        cursor.execute(sql, ('%' + keyword + '%',))
        
        results = cursor.fetchall()
        connection.close()
        return results
    

    
