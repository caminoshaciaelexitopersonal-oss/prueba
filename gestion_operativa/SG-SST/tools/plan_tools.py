# gestion_operativa/SG-SST/tools/plan_tools.py
from langchain_core.tools import tool
from typing import List, Dict
import datetime

# This is a simplified in-memory storage for plans.
# In a real system, this would use the database.
sgsst_plans = {}

@tool
def create_annual_sgsst_plan(year: int, objectives: List[str], budget: float) -> str:
    """
    Creates the main structure for the Annual Occupational Health and Safety (OHS) Plan.

    Args:
        year (int): The year for which the plan is being created.
        objectives (List[str]): A list of high-level objectives for the OHS plan for the year.
        budget (float): The total budget allocated for the OHS plan.

    Returns:
        str: A confirmation message indicating the plan has been created.
    """
    if year in sgsst_plans:
        return f"Error: An annual plan for the year {year} already exists."

    plan_id = f"PLAN-{year}"
    sgsst_plans[year] = {
        "id": plan_id,
        "year": year,
        "objectives": objectives,
        "budget": budget,
        "activities": [],
        "created_at": datetime.datetime.now().isoformat()
    }
    return f"Successfully created the Annual OHS Plan for {year} with ID {plan_id}."

@tool
def add_activity_to_annual_plan(year: int, activity_name: str, responsible: str, due_date_str: str) -> str:
    """
    Adds a specific activity to an existing Annual OHS Plan.

    Args:
        year (int): The year of the plan to which the activity will be added.
        activity_name (str): The name or description of the activity.
        responsible (str): The person or department responsible for the activity.
        due_date_str (str): The due date for the activity in YYYY-MM-DD format.

    Returns:
        str: A confirmation or error message.
    """
    if year not in sgsst_plans:
        return f"Error: No annual plan found for the year {year}. Please create one first."

    try:
        due_date = datetime.date.fromisoformat(due_date_str)
    except ValueError:
        return "Error: Invalid date format. Please use YYYY-MM-DD."

    activity = {
        "name": activity_name,
        "responsible": responsible,
        "due_date": due_date.isoformat(),
        "status": "Pending"
    }

    sgsst_plans[year]["activities"].append(activity)
    return f"Successfully added activity '{activity_name}' to the {year} OHS plan."
