import sqlite3
import os

DB_PATH = 'employee_data.db'

def setup_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Departments table
    cursor.execute('''
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Create Employees table
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department_id INTEGER,
            salary REAL,
            hire_date DATE,
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
    ''')

    # Insert sample data
    departments = [
        ('Engineering',),
        ('Sales',),
        ('Marketing',),
        ('HR',)
    ]
    cursor.executemany('INSERT INTO departments (name) VALUES (?)', departments)

    employees = [
        ('Alice Smith', 1, 120000, '2020-01-15'),
        ('Bob Jones', 1, 115000, '2021-03-22'),
        ('Charlie Brown', 2, 85000, '2019-11-01'),
        ('Diana Prince', 3, 95000, '2022-07-10'),
        ('Eve Davis', 4, 75000, '2023-02-28'),
        ('Frank Wright', 1, 130000, '2018-05-14')
    ]
    cursor.executemany('INSERT INTO employees (name, department_id, salary, hire_date) VALUES (?, ?, ?, ?)', employees)

    conn.commit()
    conn.close()
    print(f"Database setup complete at {DB_PATH}")

if __name__ == '__main__':
    setup_database()
