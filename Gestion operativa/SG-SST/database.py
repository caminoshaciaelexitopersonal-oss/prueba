import sqlite3
from typing import List, Optional
from models.incident import Incident
import uuid
from datetime import date

# This DB_FILE must be the same as the one in the HR system
DB_FILE = "company_data.db"

def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the incidents table if it doesn't exist."""
    with get_db_connection() as conn:
        # Note: The employees table is managed by the HR system's database module.
        # This module only ensures the incidents table exists.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                incident_date TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            );
        """)
        conn.commit()

def add_incident(incident: Incident) -> None:
    """Adds an incident to the database."""
    with get_db_connection() as conn:
        conn.execute(
            """INSERT INTO incidents (id, employee_id, incident_date, location, description, severity)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (str(incident.id), incident.employee_id, incident.incident_date.isoformat(), incident.location, incident.description, incident.severity),
        )
        conn.commit()

def list_incidents() -> List[Incident]:
    """Lists all incidents."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM incidents ORDER BY incident_date DESC;")
        rows = cursor.fetchall()
        return [
            Incident(
                id=uuid.UUID(row["id"]),
                employee_id=row["employee_id"],
                incident_date=date.fromisoformat(row["incident_date"]),
                location=row["location"],
                description=row["description"],
                severity=row["severity"],
            )
            for row in rows
        ]

def create_risks_table(conn):
    """Creates the risks table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            area TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            controls TEXT
        );
    """)

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    with get_db_connection() as conn:
        # Manages incidents table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                incident_date TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            );
        """)
        # Manages risks table
        create_risks_table(conn)
        conn.commit()

def add_risk(risk) -> None:
    """Adds a risk to the database."""
    with get_db_connection() as conn:
        conn.execute(
            """INSERT INTO risks (id, name, description, area, risk_level, controls)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (str(risk.id), risk.name, risk.description, risk.area, risk.risk_level, ", ".join(risk.controls)),
        )
        conn.commit()

def list_risks() -> List:
    """Lists all risks."""
    from models.risk import Risk # Local import to avoid circular dependency if models need db
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM risks ORDER BY area, name;")
        rows = cursor.fetchall()
        risks = []
        for row in rows:
            controls_str = row["controls"] if row["controls"] else ""
            risks.append(
                Risk(
                    id=uuid.UUID(row["id"]),
                    name=row["name"],
                    description=row["description"],
                    area=row["area"],
                    risk_level=row["risk_level"],
                    controls=controls_str.split(", "),
                )
            )
        return risks

# Initialize the database when this module is first imported
init_db()
