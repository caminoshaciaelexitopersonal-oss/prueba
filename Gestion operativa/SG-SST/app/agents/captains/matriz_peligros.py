from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# --- State Definition for the Hazard Matrix Captain's Subgraph ---
class HazardMatrixState(TypedDict):
    command: str
    task_type: Literal["create_matrix", "add_risk", "list_risks", "unknown"]
    payload: dict
    response: str

# --- Tactical Team Agents (Placeholders) ---
def tactical_create_matrix(state: HazardMatrixState):
    print("---TACTICAL AGENT: Create Hazard Matrix---")
    matrix_name = state.get("payload", {}).get("name", "Nueva Matriz IPERC")
    return {"response": f"Matriz de peligros '{matrix_name}' ha sido creada (simulado)."}

def tactical_add_risk(state: HazardMatrixState):
    print("---TACTICAL AGENT: Add Risk---")
    risk_desc = state.get("payload", {}).get("description", "Riesgo no especificado")
    return {"response": f"Nuevo riesgo '{risk_desc}' ha sido añadido a la matriz (simulado)."}

# --- Captain's Router ---
def route_to_tactical_team(state: HazardMatrixState):
    print("---CAPTAIN'S ROUTER: Hazard Matrix---")
    command = state.get("command", "").lower()

    if ("crear" in command or "crea" in command) and "matriz" in command:
        return {"task_type": "create_matrix", "payload": {"name": "Matriz IPERC para Taller"}}
    elif ("añadir" in command or "registrar" in command) and "riesgo" in command:
        return {"task_type": "add_risk", "payload": {"description": "Riesgo de caída a distinto nivel"}}
    else:
        return {"task_type": "unknown", "payload": {}}

# --- Build the Captain's Subgraph ---
workflow = StateGraph(HazardMatrixState)

workflow.add_node("captain_router", route_to_tactical_team)
workflow.add_node("create_matrix", tactical_create_matrix)
workflow.add_node("add_risk", tactical_add_risk)
workflow.add_node("unknown_task", lambda state: {"response": "No se pudo determinar la tarea de matriz de peligros."})

workflow.set_entry_point("captain_router")
workflow.add_conditional_edges(
    "captain_router",
    lambda x: x["task_type"],
    {
        "create_matrix": "create_matrix",
        "add_risk": "add_risk",
        "unknown": "unknown_task",
    }
)
workflow.add_edge("create_matrix", END)
workflow.add_edge("add_risk", END)
workflow.add_edge("unknown_task", END)

captain_matriz_peligros_app = workflow.compile()

print("Subgraph for 'Capitán de Matriz de Peligros' compiled.")
