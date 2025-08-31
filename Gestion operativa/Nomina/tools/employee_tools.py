from langchain_core.tools import tool
from datetime import date
from models.employee import Employee
import database

@tool
def add_employee(name: str, position: str, salary: float, start_date_str: str) -> str:
    """
    Adds a new employee to the system.
    Args:
        name: The full name of the employee.
        position: The job position of the employee.
        salary: The monthly salary of the employee.
        start_date_str: The employee's start date in YYYY-MM-DD format.
    """
    try:
        start_date = date.fromisoformat(start_date_str)
        new_employee = Employee(
            name=name,
            position=position,
            salary=salary,
            start_date=start_date,
        )
        database.add_employee(new_employee)
        return f"Successfully added employee {name} with ID {new_employee.id}."
    except Exception as e:
        return f"Error adding employee: {e}"

@tool
def list_employees() -> str:
    """Lists all employees in the system."""
    employees = database.list_employees()
    if not employees:
        return "No employees found."

    report = "Current Employees:\n"
    for emp in employees:
        report += f"- ID: {emp.id}, Name: {emp.name}, Position: {emp.position}\n"
    return report
