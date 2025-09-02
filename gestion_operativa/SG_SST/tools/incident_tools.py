from langchain_core.tools import tool
from datetime import date
from models.incident import Incident
import database
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

def get_severity_suggestion(description: str) -> str:
    """Helper function to get severity suggestion from an LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "AI analysis disabled (no API key)"

    template = """
    Eres un experto en seguridad y salud en el trabajo.
    Analiza la siguiente descripción de un incidente y clasifica su severidad.
    Responde únicamente con una de las siguientes tres opciones: "Baja", "Media", "Alta".
    Descripción: "{description}"
    Severidad:
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo")
    chain = prompt | model | StrOutputParser()
    return chain.invoke({"description": description}).strip()

@tool
def report_incident(employee_id: str, location: str, description: str, incident_date_str: str) -> str:
    """
    Reports a new safety and health incident.
    Args:
        employee_id: The ID of the employee involved.
        location: The location where the incident occurred.
        description: A detailed description of the incident.
        incident_date_str: The date of the incident in YYYY-MM-DD format.
    """
    try:
        incident_date = date.fromisoformat(incident_date_str)

        # Get AI-powered severity suggestion
        severity = get_severity_suggestion(description)

        new_incident = Incident(
            employee_id=employee_id,
            location=location,
            description=description,
            incident_date=incident_date,
            severity=severity
        )
        database.add_incident(new_incident)
        return f"Successfully reported incident with ID {new_incident.id}. AI suggested severity: {severity}."
    except Exception as e:
        return f"Error reporting incident: {e}"

@tool
def list_incidents() -> str:
    """Lists all reported incidents."""
    incidents = database.list_incidents()
    if not incidents:
        return "No incidents found."

    report = "Reported Incidents:\n"
    for inc in incidents:
        report += f"- ID: {inc.id}, Date: {inc.incident_date}, Location: {inc.location}, Severity: {inc.severity}\n"
    return report
