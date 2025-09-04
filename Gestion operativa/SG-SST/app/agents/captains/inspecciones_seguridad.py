from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# --- State Definition for the Captain's Subgraph ---
class InspectionsState(TypedDict):
    # The original command from the user
    command: str
    # The decision on which tactical agent to use
    task_type: Literal["create", "list", "update", "unknown"]
    # The data needed to execute the task
    payload: dict
    # The final response from the tactical agent
    response: str


# --- Tactical Team Agents (Real Implementation) ---
from database import SessionLocal
from models import Inspection

def tactical_create_inspection(state: InspectionsState):
    print("---TACTICAL AGENT: Create Inspection (Real DB Write)---")
    payload = state.get("payload", {})
    area = payload.get("area", "Área no especificada")
    print(f"Payload received: {payload}")

    db = SessionLocal()
    try:
        new_inspection = Inspection(
            area=area,
            # status e inspector_id se pueden añadir aquí si el agente los extrae
        )
        db.add(new_inspection)
        db.commit()
        db.refresh(new_inspection)
        print(f"SUCCESS: New inspection with ID {new_inspection.id} saved to database.")
        return {"response": f"¡Acción permanente! Inspección de seguridad con ID {new_inspection.id} creada para el área '{area}'."}
    except Exception as e:
        print(f"ERROR: Could not write to database. {e}")
        db.rollback()
        return {"response": f"Error al guardar la inspección en la base de datos: {e}"}
    finally:
        db.close()

def tactical_list_inspections(state: InspectionsState):
    print("---TACTICAL AGENT: List Inspections---")
    # In a real implementation, this would query the database.
    return {"response": "Aquí está la lista de todas las inspecciones de seguridad (simulado)."}

# --- Captain's Router ---
# This agent decides which tactical agent to use based on the command.
def route_to_tactical_team(state: InspectionsState):
    print("---CAPTAIN'S ROUTER: Inspections---")
    command = state.get("command", "").lower()

    if "crear" in command or "programar" in command or "nueva" in command:
        # Here, a more advanced agent would parse the command to extract entities
        # like the area, date, etc., and put them in the payload.
        # For now, we'll simulate it.
        area_payload = {"area": "Área Extraída de Comando"}
        return {"task_type": "create", "payload": area_payload}
    elif "listar" in command or "mostrar" in command or "ver todas" in command:
        return {"task_type": "list", "payload": {}}
    else:
        return {"task_type": "unknown", "payload": {}}

# --- Build the Captain's Subgraph ---
workflow = StateGraph(InspectionsState)

# Add nodes
workflow.add_node("captain_router", route_to_tactical_team)
workflow.add_node("create_inspection", tactical_create_inspection)
workflow.add_node("list_inspections", tactical_list_inspections)
workflow.add_node("unknown_task", lambda state: {"response": "No se pudo determinar la tarea de inspección específica."})

# Define edges
workflow.set_entry_point("captain_router")
workflow.add_conditional_edges(
    "captain_router",
    lambda x: x["task_type"],
    {
        "create": "create_inspection",
        "list": "list_inspections",
        "unknown": "unknown_task",
    }
)
workflow.add_edge("create_inspection", END)
workflow.add_edge("list_inspections", END)
workflow.add_edge("unknown_task", END)

# Compile the subgraph
captain_inspections_app = workflow.compile()

print("Subgraph for 'Capitán de Inspecciones de Seguridad' compiled.")
