from langchain_core.tools import tool
from typing import List
from models.risk import Risk
import database

@tool
def add_risk(name: str, description: str, area: str, risk_level: str, controls: List[str]) -> str:
    """
    Adds a new risk to the system's risk matrix.
    Args:
        name: A short name for the risk (e.g., "Chemical Spill").
        description: A detailed description of the risk.
        area: The area or department where the risk is present (e.g., "Warehouse").
        risk_level: The assessed level of the risk (e.g., "Bajo", "Medio", "Alto").
        controls: A list of control measures implemented for this risk.
    """
    try:
        new_risk = Risk(
            name=name,
            description=description,
            area=area,
            risk_level=risk_level,
            controls=controls,
        )
        database.add_risk(new_risk)
        return f"Successfully added risk '{name}' to the matrix."
    except Exception as e:
        return f"Error adding risk: {e}"

@tool
def list_risks() -> str:
    """Lists all identified risks in the system."""
    risks = database.list_risks()
    if not risks:
        return "No risks have been identified yet."

    report = "Identified Risks Matrix:\n"
    for risk in risks:
        report += f"- Area: {risk.area}, Risk: {risk.name}, Level: {risk.risk_level}\n"
    return report
