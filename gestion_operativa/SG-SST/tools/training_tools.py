# gestion_operativa/SG-SST/tools/training_tools.py
from langchain_core.tools import tool
from typing import List, Dict
import datetime

# Simplified in-memory storage
training_records = {}
ppe_records = {}

@tool
def record_sgsst_training(employee_id: str, course_name: str, training_date_str: str, duration_hours: int) -> str:
    """
    Records that an employee has completed an OHS training course.

    Args:
        employee_id (str): The ID of the employee who received the training.
        course_name (str): The name of the training course (e.g., 'First Aid', 'Fire Safety').
        training_date_str (str): The date the training was completed in YYYY-MM-DD format.
        duration_hours (int): The duration of the training in hours.

    Returns:
        str: A confirmation message.
    """
    try:
        training_date = datetime.date.fromisoformat(training_date_str)
    except ValueError:
        return "Error: Invalid date format. Please use YYYY-MM-DD."

    record_id = f"TRAIN-{len(training_records) + 1}"
    training_records[record_id] = {
        "id": record_id,
        "employee_id": employee_id,
        "course": course_name,
        "date": training_date.isoformat(),
        "duration": duration_hours
    }
    return f"Successfully recorded training '{course_name}' for employee {employee_id}."

@tool
def record_ppe_delivery(employee_id: str, ppe_item: str, quantity: int, delivery_date_str: str) -> str:
    """
    Records the delivery of Personal Protective Equipment (PPE) to an employee.

    Args:
        employee_id (str): The ID of the employee who received the PPE.
        ppe_item (str): The name of the PPE item (e.g., 'Safety Helmet', 'Gloves').
        quantity (int): The number of items delivered.
        delivery_date_str (str): The date the PPE was delivered in YYYY-MM-DD format.

    Returns:
        str: A confirmation message.
    """
    try:
        delivery_date = datetime.date.fromisoformat(delivery_date_str)
    except ValueError:
        return "Error: Invalid date format. Please use YYYY-MM-DD."

    record_id = f"PPE-{len(ppe_records) + 1}"
    ppe_records[record_id] = {
        "id": record_id,
        "employee_id": employee_id,
        "item": ppe_item,
        "quantity": quantity,
        "date": delivery_date.isoformat()
    }
    return f"Successfully recorded delivery of {quantity} x {ppe_item} to employee {employee_id}."
