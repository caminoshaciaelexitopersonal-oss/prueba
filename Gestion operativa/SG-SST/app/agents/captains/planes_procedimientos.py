from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# --- State Definition for the Plans and Procedures Captain's Subgraph ---
class PlansState(TypedDict):
    command: str
    task_type: Literal["create_pet", "manage_ptar", "unknown"]
    payload: dict
    response: str

# --- Tactical Team Agents (Placeholders) ---
def tactical_create_pet(state: PlansState):
    print("---TACTICAL AGENT: Create PETS---")
    procedure_name = state.get("payload", {}).get("name", "Nuevo Procedimiento de Trabajo Seguro")
    return {"response": f"El procedimiento '{procedure_name}' ha sido creado (simulado)."}

def tactical_manage_ptar(state: PlansState):
    print("---TACTICAL AGENT: Manage PTAR---")
    ptar_id = state.get("payload", {}).get("id", "PTAR-001")
    return {"response": f"El permiso de trabajo de alto riesgo '{ptar_id}' está siendo gestionado (simulado)."}

# --- Captain's Router ---
def route_to_tactical_team(state: PlansState):
    print("---CAPTAIN'S ROUTER: Plans and Procedures---")
    command = state.get("command", "").lower()

    if ("crear" in command or "elabora" in command) and ("procedimiento" in command or "pet" in command or "pets" in command):
        return {"task_type": "create_pet", "payload": {"name": "PETS para Trabajos en Altura"}}
    elif "permiso" in command or "ptar" in command:
        return {"task_type": "manage_ptar", "payload": {"id": "PTAR-2024-105"}}
    else:
        return {"task_type": "unknown", "payload": {}}

# --- Build the Captain's Subgraph ---
workflow = StateGraph(PlansState)

workflow.add_node("captain_router", route_to_tactical_team)
workflow.add_node("create_pet", tactical_create_pet)
workflow.add_node("manage_ptar", tactical_manage_ptar)
workflow.add_node("unknown_task", lambda state: {"response": "No se pudo determinar la tarea de planes o procedimientos."})

workflow.set_entry_point("captain_router")
workflow.add_conditional_edges(
    "captain_router",
    lambda x: x["task_type"],
    {
        "create_pet": "create_pet",
        "manage_ptar": "manage_ptar",
        "unknown": "unknown_task",
    }
)
workflow.add_edge("create_pet", END)
workflow.add_edge("manage_ptar", END)
workflow.add_edge("unknown_task", END)

captain_planes_procedimientos_app = workflow.compile()

print("Subgraph for 'Capitán de Planes y Procedimientos' compiled.")
