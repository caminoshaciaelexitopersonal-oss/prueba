import sqlite3
from typing import List, Optional
from models.employee import Employee
import uuid
from datetime import date

DB_FILE = "company_data.db"

def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the employees table if it doesn't exist."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                salary REAL NOT NULL,
                start_date TEXT NOT NULL,
                is_active BOOLEAN NOT NULL
            );
        """)
        conn.commit()

def add_employee(employee: Employee) -> None:
    """Adds an employee to the database."""
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO employees (id, name, position, salary, start_date, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            (str(employee.id), employee.name, employee.position, employee.salary, employee.start_date.isoformat(), employee.is_active),
        )
        conn.commit()

def get_employee(employee_id: str) -> Optional[Employee]:
    """Gets an employee by their ID."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Employee(
            id=uuid.UUID(row["id"]),
            name=row["name"],
            position=row["position"],
            salary=row["salary"],
            start_date=date.fromisoformat(row["start_date"]),
            is_active=bool(row["is_active"]),
        )

def list_employees() -> List[Employee]:
    """Lists all employees."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM employees ORDER BY name;")
        rows = cursor.fetchall()
        return [
            Employee(
                id=uuid.UUID(row["id"]),
                name=row["name"],
                position=row["position"],
                salary=row["salary"],
                start_date=date.fromisoformat(row["start_date"]),
                is_active=bool(row["is_active"]),
            )
            for row in rows
        ]

def reset_employees() -> None:
    """Clears all employees from the database."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM employees;")
        conn.commit()

# Initialize the database when this module is first imported
init_db()
