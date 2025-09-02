# gestion_operativa/SG-SST/tools/indicator_tools.py
from langchain_core.tools import tool
from typing import List

# Simplified in-memory storage
sgsst_indicators = {}

@tool
def define_sgsst_indicator(name: str, description: str, formula: str, goal: str) -> str:
    """
    Defines a new Key Performance Indicator (KPI) for the OHS management system.

    Args:
        name (str): The name of the indicator (e.g., 'Accident Frequency Rate').
        description (str): A brief description of what the indicator measures.
        formula (str): The mathematical formula used to calculate the indicator.
        goal (str): The target or goal for this indicator (e.g., '< 1.0', '100% compliance').

    Returns:
        str: A confirmation message.
    """
    indicator_id = f"IND-{len(sgsst_indicators) + 1}"
    sgsst_indicators[indicator_id] = {
        "id": indicator_id,
        "name": name,
        "description": description,
        "formula": formula,
        "goal": goal,
        "measurements": []
    }
    return f"Successfully defined new OHS indicator '{name}'."

@tool
def list_sgsst_indicators() -> str:
    """
    Lists all defined OHS management system indicators.

    Returns:
        str: A list of all defined indicators.
    """
    if not sgsst_indicators:
        return "No OHS indicators have been defined yet."

    report = "Defined OHS Indicators:\n"
    for ind_id, ind in sgsst_indicators.items():
        report += f"- ID: {ind_id}, Name: {ind['name']}, Goal: {ind['goal']}\n"
    return report
